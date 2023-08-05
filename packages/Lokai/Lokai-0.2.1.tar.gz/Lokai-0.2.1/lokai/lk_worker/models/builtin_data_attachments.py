# Name:      lokai/lk_worker/models/builtin_data_attachments.py
# Purpose:   Define plugins on the IWorkerData interface
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
import glob
import pyutilib.component.core as component
from sqlalchemy import and_

import lokai.tool_box.tb_common.configuration as config
from lokai.tool_box.tb_common.dates import strtotime, now
from lokai.tool_box.tb_database.orm_interface import engine
from lokai.tool_box.tb_database.orm_base_object import OrmBaseObject
from lokai.tool_box.tb_database.orm_access import insert_or_update

from lokai.lk_worker.models import (
    ndNode,
    model,
    )

from lokai.lk_worker.extensions.data_interface import IWorkerData

#-----------------------------------------------------------------------

class ndAttachment(OrmBaseObject):

    search_fields = ['base_location',
                     'other_location',
                     'file_name',
                     'file_version']

model.register(ndAttachment, 'nd_attachment')

#-----------------------------------------------------------------------

BASE_VERSION = "_%03d"
MAX_VERSION = 1000

def make_version(number):
    return BASE_VERSION% number

def strip_version(string):
    return int(string[1:])

def unpack_version(filename):
    name_version, extension = os.path.splitext(filename)
    len_base = len(make_version(0))
    name = name_version[:-len_base]
    version = name_version[-len_base:]
    if version[0] == '_':
        if version[1:].isdigit():
            return (name, version, extension)
        elif version == '_'*len_base:
            return (name, None, extension)
    else:
        return name_version, None, extension

#-----------------------------------------------------------------------

class AttachmentError(Exception):
    pass

class AttachmentNotFound(AttachmentError):
    pass

#-----------------------------------------------------------------------

class Attachment(object):
    """ Allow access to an attachment using the ID fields from the
        attachment table in the database.

        Given a version of None - the class assumes a new file.

        Anything else, the class can be used to find an existing file.
        
    """

    def __init__(self,
                 base_location, other_location,
                 filename, version=None,
                 **kwargs):
        """ Initialise with a set of ID arguments. Generally the call
            will know these :-)

            base_location defines a head directory.

            other_location allows for the calculation of a sub-directory.

            Mostly these are used as defaults. An extension object
            would register methods in other_id_process and
            path_location to calculate the necessary paths.
        """
        #
        self.base_location = base_location
        self.other_location = other_location
        self.file_name = filename
        self.version = version
        self.user_name = kwargs.get('user_name')
        self.description = kwargs.get('description')
        self.content = kwargs.get('content')
        self.unpack = kwargs.get('unpack', False)
        if self.unpack:
            name, v_text, extension = unpack_version(filename)
            self.file_name = name+extension
            if v_text is not None:
                self.version = strip_version(v_text)
                self.get_detail()
            else:
                self.get_detail_latest()
        self.full_path = None
        self.base_file_set = None
        self.target_path = None
        self.target_version = None
        self.timestamp = now()
        self.fp = None
        #
        self.file_source = None # For creating new attachment
        #
        # Registered directory mapping callbacks.
        self.other_id_process = {}
        self.path_location = {}

    def register_id_process(self, base_location, method):
        """ Register some specific ID process for a base_location.
        """
        self.other_id_process[base_location] = method

    def register_path_location(self, base_location, method):
        """ Register some process that will return an absolute path
            for the given base_location
        """
        self.path_location[base_location] = method

    def _default_root_path(self):
        return self.base_location
    
    def _default_id_path(self):
        return self.other_location

    def _make_path(self):
        """ Build a full path if we need to.

            Defer calls to this because we may not have the id process
            registered yet.
        """
        if self.full_path == None:
            self.full_path = os.path.join(
                self.path_location.get(self.base_location,
                                          self._default_root_path)(),
                self.other_id_process.get(self.base_location,
                                          self._default_id_path)()
                )
        
    def _find_base_file_set(self):
        """ Return zero, one or more files that match the basic file
            name.
        """
        if self.base_file_set == None:
            self._make_path()
            name, extension = os.path.splitext(self.file_name)
            test_path = os.path.join(self.full_path, "%s*%s"% (name, extension))
            self.base_file_set = glob.glob(test_path)

    def get_latest_version(self):
        """ Given a file_set, identify the largest version string.

            Since version 0 represents the first version, we return -1
            if the file does not exist.
        """
        self._find_base_file_set()
        version = -1
        name, extension = os.path.splitext(self.file_name)
        len_name = len(name)
        len_ext = len(extension)
        for file_path in self.base_file_set:
            target = os.path.basename(file_path)
            remainder = target[:-(len_ext)][len_name:]
            remainder = strip_version(remainder)
            if remainder > version:
                version = remainder
        return version

    def set_version(self, number):
        """ Set the target version once the user has found out what is
            available.

            If number is >= MAX_VERSION then the actual largest
            version is used.
        """
        if number >= MAX_VERSION:
            self.version = self.get_latest_version()
        else:
            self.version = number

    def get_path(self):
        """ Return the path without the file name.
        """
        if self.full_path == None:
            self._make_path()
        return self.full_path

    def set_from_object(self, nda):
        """ Copy deatails from a ndAttachment object into local variables.
        """
        self.base_location = nda['base_location']
        self.other_location = nda['other_location']
        self.file_name = nda['file_name']
        self.version = strip_version(nda['file_version'])
        self.description = nda['description']
        self.file_version = strip_version(nda['file_version'])
        self.user_name = nda['uploaded_by']
        self.content = nda['content_type']
        self.timestamp = nda['upload_time']
        self.fp = None
        
    def open_file(self):
        if self.fp is not None:
            self.fp.close()
        self.fp = open(self.get_target_path(), 'r')
        return self.fp

    def get_detail_latest(self):
        """ Look in the database for the largest version number.
        """
        nda_fetch = engine.session.query(ndAttachment).filter(
            and_(ndAttachment.base_location == self.base_location,
                 ndAttachment.other_location == self.other_location,
                 ndAttachment.file_name == self.file_name,
                 )).order_by(ndAttachment.file_version.desc())
        nda = nda_fetch.all()
        if len(nda) >= 1:
            self.set_from_object(nda[0])
        else:
            raise AttachmentNotFound, self.file_name
        
    def get_detail(self):
        """ return description, content and user for a given file.
        """
        if self.version != None:
            nda_fetch = engine.session.query(ndAttachment).filter(
                and_(ndAttachment.base_location == self.base_location,
                     ndAttachment.other_location == self.other_location,
                     ndAttachment.file_name == self.file_name,
                     ndAttachment.file_version == make_version(self.version)))
            nda = nda_fetch.all()
            if len(nda) == 1:
                self.set_from_object(nda[0])
            else:
                raise AttachmentNotFound, self.file_name
        else:
            raise AttachmentNotFound, "Must define a version to fetch a file"

    def delete(self):
        """ Delete the file and the database entry for the given
            version.

            No questions asked.
        """
        if self.version != None:
            nda_fetch = engine.session.query(ndAttachment).filter(
                and_(ndAttachment.base_location == self.base_location,
                     ndAttachment.other_location == self.other_location,
                     ndAttachment.file_name == self.file_name,
                     ndAttachment.file_version == make_version(self.version)))
            nda_fetch.delete()
            try:
                os.remove(self.get_target_path())
            except OSError, msg:
                # Ignore files that do not exist
                if "No such file" in str(msg):
                    pass
                else:
                    raise

    def get_target_path(self):
        """ Returns a full path, including file name and version, that
            can be used to store a file or fetch the given version.
        """
        if self.target_path == None:
            self.target_version = self.version
            if self.target_version == None:
                self.target_version = self.get_latest_version() + 1
            name, extension = os.path.splitext(self.file_name)
            self.target_path = os.path.join(
                self.get_path(), "%s%s%s"% (name,
                                            make_version(self.target_version),
                                            extension))
        return self.target_path

    def set_file_source(self, from_file):
        """ Save a source stream in the object so that it can be used
            by self.store when it is called. Allows the processing of
            source stream and store actions to be handled in different
            parts of the application code.
        """
        self.source_stream = from_file

    def store(self, from_file=None):
        """ Put the stuff away in the database. Applies to new
            attachments only.
        """
        local_from_file = from_file or self.source_stream
        assert(local_from_file)
        #
        # Make sure we have a target directory
        self.make_path()
        #
        # Transfer data from source to store
        if not hasattr(local_from_file, 'read'):
            local_from_file = open(from_file, 'r')

        if self.fp is not None:
            self.fp.close()
        self.fp = open(self.get_target_path(), 'w')
        chunk = local_from_file.read(1024 * 1024)
        while chunk:
            self.fp.write(chunk)
            chunk = local_from_file.read(1024 * 1024)
        self.fp.close()
        self.fp = None
        self.flush()

    def make_path(self):
        """ Create all intervening directories
        """
        if not os.path.exists(self.get_path()):
            os.makedirs(self.get_path())
        
    def flush(self):
        """ Update the database after writing a file
        """
        #
        # Make the file look like it is an existing file :-)
        self.version = self.target_version
        #
        # We can store the detail in the database
        nda = ndAttachment()
        nda.base_location = self.base_location
        nda.other_location = self.other_location
        nda.file_name = self.file_name
        nda.file_version = make_version(self.target_version)
        nda.description = self.description
        nda.content_type = self.content
        nda.uploaded_by = self.user_name
        nda.upload_time = self.timestamp
        # Avoid problems if the version file had been previously
        # deleted and left the ndAttachment entry hanging.
        insert_or_update(ndAttachment, nda)
        engine.session.flush()
    

#-----------------------------------------------------------------------

class AttachmentCollection(object):
    """ Get together a set of attachments.

        Limited selection to those for a specific underlying directory.

        Store by filename and version.
    """

    def __init__(self,
                 base_class, base_location, other_location,
                 delay_load=False):
        """
        """
        self.base_location = base_location
        self.other_location = other_location
        self.base_class = base_class
        #
        self.data = {}
        self.length = 0
        if not delay_load:
            nda_fetch = engine.session.query(ndAttachment).filter(
                    and_(ndAttachment.base_location == self.base_location,
                         ndAttachment.other_location == self.other_location))
            nda_all = nda_fetch.all()
            self.length = len(nda_all)
            for nda in nda_all:
                self.put_attachment_detail(nda)

    def put_attachment_detail(self, nda):
        """ Register an attachment
        """
        att = self.base_class(None, None, None)
        att.set_from_object(nda)
        file_name = nda.file_name
        version = nda.file_version
        if not file_name in self.data:
            self.data[file_name] = {version: att}
        else:
            self.data[file_name][version] = att

    def __len__(self):
        return self.length
    
    def __getitem__(self, filename):
        return self.data[filename]

    def __contains__(self, filename):
        return filename in self.data

    def get_in_sequence(self):
        """ Generator for going through in order
        """
        for filename, v_set in sorted(self.data.iteritems()):
            for version, nda in sorted(v_set.iteritems()):
                yield nda

    def delete_data(self):
        """ Go through the attachements, remove from disc and delete
            the table entries.
        """
        for nda in self.get_in_sequence():
            nda.delete()

#-----------------------------------------------------------------------

class NodeAttachmentBase(object):
    """ Provide a specific ID process for nodes.
    """

    def __init__(self):
        self.register_id_process('node', self._usable_sub_directory)
        self.register_path_location('node', self._find_node_path)

    def _find_node_path(self):
        """ Look into the config file for this one.

            Result must exist, and must be a directory.
        """
        root_path = config.get_global_config()['lk_worker']['attachment_path']
        if not os.path.exists(root_path):
            os.makedirs(root_path)
        if not os.path.isdir(root_path):
            raise IOError, (
                "Path %s is not a directory"% os.path.abspath(root_path))
        return root_path
        
    def _usable_sub_directory(self):
        """ Convert 'other_location' into a path.

            This one assumes a storage paradigm for nodes.
        """
        sub_path = os.path.join(self.other_location[:2],
                                self.other_location[2:4],
                                self.other_location[4:6],
                                self.other_location[6:8],
                                self.other_location[8:10])
        return sub_path

#-----------------------------------------------------------------------

class NodeAttachment(Attachment, NodeAttachmentBase):

    def __init__(self, base_location, other_location, filename, **kwargs):

        Attachment.__init__(self,
                            base_location, other_location,
                            filename, **kwargs)
        NodeAttachmentBase.__init__(self)

     #--done
#-----------------------------------------------------------------------

class PiAttachmentData(component.SingletonPlugin):
    """ Link to nde_activity """
    component.implements(IWorkerData, inherit=True)

    def __init__(self):
        self.name = 'attachements'

    def nd_read_data_extend(self, query_result, **kwargs):
        result_map = {}
        if query_result and isinstance(query_result, (list, tuple)):
            nde_idx = query_result[0].nde_idx
            result_map['attachments'] = [
                x for x in
                AttachmentCollection(
                    NodeAttachment, 'node', nde_idx).get_in_sequence()]
        return result_map
    
    def nd_delete_data_extend(self, data_object):
        hist_response = []
        nde_idx = data_object['nd_node']['nde_idx']
        attach_set =  AttachmentCollection(
                NodeAttachment, 'node', nde_idx)
        attach_set.delete_data()
        return hist_response

    def nd_write_data_extend(self, new_data, old_data):
        if 'attachments' in new_data:
            for nda in new_data['attachments']:
                if nda.source_stream:
                    nda.store()
        if 'attachments_to_remove' in new_data:
            for nda in new_data['attachments_to_remove']:
                nda.delete()

#-----------------------------------------------------------------------
