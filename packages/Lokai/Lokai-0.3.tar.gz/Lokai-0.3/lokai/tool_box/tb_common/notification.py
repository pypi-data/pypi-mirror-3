# Name:      lokai/tool_box/tb_common/notification.py
# Purpose:   Provide tools for logging and notification
# Copyright: 2011: Database Associates Ltd.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
#    See the License for the specific language governing permissions and
#    limitations under the License.

#-----------------------------------------------------------------------

"""

This module makes use of the Python logging module to provide flexible
ways of logging messages to streams or files, and of notifying same by
email.

The advantage of using the Python module is that it gives a consistent
process for handling such things and makes it relatively
straightforward to re-direct output according to the needs of the
moment.

Much of the content of this module is this documentation. The
facilities needed generally exist within the language logging module
and the particular applications need to use appropriate patterns to
achieve the desired results.

Error Handling
--------------

Applications should trap and handle errors in the usual way. As a
matter of principle, the application should attempt to handle errors
reasonably, but this is not always possible. Here we are talking about
errors that need to be reported.

Generally, all applications should have a high level trap to catch
*all* exceptions so that loggging can happen.

Long-running, deamon-like, applications will log each error as it
happens and then try to carry on in some sensible way.

Once-off applications that are expected to terminate on unhandlable
errors will trap errors at a suitable high level, log the error, and
then call the exit function with a non-zero argument. Since the exit
function itself raises a SystemExit error it is important that this is
not trapped at a higher level.

Adding Extra Information
------------------------

A logger generally takes the message it is given and then wraps it up
with additional information, such as the time when the message was
generated. If you need to provide the reader with context specific
information, such as the data that was being processed at the time,
you generally need to include this in the message text before passing
it to the logger.

Alternatively, when you call a logging function such as info, warn or
debug, you can pass a keyword argument that contains the context
reltated data in a dictionary. For this to be useful you have to
provide a formating string that actually invokes the items in the
dictionary.

Since emails might be expected to have different layout requirements
than files it is generally better to use the extra data dictionary and
allow the logging code to handle the differences.

The disadvantage of providing a specialised format string is that the
extra data dictionary must provide all of the required data
fields. This disadvantage is overcome in the formatter extensions in
this file, where the content of the output reflects only the data that
is provided.

Since the fields supported are application dependent, each application
must define its own field set. See the Formatter definitions below.

Dynamic logging parameters
--------------------------

Much of the information used by the standard library to manage logging
is set up when a logger is initialised. This is fine for single-shot
programs that process something and then exit, but it may be less fine
for programs where the data itself provides some of the information
needed, or for long-running deamons where logging may need parameters
relating to the current request.

To handle this we have a number of tools:

  The RecordingLoggger has a facility to execute a given function on
  all of the handlers in a logger. This is taken from the standard
  flush mechanism, where applying flush to a logger has the effect of
  aplying flush to all of the attached handlers. In our case we
  generalise it to look for a specified method name. If that method
  exists for the handler then it is executed with the given arguments.

  The BulkHandler provides getAttributes and setAttributes that can be
  called by this mechanism. These methods handle a fixed set of
  attributes that apply to the formatter, or the target handler, as
  appropriate. Calling::
  
    notify.getLogger().execute_all('setAttributes', kwargs)

  has the effect of updating those attributes in the underlying
  structure.

  Some of these attibutes are dealt with in methods in this module.
  See the setAttributes method for BulkHandler. Others may be handled
  by application specific code.
  
Logging to more than one destination
------------------------------------

The Python logging facility allows multiple handlers to be attached to
a logger. Each handler can have its own characteristics and a message
will be processed into each of the outputs according to those
characteristics. In particular, each handler can have a different
format, allowing email and file formats to be different for the same
message.

Chosing a particular destination
--------------------------------

System administrators need to see: information about how the program
is running; warning messages; error messages; and all the messages for
users and developers.

Users need to see information about what the program achieved and any
warning or error messages that arise directly from user input or
configuration.

Developers need to see debug messages.

This is achieved by using the hierarchical logger name capability of
the Python module.

All programs will use a standard set of logger names for the various
destinations. A root logger for adminstrators, a client logger for
users and a debug logger for developers. Other logger names may be
used for specific purposes, as required.

Logger Names
------------

The root logger should be given a name that reflects the application
itself. This creates a problem for utility routines in that they do
not know the name of the application.

We get round this by providing two functions setLogName and
getLogName. These refer to a global name that can be shared across
libraries.

Standardised names
------------------

There is one standardised default name that is used by lower level
code to report debug messages. This name is returned by the function
getDebugName given below. Other names can be easily created using the
same function

Switching debug on and off
--------------------------

The logging facilities provide for the setting of a logging
level. This means that code would unconditionally make calls to
self.logger.debug(...) in all the usual places. The message would then
appear or not depending on the logging level.

Individual modules may, of course, support their own verbosity
settings as a refinement. In which case additional tests would be
required within the code.

"""
#
#-----------------------------------------------------------------------
#
import logging
import logging.handlers

#-----------------------------------------------------------------------

MONITOR = 15

logging.addLevelName(MONITOR, 'MONITOR')

my_root_log_name = ''

def setLogName(target):
    global my_root_log_name
    my_root_log_name = target

def getLogName():
    global my_root_log_name
    return my_root_log_name

def getDebugName(name='debug'):
    return "%s.%s" % (getLogName(), name)

def getLogger():
    return logging.getLogger(getLogName())

#-----------------------------------------------------------------------
# A logger class that records statistics about severity. Use this one
# by default.

class RecordingLogger(logging.Logger):

    def __init__(self, name, level=logging.NOTSET):
        logging.Logger.__init__(self, name=name, level=level)
        self._set_stats()
        self.propagate = 0

    def _set_stats(self):
        self.stats = {'CRITICAL': 0,
                      'ERROR': 0,
                      'WARNING': 0,
                      'INFO': 0,
                      'MONITOR': 0,
                      'DEBUG': 0}

    def _log(self, level, msg, args, exc_info=None, extra=None):
        self.stats[logging.getLevelName(level)] += 1
        logging.Logger._log(self, level=level, msg=msg, args=args,
                            exc_info=exc_info, extra=extra)

    def flush(self):
        self.execute_all('flush')
        self._set_stats()

    def execute(self, function, *args, **kwargs):
        """ Apply this function to all the handlers for this
            logger. Ignore if the handler does not support the
            function.

            This supports return values by yielding the answer at each
            level.
        """
        c = self
        while c:
            for hdlr in c.handlers:
                if hasattr(hdlr, function):
                    target = getattr(hdlr, function)
                    if callable(target):
                        yield target(*args, **kwargs)
            if not c.propagate:
                c = None    #break out
            else:
                c = c.parent

    def execute_all(self, function, *args, **kwargs):
        """ call execute in a loop and throw away any responses.
        """
        for resp in self.execute(function, *args, **kwargs):
            pass

    def execute_one(self, function, *args, **kwargs):
        """ call execute once and return the response.
        """
        for resp in self.execute(function, *args, **kwargs):
            return resp
        return None
    
logging.setLoggerClass(RecordingLogger)
    
#-----------------------------------------------------------------------
# SMTP specials

class checkingSMTPHandler(logging.handlers.SMTPHandler):
    """ Send email to target addresses. Quietly ignore the emit
        command if there are no target addresses.

        This handler supports some dynamically updatable attributes.

        :subject: The text for the email subject line.

        :toaddrs: Override the logging.handlers.SMTPHandler attribute
            that is normally set when the handler is instantiated.

        :temp_toaddrs: A list of to addresses that will temporarily
            override self.toaddrs. The list will be emptied at the
            next flush.
        
    """
    def __init__(self, *args):
        logging.handlers.SMTPHandler.__init__(self, *args)

    def setAttributes(self, *args, **kwargs):
        if 'subject' in kwargs:
            self.subject = kwargs['subject']
        if 'temp_toaddrs' in kwargs:
            self.temp_toaddrs = kwargs['temp_toaddrs']

    def getSubject(self, record):
        #
        # subject of email uses defined subject plus the raw message
        op = self.subject
        return op

    def emit(self, record):
        #
        # Check that to_address exists.
        #
        # Default to_address is the from address.
        save_toaddrs = self.toaddrs
        try:
            self.toaddrs = self.temp_toaddrs
            del self.temp_toaddrs
        except AttributeError:
            pass
        try:
            if len(self.toaddrs) == 0 :
                if self.fromaddr :
                    self.toaddrs = [self.fromaddr]
                else:
                    #
                    # LEAVE QUIETLY
                    return
            logging.handlers.SMTPHandler.emit(self, record)
        finally:
            self.toaddrs = save_toaddrs

#-----------------------------------------------------------------------

class BulkHandler(logging.handlers.BufferingHandler):
    """ A basic buffering message handler that stores all emits until
        such a time as the .flush() or .close() is explicitely called.

        The buffered messages are formatted into a full message on
        flush. The structure and content of the full message are
        controlled by the formatter attached to this handler. See
        below.

        The full message is passed to a target handler that passes the
        full message to the output channel.

        This handler provides a setAttributes method that allows
        useful meta data to be passed to the target handler and to the
        formatter. This means that the information can be updated
        dynamically using 'execute' on the RecordingLogger to call
        setAttributes
    """
    def __init__(self,
                 target=None,
                 formatter=None,
                 capacity=-1,
                 **kwargs):
        """ Initialise this handler:

            target = Handler to output the completed buffered message
                when 'flush' is called. Can also use setTarget. It is
                generally appropriate to initialise this target
                handler with a nullFormatter.

                There is no default value.
            
            formatter = Formatter used to lay out the full
                message. Can be set with setFormatter. The message
                formater should be initialised with a line formatter
                to apply to each accumulated log record.

                The default is BulkFormatter using the loging default
                line format.

            capacity = The number of records to store before
                auto-flush. Set this to -1 to disable autoflush.
                The default is -1.
        """
        logging.handlers.BufferingHandler.__init__(self, capacity)
        if target:
            self.setTarget(target)
        if formatter:
            self.setFormatter(formatter)
        else:
            # We default to a BulkFormatter with facility for a header
            # and footer and a default line formatter.
            self.setFormatter(BulkFormatter())

        if kwargs.get('logname', None):
            # Add a filter so only messages to the named log get mailed
            self.addFilter(logging.Filter(kwargs.get('logname', None)))
        if kwargs.get('level', None):
            # Set the Level for filtering
            self.setLevel(kwargs.get('level', None))
        
    def setTarget(self, target):
        """ Set the target handler for this handler.
        """
        self.target = target
        
    def setFormatter(self, formatter):
        """ Set the formatter for this handler.
        """
        self.formatter = formatter
        
    def shouldFlush(self, record):
        """
        Should the handler flush its buffer?

        Returns true if the buffer is up to capacity.

        Return False always if capacity is -ve
        
        """
        return self.capacity >= 0 and (len(self.buffer) >= self.capacity)

    def emit(self, record):
        """ Emit a record by  appending it to an interal buffer.

            If the record happens to be a list, break out the contents
            of the list and append them individually.
        """
        if isinstance(record, type([])):
            for rr in record:
                logging.handlers.BufferingHandler.emit(self, rr)
        else:
            logging.handlers.BufferingHandler.emit(self, record)


    def flush(self):
        # Note that self.close() will call this.
        if len(self.buffer) > 0:
            # We only send if the buffer has been added to
            # Compile the stack as a string message and emit the smtp base
            message = logging.LogRecord('', 0, '', 0,
                                        self.format(self.buffer),
                                        None, None)
            self.target.emit(message)
            self.buffer = []

    def getAttributes(self):
        """ Return a dictionary of settable attributes and current
            values.

            This is derived from a set of things that we choose to
            display to the caller. There is no guarantee that the
            attributes will have any effect, as we don't have full
            control over the formatter and target handler objects.
        """
        op = {}
        if self.formatter:
            try:
                op['header'] = self.formatter.header
            except AttributeError:
                pass
            try:
                op['footer'] = self.formatter.footer
            except AttributeError:
                pass
        if self.target:
            try:
                op['subject'] = self.target.subject
            except AttributeError:
                pass
            try:
                op['toaddrs'] = self.target.toaddrs
            except AttributeError:
                pass
            try:
                op['temp_toaddrs'] = self.target.temp_toaddrs
            except AttributeError:
                pass
            
        return op

    def execute(self, function, *args, **kwargs):
        """ Apply this function to the underlying hander and to the
            underlying formatter and handler
        """
        for c in (self.formatter, self.target):
            if c and hasattr(c, function):
                target = getattr(c, function)
                if callable(target):
                    yield target(*args, **kwargs)

    def execute_all(self, function, *args, **kwargs):
        """ call execute in a loop and throw away any responses.
        """
        for resp in self.execute(function, *args, **kwargs):
            pass

    def setAttributes(self, *args, **kwargs):
        """ Set the appropriate attribute values for this handler
            _and_ the target handler.

            Pick and choose from the attribute list, ignoring values
            that we don't want.

            The values may be posted into the fomatter
        """
        # No settable attributes at this level, so go down to target
        # handler and formatter
        self.execute_all('setAttributes', *args, **kwargs)

#-----------------------------------------------------------------------

class UnicodeToStrFormatter(logging.Formatter):
    """ Do the same thing as the logging base Formater, except that
        strings are encode to ascii, primarily for use by email.

        This is done to the resulting formatted string, so all the
        capabilities of Formatter are retained.
    """

    def format(self, record):
        op = logging.Formatter.format(self, record)
        return op.encode('ascii', 'backslashreplace')

#-----------------------------------------------------------------------
    
class BulkFormatter(logging.BufferingFormatter):
    
    def __init__(self, linefmt=None, **kwargs):
        """ Initialise this formatter:
        
            linefmt = Formatter to apply to each log message as it is
                posted into the full message.

                This defaults to the logging Formatter using
                BASIC_FORMAT.
        """
        logging.BufferingFormatter.__init__(self, linefmt)

    def setAttributes(self, **kwargs):
        if 'header' in kwargs:
            self.header = kwargs['header']
        if 'footer' in kwargs:
            self.footer = kwargs['footer']
        
    def formatHeader(self, records):
        """ Return the header string for the specified records."""
        try:
            return self.header
        except AttributeError:
            return ''

    def formatFooter(self, records):
        """ Return the footer string for the specified records."""
        try:
            return self.footer
        except AttributeError:
            return ''

#-----------------------------------------------------------------------

class nullFormatter(logging.Formatter):
    """ A formatter that simply returns the given message.

        This is intended for use by whatever target handler is set in
        the BulkHandler. We assume that the Bulk Handler as done all
        the formatting work that might be necessary.
    """

    def __init__(self):
        logging.Formatter.__init__(self)

    def format(self, record):
        return record.getMessage()

#-----------------------------------------------------------------------

class FilterMax(object):
    """ Filter that sets a max level instead of a minimum level

        Normal filtering is level >= given level, so this one must be
        level < given level
    """
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        if record.levelno < self.level:
            return 1
        return 0

#-----------------------------------------------------------------------

# Logging calls that log to default places

def critical(msg, *args, **kwargs):
    logging.getLogger(getLogName()).critical(msg, *args, **kwargs)

fatal = critical

def error(msg, *args, **kwargs):
    logging.getLogger(getLogName()).error(msg, *args, **kwargs)

def exception(msg, *args):
    error(*((msg,)+args), **{'exc_info': 1})

def warning(msg, *args, **kwargs):
    logging.getLogger(getLogName()).warning(msg, *args, **kwargs)

warn = warning

def info(msg, *args, **kwargs):
    logging.getLogger(getLogName()).info(msg, *args, **kwargs)

def monitor(msg, *args, **kwargs):
    logging.getLogger(getLogName()).log(MONITOR, msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    logging.getLogger(getDebugName()).debug(msg, *args, **kwargs)


#-----------------------------------------------------------------------
