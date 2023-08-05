# -*- coding: utf-8 -*-
from __future__ import with_statement

import sys
import os
import glob
import uuid
import subprocess
import tempfile
import datetime
import shutil
import logging
from functools import partial
from unittest import TestCase
from cStringIO import StringIO

from xml.etree.ElementTree import fromstring

import turbomail
from errorreporter.collector import collect_exception
from errorreporter.formatter import format_xml
from errorreporter.reporter import (
    EmailReporter,
    XMLExceptionDumper,
    StreamReporter,
    LogReporter,
    )


class ExcSerTests(TestCase):


    UMLAUT_TEXT = u"Here we go, with some nasty umlauts: öäß!"

    JAPANESE_TEXT = u"ぜひご覧いただき"
    
    def nice_exception(self, encoding=None, message=None):

        def foo(level):
            local_variable = level
            if level == 0:
                if message is None:
                    m = self.UMLAUT_TEXT
                else:
                    m = message
                if encoding is not None:
                    m = m.encode(encoding)
                raise Exception(m)
            foo(level-1)

        def bar(level=10):
            a = 100
            b = "a string"
            c = dict(key="value")
            foo(level)

        bar()
            


    def get_exception_info(self, callable_):
        try:
            callable_()
            assert False, "Your callable didn't produce an exception!"
        except:
            return sys.exc_info()



    def print_linted_xml(self, xml):
        xmlfile = tempfile.mktemp()
        with open(xmlfile, "w") as outf:
            outf.write(xml)
            
        p = subprocess.Popen(["xmllint", "--format", xmlfile],
                             stdout=subprocess.PIPE)

        print p.stdout.read()
        
        
    def test_collection(self):
        ei = self.get_exception_info(self.nice_exception)
        h = collect_exception(*ei)
        assert len(h.frames) == 14

        # limiting works as advertised
        h = collect_exception(limit=5, *ei)
        assert len(h.frames) == 5
        


    def test_xml_formatting(self):
        ei = self.get_exception_info(self.nice_exception)
        h = collect_exception(*ei)
        s, _ = format_xml(h)
        # this must be valid XML
        assert isinstance(s, str)
        doc = fromstring(s)

        # now test that plugins are called

        testvalue = uuid.uuid4().hex
        def myplugin():
            return dict(key=[dict(testvalue=testvalue)])
        
        s, _ = format_xml(h, plugins=[myplugin])

        #self.print_linted_xml(s)
        


    def test_email_reporting(self):
        turbomail.interface.start({
            "mail.on" : True,
            "provider" : "debug",
            #"mail.transport" : "smtp",
            #"mail.smtp.server" : "mail.ableton.net",
            })
            
        conf = {
            "author" : "dir@ableton.com",
            "to" : "dir@ableton.com",
            }
        reporter = EmailReporter(**conf)
        ei = self.get_exception_info(self.nice_exception)
        h = collect_exception(*ei)
        reporter.report(h)
        mails = turbomail.interface.manager.transport.get_sent_mails()
        assert mails
        mail = mails[0]
        
        conf["subject_template"] = "$edata $subject_field"

        subject_field = uuid.uuid4().hex
        test_header = uuid.uuid4().hex
        
        class TestPlugin(object):

            def enrich_message_data(self, _, subject_data):
                subject_data["subject_field"] = subject_field


            def enrich_header_data(self, _, header_data):
                header_data["headers"].append(("TestHeader", test_header))



        turbomail.interface.manager.transport._sent_mails = []
        
        reporter = EmailReporter(plugins=[TestPlugin()], **conf)
        reporter.report(h)
        
        mails = turbomail.interface.manager.transport.get_sent_mails()
        assert mails
        mail = mails[0]
        assert subject_field in mail
        assert test_header in mail

        # now some encoding fun
        
        ei = self.get_exception_info(partial(self.nice_exception, encoding="utf-8"))
        h = collect_exception(*ei)
        reporter.report(h)

        ei = self.get_exception_info(partial(self.nice_exception, encoding="latin1"))
        h = collect_exception(*ei)
        reporter.report(h)

        ei = self.get_exception_info(partial(self.nice_exception,
                                             encoding="utf-8",
                                             message=self.JAPANESE_TEXT))
        h = collect_exception(*ei)
        reporter.report(h)

        ei = self.get_exception_info(partial(self.nice_exception,
                                             encoding="shift-jis",
                                             message=self.JAPANESE_TEXT))
        h = collect_exception(*ei)
        reporter.report(h)

        


    def test_xml_reporting(self):
        outputdir = tempfile.mkdtemp()
        dumper = XMLExceptionDumper(outputdir=outputdir,
                                    daily_dirs=True)

        ei = self.get_exception_info(self.nice_exception)
        h = collect_exception(*ei)
        dumper.report(h)

        def latest_exception_file():
            # we created a daily-dir inside the outputdir. Locate that
            dname = glob.glob(os.path.join(outputdir, "%i-*" % datetime.date.today().year))[0]
            assert len(os.listdir(dname)) == 1
            exception_filename = os.path.join(dname, os.listdir(dname)[0])
            return exception_filename

        def cleanup():
            shutil.rmtree(outputdir)
            os.mkdir(outputdir)

        exception_filename = latest_exception_file()
        # assert that we really gave birth to something
        # xml-ly
        content = open(exception_filename).read()
        fromstring(content)

        cleanup()

        # now test with plugins

        testvalue = uuid.uuid4().hex

        def myplugin():
            return dict(key=[dict(testvalue=testvalue)])

        dumper = XMLExceptionDumper(outputdir=outputdir,
                                    daily_dirs=True,
                                    plugins=[myplugin])

        dumper.report(h)
        exception_filename = latest_exception_file()
        content = open(exception_filename).read()
        assert testvalue in content

        # and now again for some encoding-fun!
        ei = self.get_exception_info(partial(self.nice_exception, encoding="utf-8"))
        h = collect_exception(*ei)
        dumper.report(h)

        ei = self.get_exception_info(partial(self.nice_exception, encoding="latin1"))
        h = collect_exception(*ei)
        dumper.report(h)

        ei = self.get_exception_info(partial(self.nice_exception,
                                             encoding="utf-8",
                                             message=self.JAPANESE_TEXT))
        h = collect_exception(*ei)
        dumper.report(h)

        ei = self.get_exception_info(partial(self.nice_exception,
                                             encoding="shift-jis",
                                             message=self.JAPANESE_TEXT))
        h = collect_exception(*ei)
        dumper.report(h)

        
        
        
        # and now last but not least, see how dumping without daily dirs works.
        cleanup()
        dumper = XMLExceptionDumper(outputdir=outputdir,
                                    daily_dirs=False)
        dumper.report(h)
        # this must now be a file!
        ename = glob.glob(os.path.join(outputdir, "%i-*" % datetime.date.today().year))[0]
        assert os.path.isfile(ename)
        content = open(ename).read()
        fromstring(content)
        
        
        
    def test_some_reporters(self):
        ei = self.get_exception_info(self.nice_exception)
        h = collect_exception(*ei)

        separator = "foobarbaz"
        stream = StringIO()
        
        sr = StreamReporter(stream=stream, separator=separator)
        sr.report(h)
        v = stream.getvalue()
        assert separator in v


        class FakeLogger(object):

            message = level = None
            
            def log(self, message, level):
                self.message = message
                self.level = level


        logger = FakeLogger()
        lr = LogReporter(logger=logger)
        lr.report(h)

        assert logger.message is not None
        assert logger.level is not None
        
        
        
