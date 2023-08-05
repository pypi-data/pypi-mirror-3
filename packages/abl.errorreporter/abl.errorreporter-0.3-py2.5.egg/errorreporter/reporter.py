# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

import logging
import os
import tempfile
import time
from textwrap import dedent
import errno

import pkg_resources
from turbomail import Message
from genshi.template import NewTextTemplate as TextTemplate

import formatter
from util.escaping import safe_to_unicode


logger = logging.getLogger(__name__)


class Reporter(object):

    def __init__(self, **conf):
        for name, value in conf.items():
            if not hasattr(self, name):
                raise TypeError(
                    "The keyword argument %s was not expected"
                    % name)
            setattr(self, name, value)
        self.check_params()

    def check_params(self):
        pass

    def format_date(self, exc_data):
        return time.strftime('%c', exc_data.date)


    def format_text(self, exc_data, **kw):
        return formatter.format_text(exc_data, **kw)


class LogReporter(Reporter):

    level = logging.ERROR
    logger = None
    show_hidden_frames = True

    def check_params(self):
        assert self.logger is not None, (
            "You must give a logger instance")

    def report(self, exc_data):
        text = self.format_text(
            exc_data, show_hidden_frames=self.show_hidden_frames)[0]

        self.logger.log(text, self.level)


class StreamReporter(Reporter):

    stream = None
    show_hidden_frames = True
    separator = "\n" + ("*" * 60) + "\n"
    
    def check_params(self):
        assert self.stream is not None, (
            "You must give a file-like object")


    def report(self, exc_data):
        text = self.format_text(
            exc_data, show_hidden_frames=self.show_hidden_frames)[0]
        #print text
        self.stream.write(text)
        if self.separator:
            self.stream.write(self.separator)



class EmailReporter(Reporter):
    """
    This reporter will create an email via TurboMail and
    send it to the configured recipients.

    It is fully configurable through genshi-templates for
    subject-line & body, and a plugin-mechanism to collect data
    to be put in there, as well as defining email-properties
    such as sender, receiver, headers and the like.

    Subject and Body template setup
    -------------------------------

    For both, Genshi NewTextTemplates are used. These get passed
    a dictionary message_data when rendering which is guaranteed to have the
    following keys available:

      - id_code: the exceptions unique stacktrace-fingerprint
      - etype: the type of the exception as string, e.g. "IndexError".
      - edata: the representation of the exception as string, e.g. "IndexError('list index out of range')"
      - last_line: the last sourcecode line, like "File '/path/module.py', line 35 in foo"

    Each passed in plugin can enrich these information when the method ``enrich_message_data``
    is called upon it. It gets passed the exc_data (instance of ExceptionCollector), and
    the message-data so far.

    Message attributes
    ------------------

    When instantiating the turbomail.Message, it get's passed parameters as dictionary
    which is guaranteed to have the following keys:

     - author: sender of the mail.
     - to: the recepient or recipient list.
     - subject: the rendered subject line.
     - headers: a list of headers, which must contain tuples with (name, value).

    Each plugin can enrich and modify this via the method ``enrich_header_data`` which
    gets passed the exc_data (again, instance of ExceptionCollector), and header_data so far.

    Plugins
    -------

    Here the declaration of an EmailReporter plugin:

    class Plugin(object):


        def enrich_header_data(self, exc_data, header_data):
            pass

        def enrich_message_data(self, ext_data, message_data):
            pass

        
    """
    
    author = None
    """
    The sender.
    """
    to = None
    """
    Either a single email, or a list of emails. See TurboMail documentation.
    """
    subject_template = None
    """
    
    """
    body_template = None
    
    plugins = ()
    """
    List of plugins.
    """
    
    SUBJECT_TEMPLATE = "[ERROR] $id_code $etype $edata"
    """
    Default for the subject-line.
    """
    
    BODY_TEMPLATE = dedent("""
    A nasty exception has occured.
    
    Errocode: $id_code

    Last line: $last_line

    Full dump:

    $all_lines
    """)
    """
    Default for the body.
    """

    
    def __init__(self, author, to, plugins=[],
                 subject_template=None,
                 body_template=None):
        if subject_template is None:
            subject_template = self.SUBJECT_TEMPLATE
        if body_template is None:
            body_template = self.BODY_TEMPLATE
        Reporter.__init__(self,
                          author=author,
                          to=to,
                          plugins=plugins,
                          subject_template=subject_template,
                          body_template=body_template,
                          )


    def report(self, exc_data):
        subject, body = self.assemble_email(exc_data)
        header_data = dict(
            author=self.author,
            to=self.to,
            headers=[],
            subject=subject,)
        for plugin in self.plugins:
            plugin.enrich_header_data(exc_data, header_data)
            
        msg = Message(**header_data)
        msg.encoding = "utf-8"
        msg.plain = body
        msg.send()
    

    def check_params(self):
        if not self.to:
            raise ValueError("You must set 'to'")
        if not self.author:
            raise ValueError("You must set 'author'")


    def assemble_email(self, exc_data):
        tf = formatter.TextFormatter()
        all_lines, _ = tf.format_collected_data(exc_data)
        # this is hackish..
        all_lines = safe_to_unicode(all_lines)

        last_frame = exc_data.frames[-1]
        # we need this so that the formatter can
        # guess the proper source encoding.                
        # guess the proper source encoding.
        tf.frame = last_frame
        last_filename = last_frame.filename
        last_line = tf.format_source_line(last_filename or '?', last_frame)
        etype = exc_data.exception_type
        if not isinstance(etype, basestring):
            etype = etype.__name__
        # this is needed so we can handle umlauts in error messages
        if not isinstance(etype, unicode):
            etype = etype.decode('utf-8')
        edata = safe_to_unicode(formatter.truncate(exc_data.exception_value))
        message_data = dict(
            id_code=exc_data.identification_code,
            etype=etype,
            edata=edata,
            last_line=last_line,
            last_filename=last_filename,
            all_lines=all_lines,
            )

        for plugin in self.plugins:
            plugin.enrich_message_data(exc_data, message_data)

        template = TextTemplate(self.subject_template)
        subject = unicode(template.generate(**message_data))

        template = TextTemplate(self.body_template)
        text = unicode(template.generate(**message_data))
        return subject, text




class XMLExceptionDumper(Reporter):
    """
    This reporter dumps XML exception data into a output-directory.
    The exceptions can be grouped into daily changing subdirectories.

    Use this reporter in conjunction with the Ableton Exception Viewer
    to comfortably browse exceptions that occured on one of your systems.

    See

      http://bitbucket.org/deets/ablexceptionviewer/

    for details on that.
    """
    
    outputdir = None
    """
    The destination directory where the created
    XML-files are stored.
    """

    daily_dirs = True
    """
    If True subdirectories with the current date
    are created, to organize the exceptions and to
    prevent file-system issues with to many files
    per directory.
    """
    
    plugins = []
    """
    A list of potential XMLFormatter-plugins.

    See XMLFormatter for details.
    """
    
    dirmode = 0755
    """
    The file-mode for the created output-directories. By
    default, make them world-readable (unix).

    Set to None to prevent this from happening.
    """
    filemode = 0644
    """
    The file-mode for the created XML-files. By default,
    make them world-readable (unix).

    Set to None to prevent this from happening.
    """
    
    
    def check_params(self):
        assert self.outputdir is not None, (
            "You must give a directory to store files")


    def report(self, exc_data):
        text, _ = formatter.format_xml(exc_data, plugins = self.plugins)
        # write it out to a temp file
        self.safe_make_dir(self.outputdir)
        tmp_dir = os.path.join(self.outputdir, '.tmp')
        self.safe_make_dir(tmp_dir)
        tmp_file, tmp_name = tempfile.mkstemp(dir = tmp_dir)
        try:
            os.write(tmp_file, text)
        finally:
            os.close(tmp_file)

        if self.filemode:
            os.chmod(tmp_name, self.filemode)
            
        # and now move it to it's permanent home
        local_name = self.make_filename(exc_data, self.daily_dirs)
        filename = os.path.join(self.outputdir, local_name)
        # first, make sure the directory exists (first exception of the day)
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            self.safe_make_dir(dirname)
        os.rename(tmp_name, filename)
        # for use in the nosetests to generate a link
        return local_name


    def safe_make_dir(self, dirname):
        """Make a directory, but don't die over concurrency conflicts."""
        try:
            os.mkdir(dirname)
            # let others in the same group write here (shared dir for daemons)
            # let anyone read it (www-data for example)
        except OSError, e:
            # suppress raising when the file exists & is a directory
            if e.errno != errno.EEXIST or not os.path.isdir(dirname):
                raise

        if self.dirmode is not None:
            os.chmod(dirname, self.dirmode)


    @classmethod
    def make_filename(self, exc_data, daily_dirs = True):
        """
        Makes a unique filename for the exception based on
        it's unique id and date.

        If dailydirs is True, the date-part is splitted of
        as separate directory, otherwise it's part of
        the filename.
        """
        edate = time.strftime("%Y-%m-%d", exc_data.date)
        etime = time.strftime("%H-%M-%S", exc_data.date)
        ident = exc_data.identification_code

        if daily_dirs:
            name = "%(etime)s_%(ident)s.xml" % locals()            
            return os.path.join(edate, name)
        else:
            return "%(edate)s_%(etime)s_%(ident)s.xml" % locals()


