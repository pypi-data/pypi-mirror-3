# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

"""
Formatters for the exception data that comes from ExceptionCollector.

plugins for xmlexceptiondump are defined in setuptool entry points, under the goruping exception_info.   They return a dictionary.  Key is the title of the sections, value is a list, containing one or more dictionaries, which are name-value pairs including the data of that section.  Here is an example:

def get_environ():
    real, virtual = safe_environ_info()
    info = { 'real' : real, 'virtual' : virtual }
    return { 'Environ Info' : [ info ] }
"""


from datetime import datetime
import logging
import sys
import time

from util import escaping
from xml.dom.minidom import getDOMImplementation

try:
    import pkg_resources
except ImportError:
    pkg_resources = None

logger = logging.getLogger(__name__)


def truncate(string, limit=1000):
    """
    Truncate the string to the limit number of
    characters
    """
    if len(string) > limit:
        return string[:limit-20]+'...'+string[-17:]
    else:
        return string



class AbstractFormatter(object):

    general_data_order = ['object', 'source_url']

    def __init__(self, show_hidden_frames=False, include_reusable=True,
                 show_extra_data=True, trim_source_paths=(), **kwargs):
        self.show_hidden_frames = show_hidden_frames
        self.trim_source_paths = trim_source_paths
        self.include_reusable = include_reusable
        self.show_extra_data = show_extra_data
        self.extra_kwargs = kwargs

    def format_collected_data(self, exc_data):
        general_data = {}
        if self.show_extra_data:
            for name, value_list in exc_data.extra_data.items():
                if isinstance(name, tuple):
                    importance, title = name
                else:
                    importance, title = 'normal', name
                for value in value_list:
                    general_data[(importance, name)] = self.format_extra_data(
                        importance, title, value)
        lines = []
        frames = self.filter_frames(exc_data.frames)
        for frame in frames:
            self.frame = frame
            res = self.format_frame_start(frame)
            if res:
                lines.append(res)
            sup = frame.supplement
            if sup:
                if sup.object:
                    general_data[('important', 'object')] = self.format_sup_object(
                        sup.object)
                if sup.source_url:
                    general_data[('important', 'source_url')] = self.format_sup_url(
                        sup.source_url)
                if sup.line:
                    lines.append(self.format_sup_line_pos(sup.line, sup.column))
                if sup.expression:
                    lines.append(self.format_sup_expression(sup.expression))
                if sup.warnings:
                    for warning in sup.warnings:
                        lines.append(self.format_sup_warning(warning))
                if sup.info:
                    lines.extend(self.format_sup_info(sup.info))
            if frame.supplement_exception:
                lines.append('Exception in supplement:')
                lines.append(self.quote_long(frame.supplement_exception))
            if frame.traceback_info:
                lines.append(self.format_traceback_info(frame.traceback_info))
            filename = frame.filename
            if filename and self.trim_source_paths:
                for path, repl in self.trim_source_paths:
                    if filename.startswith(path):
                        filename = repl + filename[len(path):]
                        break
            lines.append(self.format_source_line(filename or '?', frame))
            source = frame.get_source_line()
            long_source = frame.get_source_line(2)
            if source:
                lines.append(self.format_long_source(filename, source,
                                                     long_source))
            res = self.format_frame_end(frame)
            if res:
                lines.append(res)
        etype = exc_data.exception_type
        if not isinstance(etype, basestring):
            etype = etype.__name__
        exc_info = self.format_exception_info(
            etype,
            exc_data.exception_value)
        data_by_importance = {'important': [], 'normal': [],
                              'supplemental': [], 'extra': []}
        for (importance, name), value in general_data.items():
            data_by_importance[importance].append(
                (name, value))
        for value in data_by_importance.values():
            value.sort()
        return self.format_combine(data_by_importance, lines, exc_info)

    def filter_frames(self, frames):
        """
        Removes any frames that should be hidden, according to the
        values of traceback_hide, self.show_hidden_frames, and the
        hidden status of the final frame.
        """
        if self.show_hidden_frames:
            return frames
        new_frames = []
        hidden = False
        for frame in frames:
            hide = frame.traceback_hide
            # @@: It would be nice to signal a warning if an unknown
            # hide string was used, but I'm not sure where to put
            # that warning.
            if hide == 'before':
                new_frames = []
                hidden = False
            elif hide == 'before_and_this':
                new_frames = []
                hidden = False
                continue
            elif hide == 'reset':
                hidden = False
            elif hide == 'reset_and_this':
                hidden = False
                continue
            elif hide == 'after':
                hidden = True
            elif hide == 'after_and_this':
                hidden = True
                continue
            elif hide:
                continue
            elif hidden:
                continue
            new_frames.append(frame)
        if frames[-1] not in new_frames:
            # We must include the last frame; that we don't indicates
            # that the error happened where something was "hidden",
            # so we just have to show everything
            return frames
        return new_frames

    def format_frame_start(self, frame):
        """
        Called before each frame starts; may return None to output no text.
        """
        return None

    def format_frame_end(self, frame):
        """
        Called after each frame ends; may return None to output no text.
        """
        return None

    def pretty_string_repr(self, s):
        """
        Formats the string as a triple-quoted string when it contains
        newlines.
        """
        if '\n' in s:
            s = repr(s)
            s = s[0]*3 + s[1:-1] + s[-1]*3
            s = s.replace('\\n', '\n')
            return s
        else:
            return repr(s)

    def long_item_list(self, lst):
        """
        Returns true if the list contains items that are long, and should
        be more nicely formatted.
        """
        how_many = 0
        for item in lst:
            if len(repr(item)) > 40:
                how_many += 1
                if how_many >= 3:
                    return True
        return False

class TextFormatter(AbstractFormatter):

    def quote(self, s):
        if isinstance(s, str) and hasattr(self, 'frame'):
            s = s.decode(self.frame.source_encoding, 'replace')
        return s.encode('utf-8', 'htmlentityreplace')

    def quote_long(self, s):
        return self.quote(s)

    def emphasize(self, s):
        return s

    def format_sup_object(self, obj):
        return 'In object: %s' % self.emphasize(self.quote(repr(obj)))

    def format_sup_url(self, url):
        return 'URL: %s' % self.quote(url)

    def format_sup_line_pos(self, line, column):
        if column:
            return self.emphasize('Line %i, Column %i' % (line, column))
        else:
            return self.emphasize('Line %i' % line)

    def format_sup_expression(self, expr):
        return self.emphasize('In expression: %s' % self.quote(expr))

    def format_sup_warning(self, warning):
        return 'Warning: %s' % self.quote(warning)

    def format_sup_info(self, info):
        return [self.quote_long(info)]

    def format_source_line(self, filename, frame):
        return 'File %r, line %s in %s' % (
            filename, frame.lineno or '?', frame.name or '?')

    def format_long_source(self, filename, source, long_source):
        return self.format_source(filename, source)

    def format_source(self, filename, source_line):
        return '  ' + self.quote(source_line.strip())

    def format_exception_info(self, etype, evalue):
        return self.emphasize(
            '%s: %s' % (self.quote(etype), self.quote(evalue)))

    def format_traceback_info(self, info):
        return info

    def format_combine(self, data_by_importance, lines, exc_info):
        lines[:0] = [value for n, value in data_by_importance['important']]
        lines.append(exc_info)
        for name in 'normal', 'supplemental', 'extra':
            lines.extend([value for n, value in data_by_importance[name]])
        return self.format_combine_lines(lines), ''

    def format_combine_lines(self, lines):
        return '\n'.join(lines)

    def format_extra_data(self, importance, title, value):
        if isinstance(value, str):
            s = self.pretty_string_repr(value)
            if '\n' in s:
                return '%s:\n%s' % (title, s)
            else:
                return '%s: %s' % (title, s)
        elif isinstance(value, dict):
            lines = ['\n', title, '-'*len(title)]
            items = value.items()
            items.sort()
            for n, v in items:
                try:
                    v = repr(v)
                except Exception, e:
                    v = 'Cannot display: %s' % e
                v = truncate(v)
                lines.append('  %s: %s' % (n, v))
            return '\n'.join(lines)
        elif (isinstance(value, (list, tuple))
              and self.long_item_list(value)):
            parts = [truncate(repr(v)) for v in value]
            return '%s: [\n    %s]' % (
                title, ',\n    '.join(parts))
        else:
            return '%s: %s' % (title, truncate(repr(value)))

    def format_extra_data(self, importance, title, value):
        if isinstance(value, str):
            s = self.pretty_string_repr(value)
            if '\n' in s:
                return '%s:<br><pre>%s</pre>' % (title, self.quote(s))
            else:
                return '%s: <tt>%s</tt>' % (title, self.quote(s))
        elif isinstance(value, dict):
            return self.zebra_table(title, value)
        elif (isinstance(value, (list, tuple))
              and self.long_item_list(value)):
            return '%s: <tt>[<br>\n&nbsp; &nbsp; %s]</tt>' % (
                title, ',<br>&nbsp; &nbsp; '.join(map(self.quote, map(repr, value))))
        else:
            return '%s: <tt>%s</tt>' % (title, self.quote(repr(value)))

    def format_combine(self, data_by_importance, lines, exc_info):
        lines[:0] = [value for n, value in data_by_importance['important']]
        lines.append(exc_info)
        for name in 'normal', 'supplemental':
            lines.extend([value for n, value in data_by_importance[name]])

        extra_data = []
        if data_by_importance['extra']:
            extra_data.extend([value for n, value in data_by_importance['extra']])
        text = self.format_combine_lines(lines)
        ## FIXME: something about this is wrong:
        if self.include_reusable:
            return text, extra_data
        else:
            # Usually because another error is already on this page,
            # and so the js & CSS are unneeded
            return text, extra_data

    def zebra_table(self, title, rows, table_class="variables"):
        if isinstance(rows, dict):
            rows = rows.items()
            rows.sort()
        table = ['<table class="%s">' % table_class,
                 '<tr class="header"><th colspan="2">%s</th></tr>'
                 % self.quote(title)]
        odd = False
        for name, value in rows:
            try:
                value = repr(value)
            except Exception, e:
                value = 'Cannot print: %s' % e
            odd = not odd
            table.append(
                '<tr class="%s"><td>%s</td>'
                % (odd and 'odd' or 'even', self.quote(name)))
            table.append(
                '<td><tt>%s</tt></td></tr>'
                % self.quote(truncate(value)))
        table.append('</table>')
        return '\n'.join(table)





#---------------------------
# for formatting strings.  Not sure if it belongs here, but let's try...

def for_display(obj):
    """
    This is a method to format the object for xml output.
    Right now, a placeholder, but we can do more later...
    """
    try:
        # this raises an error with some sqlalchemy objects, which
        # try to perform a db call
        result = repr(obj)
    except:
        try:
            result = str(obj)
        except:
            result = "Opaque object: " + str(type(obj))
    if not isinstance(result, unicode):
        result = escaping.safe_to_unicode(result)
    return result



class XMLFormatter(AbstractFormatter):

    def __init__(self, **kwargs):
        super(XMLFormatter, self).__init__(**kwargs)
        self.plugins = kwargs.get('plugins', [])


    def format_collected_data(self, exc_data):
        impl = getDOMImplementation()
        newdoc = impl.createDocument(None, "traceback", None)
        top_element = newdoc.documentElement

        sysinfo = newdoc.createElement('sysinfo')
        language = self.create_text_node(newdoc, 'language', 'Python')
        language.attributes['version'] = sys.version.split(' ')[0]
        language.attributes['full_version'] = sys.version
        language.attributes['platform'] = sys.platform
        sysinfo.appendChild(language)

        top_element.appendChild(sysinfo)

        frames = self.filter_frames(exc_data.frames)
        stack = newdoc.createElement('stack')
        top_element.appendChild(stack)
        url = '(Not Available)'
        variable_hash = {}
        for frame in frames:
            xml_frame = newdoc.createElement('frame')
            stack.appendChild(xml_frame)

            filename = frame.filename
            if filename and self.trim_source_paths:
                for path, repl in self.trim_source_paths:
                    if filename.startswith(path):
                        filename = repl + filename[len(path):]
                        break
            self.format_source_line(filename or '?', frame, newdoc, xml_frame)

            source = frame.get_source_line()
            long_source = frame.get_source_line(2)
            if source:
                self.format_long_source(filename,
                    source.decode(frame.source_encoding, 'replace'),
                    long_source.decode(frame.source_encoding, 'replace'),
                    newdoc, xml_frame)

            # find the url for later
            if frame.supplement:
                if frame.supplement.source_url:
                    url = frame.supplement.source_url

            # Only store each variable once (eg. environment)
            # for speed and space performance reasons.
            variables = newdoc.createElement('variables')
            xml_frame.appendChild(variables)
            # this works around some weird error with Genshi call stacks
            if hasattr(frame.locals, "iteritems"):
                for name, value in frame.locals.iteritems():
                    if isinstance(value, unicode):
                        value = value.encode('ascii', 'xmlcharrefreplace')
                    variable = newdoc.createElement('variable')
                    variable.appendChild(self.create_text_node(newdoc, 'name', name))
                    # store the variable in a global hash the first time
                    var_id = str(id(value))
                    if not variable_hash.has_key(var_id):
                        variable_hash[var_id] = for_display(value)
                    variable.appendChild(self.create_text_node(newdoc, 'value', var_id))
                    variables.appendChild(variable)

        url_node = self.create_text_node(newdoc, 'url_error', for_display(url))
        top_element.appendChild(url_node)

        # first, add any "extra data" from the plugins
        for plug in self.plugins:
            # we can't trust the plugins, so let's catch all exceptions
            try:
                data = plug()
                exc_data.extra_data.update(data)
            except Exception, e:
                logger.error('Plugin %s raised error: %s' % \
                    (plug.__name__, str(e)))

        # get the "extra data" like cgi and wsgi parameters
        extra = newdoc.createElement("extra_data")
        for name, value_list in exc_data.extra_data.iteritems():
            if isinstance(name, tuple):
                _, name = name
            datum = self.create_text_node(newdoc, 'extra_datum', name)

            for value in value_list:
                assert isinstance(value, (dict, list))
                if isinstance(value, list):
                    value = dict((str(key), v) for key, v in enumerate(value))
                for k, v in value.items():
                    content = newdoc.createElement('content')
                    # the keys are always simple strings
                    content.appendChild(self.create_text_node(newdoc, 'name', k))
                    content.appendChild(
                        self.create_text_node(newdoc, 'value', for_display(v)))
                    datum.appendChild(content)
            extra.appendChild(datum)
        top_element.appendChild(extra)

        id_lookup = newdoc.createElement("id_lookup")
        for var_id, value in variable_hash.iteritems():
            content = newdoc.createElement('content')
            content.appendChild(self.create_text_node(newdoc, 'name', var_id))
            content.appendChild(self.create_text_node(newdoc, 'value', value))
            id_lookup.appendChild(content)
        top_element.appendChild(id_lookup)

        top_element.appendChild(self.format_exception_info(
            exc_data, newdoc, frame))
        return newdoc.toxml(encoding='utf-8'), ''



    def format_source_line(self, filename, frame, newdoc, xml_frame):
        name = frame.name or '?'
        xml_frame.appendChild(self.create_text_node(newdoc, 'module', frame.modname or '?'))
        xml_frame.appendChild(self.create_text_node(newdoc, 'filename', filename))
        xml_frame.appendChild(self.create_text_node(newdoc, 'line', str(frame.lineno) or '?'))
        xml_frame.appendChild(self.create_text_node(newdoc, 'function', name))

    def format_long_source(self, filename, source, long_source, newdoc, xml_frame):
        source = source.encode('ascii', 'xmlcharrefreplace')
        long_source = long_source.encode('ascii', 'xmlcharrefreplace')
        xml_frame.appendChild(self.create_text_node(newdoc, 'operation', source.strip()))
        xml_frame.appendChild(self.create_text_node(newdoc, 'operation_context', long_source))

    def format_exception_info(self, exc_data, newdoc, frame):
        evalue = exc_data.exception_value
        etype = exc_data.exception_type
        ident = exc_data.identification_code
        timestamp = time.strftime('%Y-%m-%d %H-%M-%S', exc_data.date)

        if not isinstance(etype, basestring):
            etype = etype.__name__

        exception = newdoc.createElement('exception')
        evalue = evalue.decode(
            frame.source_encoding, 'replace').encode('ascii',
                                                     'xmlcharrefreplace')
        exception.appendChild(self.create_text_node(newdoc, 'type', etype))
        exception.appendChild(self.create_text_node(newdoc, 'value', evalue))
        exception.appendChild(self.create_text_node(newdoc, 'timestamp', timestamp))
        exception.appendChild(self.create_text_node(newdoc, 'ident', ident))
        return exception

    def format_source_line(self, filename, frame, newdoc, xml_frame):
        name = frame.name or '?'
        xml_frame.appendChild(self.create_text_node(newdoc, 'module', frame.modname or '?'))
        xml_frame.appendChild(self.create_text_node(newdoc, 'filename', filename))
        xml_frame.appendChild(self.create_text_node(newdoc, 'line', str(frame.lineno) or '?'))
        xml_frame.appendChild(self.create_text_node(newdoc, 'function', name))

    def format_long_source(self, filename, source, long_source, newdoc, xml_frame):
        source = source.encode('ascii', 'xmlcharrefreplace')
        long_source = long_source.encode('ascii', 'xmlcharrefreplace')
        xml_frame.appendChild(self.create_text_node(newdoc, 'operation', source.strip()))
        xml_frame.appendChild(self.create_text_node(newdoc, 'operation_context', long_source))

    def format_exception_info(self, exc_data, newdoc, frame):
        evalue = exc_data.exception_value
        etype = exc_data.exception_type
        ident = exc_data.identification_code
        timestamp = time.strftime('%Y-%m-%d %H-%M-%S', exc_data.date)

        if not isinstance(etype, basestring):
            etype = etype.__name__

        exception = newdoc.createElement('exception')
        evalue = evalue.decode(
            frame.source_encoding, 'replace').encode('ascii',
                                                     'xmlcharrefreplace')
        exception.appendChild(self.create_text_node(newdoc, 'type', etype))
        exception.appendChild(self.create_text_node(newdoc, 'value', evalue))
        exception.appendChild(self.create_text_node(newdoc, 'timestamp', timestamp))
        exception.appendChild(self.create_text_node(newdoc, 'ident', ident))
        return exception


    def create_text_node(self, doc, elem, text):
        if not isinstance(text, basestring):
            try:
                text = escaping.removeIllegalChars(repr(text))
            except:
                text = 'UNABLE TO GET TEXT REPRESENTATION'
        new_elem = doc.createElement(elem)
        new_elem.appendChild(doc.createTextNode(text))
        return new_elem



def get_dependencies(circ_check, lib, working_set):
    libs = {}
    for proj in working_set.by_key[lib].requires():
        if proj.key in circ_check:
            continue
        circ_check[proj.key] = True
        libs[proj.key] = working_set.by_key[proj.key].version
        libs.update(get_dependencies(circ_check, proj.key, working_set))
    return libs


def get_libraries(libs=None):
    """Return a dict of the desired libraries and their version if
    active in the environment"""
    if pkg_resources and libs:
        libraries = {}
        working_set = pkg_resources.working_set
        for lib in libs:
            # Put libs we've either check dependencies on, or are in progress
            # of checking here, to avoid circular references going forever
            circ_check = {}
            if lib in working_set.by_key:
                if lib in circ_check:
                    continue
                circ_check[lib] = True
                libraries[lib] = working_set.by_key[lib].version
                libraries.update(
                    get_dependencies(circ_check, lib, working_set))
        return libraries
    else:
        return {}


def format_text(exc_data, **ops):
    return TextFormatter(**ops).format_collected_data(exc_data)


def format_xml(exc_data, **ops):
    return XMLFormatter(**ops).format_collected_data(exc_data)

