# Name:      lokai/tool_box/tb_job_manager/job_environment.py
# Purpose:   A job message board
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
import inspect
import types
import datetime
import yaml
import logging

import lokai.tool_box.tb_common.notification as notify
from lokai.tool_box.tb_common.email_address_list import EmailAddressList

from lokai.tool_box.tb_common.dates import strtotime, timetostr, now

import lokai.tool_box.tb_common.magic_file as magic
import lokai.tool_box.tb_common.file_handling as file_handling

#-----------------------------------------------------------------------

"""
    File Meta Data
    ==============

    Files are able to store meta data as part of the file name. This
    recognises that the file name is key to the operation of the job
    system in that each request for activation of a job must have a
    different filename, otherwise one request might be overwritten by
    another. The implication is that the filename has meaning. The
    presence of meta data in the filename gives the application a
    formal structure to use for distinguishing requests. The meta data
    is used by the job environment object to manage automatic
    re-queueing of jobs using the pending queue.

    Meta data us stored in the filename as a yaml string enclosed in
    '{}' just before the file extension, if any. This works fine so
    long as the dictionary only contains scalar values.

    There is also an implementation limitation that the meta data
    itself cannot contain '{'.
    
"""

def get_file_meta(file_name):
    """ given a file path, return dictionary:

        {directory, file_base, extension, meta_string}
    """
    directory, basename = os.path.split(file_name)
    file_plus, extension = os.path.splitext(basename)
    file_base = file_plus
    meta_string = ''
    meta_values = {}
    if file_plus[-1] == '}':
        # we have meta data
        for ptr in range(len(file_plus)-1, 0, -1):
            if file_plus[ptr] == '{':
                file_base = file_plus[:ptr]
                meta_string = file_plus[ptr:]
                meta_values = yaml.load(meta_string)
                break
    return {'directory': directory,
            'file_base': file_base,
            'extension': extension,
            'meta_string': meta_string,
            'meta_values': meta_values,
            'file_name': basename}

def put_file_meta(file_directory, given_meta_values={}):
    """ given a path and meta data in the form of a dictionary (see
        above), return a full path and revised filename in a new dictionary.

        {directory, file_base, extension,
         meta_string, meta_values,
         full_path, file_plus_extn}
    """
    meta_values = ((given_meta_values is not None and
                    given_meta_values) or
                   {})
    new_meta_values = {}
    new_meta_values.update(file_directory['meta_values'])
    new_meta_values.update(meta_values)
    meta_string = ''
    if new_meta_values:
        meta_string = yaml.dump(new_meta_values,
                                default_flow_style=True).strip()
        file_plus_extn = "%s%s%s"% (file_directory['file_base'],
                                      meta_string,
                                      file_directory['extension'])
    else:
        file_plus_extn = "%s%s"% (file_directory['file_base'],
                                      file_directory['extension'])
    result = {}
    result.update(file_directory)
    result['meta_string'] = meta_string
    result['meta_values'] = meta_values
    result['file_name'] = file_plus_extn
    result['full_path'] = os.path.join(file_directory['directory'],
                                       file_plus_extn)
    return result

#-----------------------------------------------------------------------
class JobEnvironment(object):

    """ A JobEnvironment provides the basic tools that allow batch
        jobs to manage their own processes.

        The JobWraper object deals with the indentification and
        management of input and output files. The invocation of an
        application as a job instance can be done using cron, at, or
        any other scheduling process.

        Equally, any standard application patters (file loops,
        logging, error handling an so on) would be handled by higher
        level objects using these tools.

        Environment
        ===========
        
        An application is assumed to manage its communication with the
        outside world using a set of input and output directories.

        Input:

            Immediate:
            
                One or more input directories can be set up. Each
                input directory may contain a further set of
                sub-directories.  JobEnvironment identifies the
                'first' actual file in this directory tree and
                presents it to the application for processing. The
                file may simply indicate 'start processing', it may
                define a set of parameters for the process, or it may
                be a file of data to process.

                The normal assumption would be that no input means no
                work to be done.  Applications that monitor external
                events (dates, web-site status and so on) may choose
                to run without an input file trigger.

                The input file is opened using a MagicFile object so
                that, when the file is closed, it is moved to a
                'processed' directory (see below).

            Pending:

                A directory structure where the immediate
                sub-directory defines a date and time. This structure
                is not explored for files until after the given
                data/time. Thus it is possible to queue actions into
                the future.

        Output:

            Immediate:

                One or more output directories can be set up. A single
                output file (opened using a MagicFile object) is
                duplicated under each of the output directories. This
                provides fan-out so that the completion of one
                application can trigger one or more follow-on
                processes.

                The output file can be opened with a relative
                path. This path is preserved underneath each of the
                output directories.

            Processed:

                One or more 'processed' directories can be set up. An
                input file, opened using a MagicFile object, is moved
                to a processed directory when the file is closed. If
                there is more than one such directory the file is
                duplicated into each of them. This provides fan-out so
                that the completion of one application can trigger one
                or more follow-on processes.

                The sub-directory structure from the input is
                maintained in this rename process. Thus, if the input
                is ``source_path/sub_1/my_file`` this will be placed
                into ``processed_path/sub_1/my_file``

            Error:

                A single error directory can be set up. If the
                application detects an error (and calls the correct
                close function) the input file is moved to this error
                directory. This has the effect of removing the file
                from the input, so it is not reprocessed, and, at the
                same time, isolating the problem file so that it can
                be dealt with.
                
                The sub-directory structure from the input is
                maintained in this rename process. Thus, if the input
                is ``source_path/sub_1/my_file`` this will be placed
                into ``error_path/sub_1/my_file``

        File Locks
        ==========

        It is potentially possible for two process to access the same
        input directory at the same time, possibly by design, more
        often because the process has been started by cron before the
        previous instance has finished. Consequently, it is possible
        for two processes to attempt to read the same file.

        The solution is to use a lock file. The job environment
        automatically creates a hidden file (name starting with '.')
        in the directory where the file is, using the base name of the
        file. This is then removed on close.

        In the case that the input directory is read-only, the job
        environment can be given a lock directory as an alternative.
        This can lead to duplicate lock file names for different input
        files (from different sub-directories). This is not a real
        problem, however. The wrongly locked input file will be
        processed at the next run.

        The lock file processing only works if the job environment
        methods are used. File locking is not handled by the MagicFile
        object.

        Output files are not locked. The operation of the MagicFile
        object means that the file does not appear in the output
        directory until it complete.
    
        Parameter File
        ==============

        The setting of input and output directories is done using one
        or more Python executable parameter files.

        The parameter files detailed here handle job management
        only. System wide parameters, such as database connections,
        for example, must be handled in some other way.

        There is a single paramter file that contains default values
        for various locations.

        By default the general parameter file is called
        job_environment.conf and is found in the current working
        directory. The file does not have to exist.

        Each application has its own parameter file defining the
        details for that application.

        By default the paramter file has the same
        name as the application (without the path and extension).
        Thus, the application ``path/to/my_app.py`` has a parameter
        file called ``my_app``.

        By default, also, the parameter files are found in a directory
        ``job_environment.d`` in the current working directory.

        The locations of both the general and application specific
        parameter files can be given to JobEnvironment on
        instantiation.

        The general paramter file can also contain the name of a
        directory that contains the aplication files. This is most
        useful when you need, for example, to run the same application
        set over different data sets in parallel. The general
        parameters can point to the data sets and the application
        specific files can be shared between the two environments.

        Parameter settings:

            app_param_path

                A path, absolute or relative to the current working
                directory, to the directory containing the application
                parameter files. Only meaningful in the general
                parameter file.

            environment_path

                A path, absolute or relative to the current working
                directory, that defines the processing environment.
                All other relative paths in the settings below are
                relative to this value.

            source_path

                A single path, or a list of paths. This path is
                searched for input files.

            pending_path

                A single path. Timed queue entries are represented by
                sub-directories immediately below this path.

            processed_path

                A path, or list of paths. Input files are moved to
                this path (or duplicated to all paths in the list)
                when closed.

            error_path

                A single path. Input files are moved to
                this path when closed.
                
            output_path

                A path or a list of paths. Files opened for output are
                moved to here on close.

            temporary_path

                A single path. Files opened for output are kept here
                while they are open.

            lock_file_location

                A path to a directory where the application specific
                lock-file will be created.

        Parameters may also be overridden on object insantiation.
        
    """

    def __init__(self,
                 general_param_file=None,
                 app_param_path = None,
                 app_param_file=None,
                 environment_path=None,
                 source_path=None,
                 pending_path=None,
                 processed_path=None,
                 error_path=None,
                 output_path=None,
                 temporary_path=None,
                 lock_file_location=None,
                 application_name=None,
                 lock_file_ignore=False,
                 ):

        # Defaults
        self.application_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        self.application_name = application_name or self.application_name
        
        self.general_param_file = general_param_file or 'job_environment.conf'
        self.app_param_path = 'job_environment.d'
        self.environment_path = self.application_name
        self.source_path = 'input'
        self.pending_path = 'pending'
        self.processed_path = 'processed'
        self.error_path = 'error'
        self.output_path = 'output'
        self.temporary_path = 'temp'
        self.lock_file_ignore = lock_file_ignore
        
        # get the general file if it exists else rely on default
        if os.path.exists(self.general_param_file):
            self._read_param_file(self.general_param_file)
        
        self.app_param_path = app_param_path or self.app_param_path
        self.app_param_file =  app_param_file or self.application_name

        # get the application file
        self._read_param_file(
            os.path.join(self.app_param_path,
                         self.app_param_file))

        # Override using the rest of the init arguments
        self.environment_path = environment_path or self.environment_path
        self.source_path = source_path or self.source_path
        self.pending_path = pending_path or self.pending_path
        self.processed_path = processed_path or self.processed_path
        self.error_path = error_path or self.error_path
        self.output_path = output_path or self.output_path
        self.temporary_path = temporary_path or self.temporary_path
        self.lock_file_location = lock_file_location

        # make lists where appropriate
        if isinstance(self.source_path, types.StringTypes):
            self.source_path = [self.source_path]
        if isinstance(self.output_path, types.StringTypes):
            self.output_path = [self.output_path]
        if isinstance(self.processed_path, types.StringTypes):
            self.processed_path = [self.processed_path]

        # process paths to locate in the environment
        if self.source_path:
            self.source_path = [os.path.join(self.environment_path, dd)
                                for dd in self.source_path]
        if self.output_path:
            self.output_path = [os.path.join(self.environment_path, dd)
                                for dd in self.output_path]
        if self.processed_path:
            self.processed_path = [os.path.join(self.environment_path, dd)
                                for dd in self.processed_path]
        if self.pending_path:
            self.pending_path = os.path.join(self.environment_path,
                                               self.pending_path)
        if self.error_path:
            self.error_path = os.path.join(self.environment_path,
                                               self.error_path)
        if self.temporary_path:
            self.temporary_path = os.path.join(self.environment_path,
                                               self.temporary_path)
        if self.lock_file_location:
            self.lock_file_location = os.path.join(self.environment_path,
                                               self.lock_file_location)

        # Control stuff
        self.current_source_name = None
        self.current_source_object= None

        self.current_target_name = None
        self.current_target_object = None

        self.current_lock_object = None
        
        self.current_lock_fd = None
        self.current_lock_name = None

    def _read_param_file(self, file_path):
        """ Read and execute the given file. Transfer result to our
            attributes. Avoid overwriting our methods.
        """
        dummy_global = {}
        argset = {}
        execfile(file_path, dummy_global, argset)
        for key, value in argset.iteritems():
            try:
                obj = getattr(self, key)
                if inspect.ismethod(obj):
                    continue
                setattr(self, key, value)
            except AttributeError:
                setattr(self, key, value)

    #-------------------------------------------------------------------
    # Input stuff

    def get_lock(self, candidate_source, file_path):
        file_head, file_name = os.path.split(
            os.path.join(candidate_source, file_path))
        lock_head = self.lock_file_location or file_head
        lock_name = '.LCK.'+file_name
        lock_path = os.path.join(lock_head, lock_name)
        if (self.lock_file_ignore and
            os.path.isfile(lock_path)):
            os.remove(lock_path)
        try:
            self.current_lock_fd = os.open(lock_path, os.O_CREAT+os.O_EXCL)
            self.current_lock_name = lock_path
            return True
        except OSError, message:
            if str(message).startswith('[Errno 17] File exists'):
                return False
            else:
                raise

    def clear_lock(self):
        if self.current_lock_fd:
            os.close(self.current_lock_fd)
            os.remove(self.current_lock_name)
        self.current_lock_fd = None
        self.current_lock_name = None

    def open_from_source(self, disposition='k', reverse=False):
        """ not quite an iterator to provide the next available file.

            The search is repeated from the top every time so that new
            entries are found as soon as possible.
            
            See magic_file for interpretaion of ``disposition``
        """
        if self.current_source_object is not None:
            self.current_source_object.close()
            self.current_source_object = None

        for candidate_source in self.source_path:
            for result in (
                file_handling.ordered_walk(candidate_source, reverse=reverse)):
                if os.path.basename(result).startswith('.'):
                    # Ignore hidden (unix) files
                    continue
                self.current_source_name = result
                if not self.get_lock(candidate_source, result):
                    continue
                self.current_source_object = magic.MagicFile(
                    self.current_source_name,
                    candidate_source,
                    self.processed_path,
                    'r',
                    disposition=disposition,
                    )
                return self.current_source_object
                #>>>>>>>>>>>>>>>>>>>>

        if self.pending_path and os.path.exists(self.pending_path):
            pending_set = os.listdir(self.pending_path)
            pending_set.sort()
            for pending in pending_set:
                pending_time = strtotime(pending)
                if pending_time < now():
                    input_path = os.path.abspath(
                        os.path.join(self.pending_path,
                                     pending))
                    for result in (
                        file_handling.ordered_walk(input_path)):
                        if  os.path.basename(result).startswith('.'):
                            # Ignore hidden (unix) files
                            continue
                        self.current_source_name = result
                        if not self.get_lock(candidate_source, result):
                            continue
                        self.current_source_object = (
                            magic.MagicFile(
                                self.current_source_name,
                                input_path,
                                self.processed_path,
                                'r',
                                disposition=disposition,
                                )
                            )
                        return self.current_source_object
                        #>>>>>>>>>>>>>>>>>>>>
        return None

    def input_set(self, disposition='k', reverse=False):
        """ Iterator for open_from_source """
        op = self.open_from_source(disposition, reverse=reverse)
        while op:
            yield op
            op = self.open_from_source(disposition, reverse=reverse)

    def close_ok(self):
        """ Close the current input in the normal way
        """
        if self.current_source_object is None:
            return
            #>>>>>>>>>>>>>>>>>>>>
        self.current_source_object.close()
        self.current_source_object = None
        self.clear_lock()

    def close_error(self):
        """ Close the input after an error. The input is renamed to
            the error path, if given, or the processed path otherwise.
        """
        if self.current_source_object is None:
            return
            #>>>>>>>>>>>>>>>>>>>>
        if hasattr(self.current_source_object, 'set_rename_target'):
            self.current_source_object.set_rename_target(
                directory=self.error_path)
        self.current_source_object.close()
        self.current_source_object = None
        self.clear_lock()

    def _get_delay_source(self, delay):
        """ Construct a directory name for a delay queue.

            Create the directory if needed.
        """
        if self.pending_path:
            # Calculate name of delay directory
            delay_source = timetostr(
                now()+datetime.timedelta(seconds=delay),
                "%Y%m%d%H%M")
            delay_path = os.path.join(self.pending_path,
                                      delay_source)
            if not os.path.exists(delay_path):
                os.makedirs(delay_path)
            return delay_path
        return None
                
    def close_pending(self, delay):
        """ Close the input and re-queue it for execution after the
            given number of seconds delay.

            The file name is given meta data with a 'repeat' count so
            that the application can keep track of how many times this
            gets done.
            
        """
        if self.current_source_object is None:
            return
            #>>>>>>>>>>>>>>>>>>>>
        if hasattr(self.current_source_object, 'set_rename_target'):
            delay_source = self._get_delay_source(delay)
            if delay_source:
                # Add repeat count meta data
                file_detail = get_file_meta(self.current_source_name)
                meta_count = file_detail['meta_values'].get('repeat', 0)
                meta_count += 1
                new_file_detail = put_file_meta(file_detail,
                                                {'repeat': meta_count})
                self.current_source_object.set_rename_target(
                    name=new_file_detail['file_name'],
                    directory=delay_source)
            
        self.current_source_object.close()
        self.current_source_object = None
        self.clear_lock()

    def post_pending(self, future_date, file_name, file_content):
        """ Create a new file in an input directory for this process.

            future_date = the date after which the file should be
                used. Can be None or empty, in which case future date
                is today.

            file_name = the name of the file to create.

            file_content = some text to put into the file.
        """
        use_date = future_date
        if not future_date:
            use_date = now()
        control_source = timetostr(use_date, "%Y%m%d%H%M")
        control_path = os.path.join(self.pending_path,
                                  control_source)
        if not os.path.exists(control_path):
            os.makedirs(control_path)
        file_path = os.path.join(control_path, file_name)
        fp = open(file_path, 'w')
        fp.write(file_content)
        fp.close()

    def get_base_input_name(self):
        if self.current_source_name:
            return os.path.basename(self.current_source_name)
        else:
            return None
  
    #-------------------------------------------------------------------
    # Output stuff

    def open_output(self, file_name, disposition='k'):
        """ Open the given file (relative path) for output. It will
            appear in the output directory when closed.
        
            See magic_file for interpretaion of ``disposition``
        """
        self.close_output() # with no opportunity for rollback
        self.current_target_object = magic.MagicFile(
            file_name,
            self.temporary_path,
            self.output_path,
            'w',
            disposition=disposition,
            )
        return self.current_target_object

    def close_output(self, delete=False):
        """ Close the current output file.

            Set delete=True to delete the output.
        """
        if self.current_target_object is not None:
            self.current_target_object.close(delete=delete)
            self.current_target_object = None

    def set_output_rename_target(self, name=None, directory=None):
        """ See magic_file set_rename_target
        """
        if self.current_target_object is not None:
            self.current_target_object.set_rename_target(name, directory)

    def output_rollback(self):
        """ Abandon any output by closing the file and then deleting
            it.

            This does not work for appending to existing files!
        """
        if self.current_target_object is None:
            return
            #>>>>>>>>>>>>>>>>>>>>
        self.close_output(delete=True)

    def output_commit(self):
        """ Close the output file in the normal way.
        """
        self.close_output()

    #-------------------------------------------------------------------
    # Lock file

    def get_lock_file(self):
        """ Return the path to the lock file for this application
        """
        return os.path.join(self.lock_file_location,
                            self.application_name)
        
    def open_lock(self, force=False):
        """ Grab the lock.

            Delete any previous lock if force is True
        """
        lock_file = self.get_lock_file()
        if force:
            self.close_lock()
        try:
            self.current_lock_object = os.open(lock_file, os.O_CREAT+os.O_EXCL)
            return True
        except:
            return False

    def close_lock(self):
        """ Close any open lock
        """
        if self.current_lock_object:
            os.close(self.current_lock_object)
        lock_file = self.get_lock_file()
        if os.path.isfile(lock_file):
            os.remove(lock_file)

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
               ):
    """ Batch jobs need logging. setLoggers is a tool to initialise
        logging in an application.

        This set-up includes creating a logger channel using
        ``process_id`` as the name. Applications should use::
        
        ``from notification import (critical, error, warning, info, debug)``

        Then, passing a log message back through the appropriate one
        of these routines will do the right thing.
        

        Logging may be set up to use an email logger (see
        tool_box.tb_common.notification). For email delivery, logging
        assumes that reports with a logging level higher than some
        value may be different from lower priority reports. This is
        reflected in the options that can be given.

        High level reports go to 'critical_to'

        Low level reports go to 'email_to' - high level reports do
        _not_ got to this email.

        Other handlers can be added as required.
        
        This is not a critical part of the job environment. There are many
        different ways to do this. ymmv.
    """

    if process_id != 'unspecified':
        notify.setLogName(process_id)

    verbosity_dict = {
        0 : logging.ERROR,
        1 : logging.WARNING,
        2 : logging.INFO,
        3 : logging.DEBUG}
    level = verbosity_dict.get(min(3, verbosity), logging.ERROR) 

    logging.basicConfig(level=logging.ERROR,
                        stream=sys.stderr)
    
    this_logger = logging.getLogger(notify.getLogName())
    this_logger.setLevel(level)
    
    if log_file:
        # Output to designated file
        handler = logging.FileHandler(log_file)
    else:
        # Output to console instead
        handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logging.getLogger(notify.getLogName()).addHandler(handler)

    if email_from:
        if critical_to:
            mail_target = notify.checkingSMTPHandler(
                'localhost',
                email_from,
                EmailAddressList(critical_to).as_list,
                critical_subject,
                )
            mail_formatter = notify.BulkFormatter(
                linefmt = logging.Formatter(
                    fmt=(
                        "%(levelname)s:%(pathname)s:%(lineno)d:%(asctime)s:"
                        "%(message)s\n")
                    )
                )
            dev_mailer = notify.BulkHandler()
            dev_mailer.addTarget(mail_target)
            dev_mailer.addFormatter(mail_formatter)
            dev_mailer.setLevel(criticality_level)
            this_logger.addHandler(dev_mailer)
        if email_to:
            mail_target = notify.checkingSMTPHandler(
                'localhost',
                email_from,
                EmailAddressList(email_to).as_list,
                email_subject_line
                )
            mail_formatter = notify.BulkFormatter(
                linefmt = logging.Formatter(
                    fmt=("%(levelname)s:%(message)s\n")
                    )
                )
            mailer = notify.MailerHandler()
            mailer.addTarget(mail_target)
            mailer.addFormatter(mail_formatter)
            mailer.addFilter(notify.FilterMax(criticality_level))
            logging.getLogger(notify.getLogName()).addHandler(mailer)

#-----------------------------------------------------------------------
