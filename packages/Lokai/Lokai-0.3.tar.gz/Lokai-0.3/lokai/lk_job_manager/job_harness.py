# Name:      lokai/lk_job_manager/job_harness.py
# Purpose:   A job wrapper, based on tb_job_manager
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

import sys
import os
import optparse
import logging
import types

from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_common.dates import timetostr, now
from lokai.tool_box.tb_common.email_address_list import EmailAddressList
import lokai.tool_box.tb_job_manager.job_environment as job_env
import lokai.tool_box.tb_common.exception_format as exc_fmt
import lokai.tool_box.tb_common.configuration as config
import lokai.tool_box.tb_common.notification as tb_notify
import lokai.lk_job_manager.notification as notify

#-----------------------------------------------------------------------

"""
    Job Structure
    =============

    Each job follows the following general outline:

        set up identity

            (Define values that are used to identify the job for
            logging and finding its environment.)

        get command line options

        set the environment

        set logging

        initiate the process

            (Log the start if required)

        for file in environment input:

            start file

            process the file

            commit or rollback

            end file

        wrap up

            (Log completion, if appropriate, and close the logs.)
"""

#-----------------------------------------------------------------------

class ProcessingIssue(Exception):
    """ Common heading for these exceptions
    """
    pass

class UpstreamFailure(ProcessingIssue):
    """ General type for missing data
    """
    pass

class TemporaryUpstreamFailure(UpstreamFailure):
    pass

#-----------------------------------------------------------------------

SEVERITY_CRITICAL = 'CRITITCAL'
SEVERITY_ERROR = 'ERROR'
SEVERITY_WARNING = 'WARNING'
SEVERITY_NOTIFICATION = 'INFO'

BASE_VERBOSITY = 2 # Can't go below this level of verbosity

#-----------------------------------------------------------------------

def setLoggers(verbosity=0,
               log_file=None,
               process_id='unspecified',
               email_from=None,
               email_to=None,
               email_subject_line=None,
               criticality_level=logging.CRITICAL,
               critical_to=None,
               critical_subject=None,
               to_database=True,
               capacity = -1,
               ):
    """ Create a set of loggers.

        Multiple loggers can be set up so that information goes to as
        many places as might be needed.

        See the documentation for raising exceptions for an
        explanation of conventions for message levels.

        Stream logger:

            There is always a stream logger, output goes to a file or
            STDERR.

        Database logger:

            Optional logger - items are handled by the
            JobManagerLogHandler so that logged messages go to data
            exception entries in the lk_worker database.

        Email loggers:

            Optional loggers - One for critical messages and one for
            everything else.

        :verbosity:  0 : logging.ERROR,
                     1 : logging.WARNING,
                     2 : logging.INFO,
                     3 : notify.MONITOR,
                     4 : logging.DEBUG

            CRITICAL messages are always logged.
            
        :log_file: Name of file for the stream logger. If this is None
                   the output goes to STDERR.

        :process_id: Text name of the process calling
             us. Used to set the name of the logger family.

        :email_from: Email <from> address used in both email
            loggers. If empty there is no email logger.

        :email_to: Email recipient for non-critidal emails.

        :email_subject: The subject line for all non-critical emails.
        
        :critical_to: Email recipient for critical emails.

        :critical_subject: The subject line for all critical emails.

        :criticality_level: The level that defines messages that use
        the critical email logger.

        :to_database: Set `True` (default) if the database logger is
            to be used.

        :capacity: The number of bytes held in the JobNotifier buffer
            that will force a flush. If capacity is -ve then no
            automatic flushing is done and we rely on explicit flush
            or close.
       
    """
    if process_id != 'unspecified':
        notify.setLogName(process_id)

    verbosity_dict = {
        0 : logging.ERROR,
        1 : logging.WARNING,
        2 : logging.INFO,
        3 : notify.MONITOR,
        4 : logging.DEBUG}
    level = verbosity_dict.get(min(4, max(BASE_VERBOSITY, verbosity)),
                               logging.ERROR) 

    logging.basicConfig(level=logging.ERROR,
                        stream=sys.stderr)
    
    this_logger = notify.getLogger()
    this_logger.setLevel(level)
    
    if log_file:
        target_handler = logging.FileHandler(log_file)
    else:
        target_handler = logging.StreamHandler()

    # Set up a debug logger to trap any debug stuff from now on
    debug_logger = logging.getLogger(notify.getDebugName())
    debug_logger.addHandler(logging.StreamHandler())
    
    # Set one handler to output to a stream of some sort.
    main_handler = notify.JobNotifier(capacity = capacity)
    main_handler.setTarget(target_handler)
    main_formatter = notify.TextFormatter(
        linefmt=logging.Formatter(fmt=("%(levelname)s:%(message)s\n")))
    main_handler.setFormatter(main_formatter)
    this_logger.addHandler(main_handler)

    if to_database:
        # Set a second handler to go to the database.
        import lokai.lk_job_manager.job_manager_logger as jml
        db_handler = notify.JobNotifier()
        db_target = jml.JobManagerLogHandler()
        db_target_formatter = jml.JobManagerLogFormatter()
        db_formatter = tb_notify.BulkFormatter(
                linefmt = logging.Formatter(fmt="%(levelname)s:%(message)s\n"))
        db_handler.setFormatter(db_formatter)
        # do these things in the right order
        db_handler.setTarget(db_target)
        db_target.setFormatter(db_target_formatter)
        this_logger.addHandler(db_handler)

    # Set some email handlers to spam the world
    if email_from:
        if critical_to:
            mail_target = tb_notify.checkingSMTPHandler(
                'localhost',
                email_from,
                EmailAddressList(critical_to).as_list,
                critical_subject,
                )
            mail_formatter = notify.TextFormatter(
                linefmt = notify.UnicodeToStrFormatter(
                    fmt=(
                        "%(levelname)s:%(pathname)s:%(lineno)d:%(asctime)s:"
                        "%(message)s\n")
                    )
                )
            dev_mailer = tb_notify.BulkHandler()
            dev_mailer.setTarget(mail_target)
            dev_mailer.setFormatter(mail_formatter)
            dev_mailer.setLevel(criticality_level)
            this_logger.addHandler(dev_mailer)
        if email_to:
            mail_target = tb_notify.checkingSMTPHandler(
                'localhost',
                email_from,
                EmailAddressList(email_to).as_list,
                email_subject_line
                )
            mail_formatter = notify.TextFormatter(
                linefmt = notify.UnicodeToStrFormatter(
                    fmt=("%(levelname)s:%(message)s\n")
                    )
                )
            mailer = tb_notify.BulkHandler()
            mailer.setTarget(mail_target)
            mailer.setFormatter(mail_formatter)
            mailer.addFilter(tb_notify.FilterMax(criticality_level))
            logging.getLogger(notify.getLogName()).addHandler(mailer)
  
#-----------------------------------------------------------------------

default_options = {
    # Verbosity count is passed to the logger instances
    '-v'          : {
        'alias'    : ['--verbose'],
        'dest'     : 'verbosity',
        'default'  : 0,
        'action'   : "count",
        'help'     : ("If present - provide verbose output " 
                      "depending on the number of times " 
                      "the option appears")
        },
    # The parameter directory is used to search for ./param/{script}
    # which can be used to set other options
    '-p'          : {
        'alias'    : ['--parameter-directory'],
        'dest'     : 'parameter_directory',
        'default'  : None,
        'action'   : "store",
        'help'     : ("If present - provide absolute or " 
                      "relative path to the parameter directory. " 
                      "This directory should be able to access " 
                      "the ./param/{script} file for parameters")
        },
    # The unlock trigger will remove the lockfile if it is there.
    # This trigger should not be used in a production environment.
    '--unlock'    : {
        'dest'     : 'force_through_lock',
        'default'  : False,
        'action'   : "store_true",
        'help'     : ("If present - forcibly remove lock " 
                      "file on current input file before continuing")
        },
    # Process alias
    '-a'         : {
        'alias'     : '--application-alias',
        'dest'      : 'application_name',
        'default'   : None,
        'action'    : "store",
        'help'      : ("Give the name that this application will be known as"
                       " when running. The default is the name of the python"
                       " file that is being executed")
        },
    # User name
    '-u'         : {
        'alias'     : '--user',
        'dest'      : 'data_amended_by',
        'default'   : 'unspecified',
        'action'    : 'store',
        'help'      : ("Specify a user name to use when "
                       "recording who did what. This is purely textual "
                       "and is not checked against any actual user list.")
        },
    '-t'        : {
        'alias'     : '--timing',
        'dest'      : 'timing',
        'default'   : False,
        'action'    : 'store_true',
        'help'      : ("Include timing information in the MONITOR log")
        },
    '--reverse' : {
        'dest'      : 'reverse',
        'default'   : False,
        'action'    : 'store_true',
        'help'      : "Reverse the order of file scannng"
        },
    '--once_only':{
        'dest'      : 'one_shot',
        'default'   : False,
        'action'    : 'store_true',
        'help'      : ("Exit after processing one file only "
                       "(May not be supported in all derived file loops)")
        },
    }

#-----------------------------------------------------------------------

def process_options(description=None,
                    default_set=None,
                    extra_set=None,
                    **kwargs
                    ):
    """ Build an option parser and then parse the input """
    parser = optparse.OptionParser()
    if description:
        parser.description = description
    for option_set in [default_set, extra_set]:
        if option_set is None:
            continue
        for option, keywords in option_set.iteritems():
            name_set = [option]
            if 'alias' in keywords:
                alias_set = keywords['alias']
                if isinstance(alias_set, types.StringTypes):
                    name_set.append(alias_set)
                else:
                    name_set.extend(alias_set)
                del keywords['alias']
            parser.add_option(*name_set, **keywords)

    parser.set_defaults(**kwargs)
    return parser.parse_args()

#-----------------------------------------------------------------------


#-----------------------------------------------------------------------
class JobHarness(object):
    """ JobHarness object

        Provides the structure for a batch job.

    """

    # Overridables
    SUCCESS_MESSAGE = "Process success"
    ABANDON_MESSAGE = "Process abandoned"
    DELAY_MESSAGE = "Process delayed"
    DEFAULT_DELAY = 3600 # One hour
    
    def __init__(self,
                 system_component=None,
                 data_area=None,
                 process_ident=None,
                 process_description=None,
                 extra_options=None,
                 disposition='k',
                 **kwargs # defaults for options
                 ):
        self.component = system_component
        self.data_area = data_area
        self.process_description = process_description
        self.file_disposition = disposition
        
        self.base_file = os.path.basename(os.path.splitext(sys.argv[0])[0])

        self.process_ident = process_ident or self.base_file

        self.option_defaults = kwargs
        
        self.options,self.args = process_options(process_description,
                                                 default_options,
                                                 extra_options,
                                                 **kwargs)

        self.user = self.options.data_amended_by

        self.exc_stack_print = False # Do not print stack on error
        
        self.set_environment()
        self.set_loggers()
        self.filename = None
        notify.getLogger().execute_all(
            'setAttributes',
            **{'title': "%s: " % self.process_ident,
               'path': [self.component, self.data_area, self.process_ident]
                })

    def set_environment(self):
        """ Overridable code to set the job environment """
        self.environment = job_env.JobEnvironment(
            application_name=self.options.application_name,
            app_param_file=self.options.parameter_directory,
            )

    def set_loggers(self):
        """ Overridable code to set the loggers """
        cs = config.get_global_config()
        cs_all = cs.get('all', {})
        from_addr = cs_all.get('email_from')
        if not from_addr or '@' in from_addr:
            use_from = from_addr
        else:
            use_from = "%s@%s"%(from_addr, cs_all.get('smtp_from_host'))
        setLoggers(verbosity=self.options.verbosity,
                   process_id=self.process_ident,
                   email_from=use_from,
                   email_to=cs_all.get('email_site'),
                   email_subject_line=("Lokai: process %s: log" %
                                       self.environment.application_name),
                   critical_to=cs_all.get('email_dev'),
                   critical_subject=("Lokai: process %s: critical" %
                                     self.environment.application_name)
                   )
        if self.options.verbosity > 2:
            self.exc_stack_print = True

        self.notify_base_path = getattr(self.environment, 'notify_base_path', None)
        
        self.notify_sub_path = getattr(self.environment, 'notify_sub_path', None)
        if self.notify_sub_path is not None:
            path = self.notify_base_path
        else:
            path = [self.component, self.data_area, self.process_ident]
            path = [item for item in path if item is not None]
        
        notify.getLogger().execute_all(
            'setAttributes',
            **{'title': "%s: " % self.process_ident,
               'path': path
                })
        if self.notify_base_path is not None:
            notify.getLogger().execute_all(
                'setAttributes',
                **{'logging_target': self.notify_base_path
                   })

    def process(self):
        """ Main loop """
        self.num_files = 0
        try:
            self.process_start()
            self.process_loop()
            self.process_end("%d file%s processed" % (
                self.num_files,
                self.num_files == 1 and ' was' or 's were',
                ))
        except SystemExit:    
            exit(1)
        except:
            # Unknown exception, so let's log it
            # File processing errors should not bubble down to here
            self.report_an_error('main process')
            exit(1)

    def process_start(self):
        self.script_start = now()
        if self.options.timing:
            notify.monitor("Process Started: %s with %s @ %s" % (
                                    str(self.base_file),
                                    str(self.options),
                                    str(timetostr(self.script_start, 'iso'))))
        else:
            notify.debug("Process Started: %s with %s" % (
                                    str(self.base_file),
                                    str(self.options)))

    def process_end(self, extra=''):
        if extra:
            log_text = "Process Completed: %s: %s" % (str(self.base_file),
                                                      extra)
        else:
            log_text = "Process Completed: %s" % str(self.base_file)
        script_end = now()
        if self.options.timing:
            notify.monitor(log_text)
            notify.monitor("Process Timing: %s @ %s - took %s" % (
                str(self.base_file),
                str(timetostr(script_end, 'iso')),
                str(script_end - self.script_start)))
        else:
            notify.debug(log_text)
    
    def process_loop(self):
        """ This is where the real work happens. There can be a number
            of ways of doing things here. We choose to override this
            in one or more other classes to emphasise the differences.
        """
        raise NotImplementedError

    #-------------------------------------------------------------------
    # Manage what to do when an input file has been processed
    
    def operation_commit(self, keep_input=False):
        engine.session.commit()
        if self.environment:
            if not keep_input:
                self.environment.close_ok()
            self.environment.output_commit()
        return self.SUCCESS_MESSAGE

    def operation_rollback(self, keep_input=False):
        engine.session.rollback()
        if self.environment:
            if not keep_input:
                self.environment.close_error()
            self.environment.output_rollback()
        return self.ABANDON_MESSAGE
    
    def operation_delay(self, delay=None):
        use_delay = delay if delay is not None else self.DEFAULT_DELAY
        engine.session.rollback()
        if self.environment:
            self.environment.close_pending(use_delay)
            self.environment.output_rollback()
        return self.DELAY_MESSAGE
    
    def determine_close_action(self,
                               keep_input=False):
        """ Identify what to do depending on the severity of items logged.

            :keep_input: If True, the input file is **not** moved to any
                output directory and remains in the input directory
                for possible re-processing.
        """
        message_stats = logging.getLogger(notify.getLogName()).stats
        if message_stats.get(SEVERITY_CRITICAL, 0):
            info_text = self.operation_rollback(keep_input)
        elif message_stats.get(SEVERITY_ERROR, 0):
            info_text = self.operation_rollback(keep_input)
        elif message_stats.get(SEVERITY_WARNING, 0):
            info_text = self.operation_rollback(keep_input)
        elif message_stats.get(SEVERITY_NOTIFICATION, 0):
            notify.monitor(self.SUCCESS_MESSAGE)
            info_text = self.operation_commit(keep_input)
        else:
            notify.monitor(self.SUCCESS_MESSAGE)
            info_text = self.operation_commit(keep_input)
        return info_text
    
     #-------------------------------------------------------------------
    
    def start_file(self):
        self.num_files += 1
        id_text = self.filename
        # center the text
        p_len = len(id_text)
        if p_len < 75:
            side_len = int((78-p_len)/2)
            p_str = ('-'*side_len + ' ' + id_text + ' ' + '-'*side_len)
        else:
            p_str = ('-- ' + id_text + ' --')
        self.file_start = now()
        if self.options.timing:
            notify.monitor(p_str)
        else:
            notify.debug(p_str)

    def end_file(self):
        file_end = now()
        if self.options.timing:
            notify.monitor("Processing %s took %s" % (
                self.filename,
                str(file_end - self.file_start)))
        else:
            notify.debug("%s completed" % self.filename)
        self.filename = None # for the record
        
    #-------------------------------------------------------------------
    
    def add_critical_file_info(self):
        if self.filename:
            notify.critical("Processing: File:%s Time:%s" % (
                self.filename,
                timetostr(now(), 'long')))
        else:
            notify.critical("Target:%s Time:%s" % (
                self.process_ident,
                timetostr(now(), 'long')))

    def report_an_error(self, location, **kwargs):
        """ Create appropriate messages and logs for a critical error.
        """
        self.add_critical_file_info()
        extra = kwargs.get('extra', None)
        err_text = sys.exc_info()[1]
        err_stuff = ["%s: %s"% (str(sys.exc_info()[0]),
                                err_text),
                     "Error in %s"%location]
        if extra:
            err_stuff.append(extra)
        err_stuff.append(exc_fmt.get_print_exc_plus(self.exc_stack_print))
        err_str = '\n\n'.join(err_stuff)
        notify.critical(err_str)
        notify.getLogger().execute_all(
            'setAttributes',
            **{'title': "Error in %s" % self.process_ident,
             'path': [self.process_ident]
             })
        notify.getLogger().flush()

    def get_a_file_name(self, extn='', extra=None):
        """ Return a default name based on process ident and date
        """
        dot = ''
        if extn:
            if extn[0] != '.':
                dot = '.'
        if extra:
            op = "%s_%s_%s%s%s"%(self.process_ident,
                                 extra,
                                 timetostr(now(), 'compact'),
                                 dot,
                                 extn
                                 )
        else:
            op = "%s_%s%s%s"%(self.process_ident,
                                 timetostr(now(), 'compact'),
                                 dot,
                                 extn
                                 )
        return op    

#-----------------------------------------------------------------------

class FileProcessorJob(JobHarness):
    """ Generic job harness that loops through a set of input files
        and passes each one to a file processor. An application must
        sub-class this to provide the file processor.
    """

    SUCCESS_MESSAGE = "File process completed"
    ABANDON_MESSAGE = "File process abandoned"

    def process_loop(self, **kwargs):

        # Iterate the files
        for file_pointer in (
             self.environment.input_set(self.file_disposition,
                                        reverse=self.options.reverse)):
            # Process file_pointer
            self.filename = u'%s' % self.environment.get_base_input_name()
            #
            # 'error' - Failure (with additional logger.critical message)
            # 'warning' - Failure
            # 'notice' - Success 
            #
            # An empty set of keys will be listed as Success
            # Any raise will list all errors and append the trace back
            #
            self.start_file()
            info_set = []
            try:
                self.process_file(file_pointer)
                #
                # The process has not raised - Determine whether the
                # import was successful
                info_set.append(
                    self.determine_close_action())
            except TemporaryUpstreamFailure:
                self.operation_delay()
            except KeyboardInterrupt:
                notify.error("Keyboard Interrupt in file %s" % self.filename)
                exit(1)
            except:
                info_set = []
                info_set.append(self.operation_rollback())
                file_entry = None
                if (hasattr(self, 'current_line_number') and
                    self.current_line_number is not None):
                    info_set.append("Line number %s" %
                                    str(self.current_line_number))
                if (hasattr(self, 'current_line') and
                    self.current_line is not None):
                    info_set.append(self.current_line)
                # Unknown exception, so let's log it
                info_set.append("Technical Error Information:")
                self.report_an_error("process file loop",
                                     extra="\n\n".join(info_set),
                                     )
                break
            self.end_file()
            if self.options.one_shot:
                break
        #--
        self.all_files_done()

    def start_file(self):
        """ Override this with, for example, code to store file
            process data in a database (assuming this is not
            adequately handled by logging)
        """
        JobHarness.start_file(self)

    def end_file(self):
        """ Overrride this with, for example, code to store file
            process data in a database (assuming this is not
            adequately handled by logging)
        """
        JobHarness.end_file(self)
        notify.getLogger().execute_all(
            'setAttributes',
            **{'title': "%s: %s" % (self.process_ident, self.filename),
                })
        notify.getLogger().flush()
        notify.getLogger().execute_all(
            'setAttributes',
            **{'title': "%s: " % self.process_ident
                })

    def all_files_done(self):
        """ Hook for end of loop procesing if required.

            Only get here if there were no forced exits. Some files
            _may_ have had problems, but the loop continued to look
            for things to do.
           
        """
        pass

#-----------------------------------------------------------------------
