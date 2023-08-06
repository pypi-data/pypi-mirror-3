# Name:      lokai/tool_box/tb_common/magic_file.py
# Purpose:   A file-like object with magic actions on close
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

import os
import tempfile
import gzip
import shutil
import types

#-----------------------------------------------------------------------

class MFError(IOError):
    pass

def _create_tree(target):
    """ Create intermediate directories
    """
    head = os.path.dirname(target)
    if not os.path.isdir(head):
                os.makedirs(head)

def _rename(source, destination):
    """ Rename, but make sure the target directory structure exists
    """
    _create_tree(destination)
    shutil.move(source, destination)

class MagicFile(object):

    """ For output, output to a file that magically appears in the target
        directory (directories) when closed.

        For input, magically move the file to a 'processed' directory when
        closed.

        The given file name can be a relative path. When the file is
        closed, the directories in the this path are created under the
        given target directory (directories).

        Supports multiple destination directories (fan-out) where the file
        is copied (magically) to more than one directory.

        Both the destination directories and the name that the file will
        take after the move can be adjusted dynamically to give the
        calling application a chance to respond to file content.

        The action taken if the destination already exists can also be
        adjusted for different circumstances.
    """

    def __init__(self, file_name,
                 source_dir, target_dir,
                 mode, disposition=None):
        """ Create and open the file object

            file_name = relative path, including at lease the base
                name of the file.

            source_dir = Path for the directory containing file_name.

                For input or append modes the given file_name must
                exist in this directory.  For output a file is created
                in this directory.

                If target_dir is not None then the source_dir is
                treated as a temproary directory and the newly created
                file is given a temporary name.

            target_dir = Path to the directory where the file will
                appear when closed. If 'None', then the file is not moved.

                Providing a target_dir when you want to write to a
                file means that the output is placed into a temporary
                file which is then renamed on close. If you are trying
                to overwrite an existing file then you can set source
                and target to be the same and the overwrite will
                happen magically on close. If you are trying to write
                to an existing file and you set the source and target
                to different directories then the output will appear
                in the target, but the original file will remain in
                the source.

                Providing a target_dir when you want to read from a
                file means that the source file is renamed into the
                target dir on close.

                You may provide a list of paths. In this case the
                single file magically appears in each of the paths in
                the list.
                
            mode = Standard file opening modes. Normally 'r' or
                'w'. You can use 'a', but this acts rather like 'r'
                and some of the majic is lost.

            disposition = flag to say what to do if the rename action
                finds there is a file of the same name already in the
                target_dir.

                'k' = keep the file so found and do not do any renaming.

                'o' = overwrite the file (delete before renaming).

                Anything else raises an error. The name is checked on
                open (so that the application can re-think what to do)
                and on close (in case another aplication got in
                first). The close action can be repeated. It is
                possible to change the rename target (both file name
                and target directory), so that the application can
                gracefully recover.
        """
        self.target_container_set = None
        self.target_file_name = None
        self.source_container = os.path.abspath(
                   os.path.normcase(
                       os.path.normpath(source_dir)))
        self.source_file_name = file_name
        self.disposition = None
        self.set_rename_target(name=file_name,
                               directory=target_dir,
                               disposition=disposition)
        self.mode = None
        self.file_object = None
        self.file_object_path = None
        self.is_dirty = False
        self._open(mode)

    def set_rename_target(self, name=None, directory=None, disposition=None):
        """ Set where the open file will be moved to when it is closed.

            If either parameter is omitted or set to None then the
            current vlaue of the internal variable is not
            changed. Thus, it is not possible to set the target_dir to
            None using this method.
        """
        if disposition is not None:
            self.disposition = disposition
        if isinstance(directory, types.StringTypes):
            self.target_container_set = [
                os.path.abspath(
                    os.path.normcase(
                        os.path.normpath(directory)))
                ]
        elif isinstance(directory, (list, tuple)):
            self.target_container_set = [
                os.path.abspath(
                    os.path.normcase(
                        os.path.normpath(dx))) for dx in directory
                ]
            
        if isinstance(name, types.StringTypes):
            self.target_file_name = name

        # Check the rename target does not violate the disposition.
        self._check_target()

    def _open(self, mode):
        """ Open the file. This is called from the class init method
            and there is no need for it to be public.
        """
        self.mode = mode

        # Identify the file to open
        if 'w' in mode:
            if self.target_container_set is not None:
                # If we have a target_dir, then we just create a temp
                # file.
                os_handle, self.file_object_path = (
                    tempfile.mkstemp(dir=self.source_container))
                self.file_object = os.fdopen(os_handle, 'w')
            else:
                # The file may or may not exist, but intermediate
                # directories should exist. These can be created.
                self.file_object_path = source_full_path = (
                    os.path.join(self.source_container, self.source_file_name))
                _create_tree(source_full_path)
        else:
            # Assume the file exists.
            self.file_object_path = source_full_path = (
                    os.path.join(self.source_container, self.source_file_name))
        
        if self.file_object is None:
            # Open a file
            
            # Handle Gzipped files if necessary
            extn = os.path.splitext(source_full_path)
            if extn[1].lower() in ['.gz', '.z']:
                fixed_mode = mode
                if 'r' in mode:
                    fixed_mode = 'r' # to avoid 'rU'
                self.file_object = gzip.GzipFile(source_full_path, fixed_mode)
            else:
                self.file_object = open(source_full_path, mode)

    def _check_target(self):
        """ make sure the target does not contain a clashing name
        """
        if self.disposition in ['k', 'o']:
            return
        if self.target_container_set is None:
            return
        for dx in self.target_container_set:
            target_full_path = os.path.join(dx, self.target_file_name)
            if os.path.exists(target_full_path):
                raise MFError, "target %s already exists"%target_full_path

    def _rename_from_list(self):
        """ Move stuf to make it magically appear
        """
        if self.target_container_set is None:
           return
        self._check_target()
        # Go through all the targets except the first
        for dx in self.target_container_set[1:]:
           target_full_path = os.path.join(dx, self.target_file_name)
           os_handle, copy_target_name = (
               tempfile.mkstemp(dir=self.source_container))
           copy_target = os.fdopen(os_handle, 'w')
           if os.path.exists(target_full_path):
               if self.disposition == 'k':
                   copy_target.close()
                   os.remove(copy_target_name)
               elif self.disposition == 'o':
                   os.remove(target_full_path)
                   copy_source = open(self.file_object_path, 'r')
                   shutil.copyfileobj(copy_source, copy_target)
                   copy_target.close()
                   copy_source.close()
                   _rename(copy_target_name, target_full_path)
               else:
                   raise MFError, "target %s already exists"%target_full_path
           else:
               copy_source = open(self.file_object_path, 'r')
               shutil.copyfileobj(copy_source, copy_target)
               copy_target.close()
               copy_source.close()
               _rename(copy_target_name, target_full_path)
        # Now finish off with the one remaining
        dx = self.target_container_set[0]
        target_full_path = os.path.join(dx, self.target_file_name)
        if os.path.exists(target_full_path):
           if self.disposition == 'k':
               os.remove(self.file_object_path)
           elif self.disposition == 'o':
               os.remove(target_full_path)
               _rename(self.file_object_path, target_full_path)
           else:
               raise MFError, "target %s already exists"%target_full_path
        else:
            _rename(self.file_object_path, target_full_path)

    def close(self, delete=False):
        """ Close the open file, move the file to the target_dir as required.

            This may be called more than once. The actual file is
            closed on first entry. A second try might be needed if
            there is clash in the target_dir.

            The delete flag forces the file to be deleted on close
            instead of being renamed. This is used to support
            application rollback.
        """
        if self.file_object:
            self.file_object.close()
            self.file_object = None
        if self.file_object_path:
            if (delete or
                (not self.is_dirty and 'w' in self.mode)):
                os.remove(self.file_object_path)
                self.file_object_path = None
            else:
                self._rename_from_list()
                self.file_object_path = None

    def readlines(self, *k):
        try:
            return self.file_object.readlines(*k)
        except AttributeError:
            if self.file_object is None:
                raise MFError, "File object is closed"
            else:
                raise

    def readline(self, *k):
        try:
            return self.file_object.readline(*k)
        except AttributeError:
            if self.file_object is None:
                raise MFError, "File object is closed"
            else:
                raise

    def read(self, *k):
        try:
            return self.file_object.read(*k)
        except AttributeError:
            if self.file_object is None:
                raise MFError, "File object is closed"
            else:
                raise

    def write(self, *k):
        self.is_dirty = True
        try:
            return apply(self.file_object.write, k)
        except AttributeError:
            if self.file_object is None:
                raise MFError, "File object is closed"
            else:
                raise

    def writelines(self, *k):
        self.is_dirty = True
        try:
            return self.file_object.writelines(*k)
        except AttributeError:
            if self.file_object is None:
                raise MFError, "File object is closed"
            else:
                raise

    def seek(self, *k):
        try:
            return self.file_object.seek(*k)
        except AttributeError:
            if self.file_object is None:
                raise MFError, "File object is closed"
            else:
                raise
        
    def __iter__(self):
        return self

    def next(self):
        nextline = self.readline()
        if not nextline:
            raise StopIteration()

        return nextline

    def get_name(self):
        if self.file_object:
            return self.file_object_path
        return None

    name = property(get_name)

#-----------------------------------------------------------------------
