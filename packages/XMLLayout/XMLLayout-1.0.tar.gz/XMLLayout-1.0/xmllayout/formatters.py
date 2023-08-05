"""logging Formatters"""
import cgi
import logging

__all__ = ['XMLLayout']

# Level names differ slightly in log4j, see
# http://logging.apache.org/log4j/1.2/apidocs/org/apache/log4j/Level.html
LOG4J_LEVEL_MAP = dict(WARNING='WARN', CRITICAL='FATAL')


class XMLLayout(logging.Formatter):

    """Formats log Records as XML according to the `log4j XMLLayout
    <http://logging.apache.org/log4j/docs/api/org/apache/log4j/xml/
    XMLLayout.html>_`
    """

    def format(self, record):
        """Format the log record as XMLLayout XML"""
        levelname = LOG4J_LEVEL_MAP.get(record.levelname, record.levelname)
        event = dict(name=cgi.escape(record.name),
                     threadName=cgi.escape(record.threadName),
                     levelname=cgi.escape(levelname),
                     created=int(record.created * 1000))

        event['message'] = LOG4J_MESSAGE % escape_cdata(record.getMessage())

        # FIXME: Support an NDC somehow
        event['ndc'] = ''
        #ndc = self.get_ndc(record)
        #if ndc:
        #    event['ndc'] = LOG4J_NDC % escape_cdata(ndc)

        event['throwable'] = ''
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
            event['throwable'] = (LOG4J_THROWABLE %
                                  escape_cdata(record.exc_text))

        location_info = dict(pathname=cgi.escape(record.pathname),
                             lineno=record.lineno,
                             module=cgi.escape(record.module), funcName='')
        if hasattr(record, 'funcName'):
            # >= Python 2.5
            location_info['funcName'] = cgi.escape(record.funcName)
        event['locationInfo'] = LOG4J_LOCATIONINFO % location_info

        return LOG4J_EVENT % event


def escape_cdata(cdata):
    """Escape XML CDATA content"""
    return cdata.replace(']]>', ']]>]]&gt;<![CDATA[')

# General logging information
LOG4J_EVENT = """\
<log4j:event logger="%(name)s"
    timestamp="%(created)i"
    level="%(levelname)s"
    thread="%(threadName)s">
%(message)s%(ndc)s%(throwable)s%(locationInfo)s</log4j:event>
"""

# The actual log message
LOG4J_MESSAGE = """\
    <log4j:message><![CDATA[%s]]></log4j:message>
"""

# log4j's 'Nested Diagnostic Context': additional, customizable information
# included with the log record
LOG4J_NDC = """\
    <log4j:ndc><![CDATA[%s]]></log4j:ndc>
"""

# Exception information, if exc_info was included with the record
LOG4J_THROWABLE = """\
    <log4j:throwable><![CDATA[%s]]></log4j:throwable>
"""

# Traceback information
LOG4J_LOCATIONINFO = """\
    <log4j:locationInfo class="%(module)s"
        method="%(funcName)s"
        file="%(pathname)s"
        line="%(lineno)d"/>
"""
