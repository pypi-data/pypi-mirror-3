# Name:      lokai/tool_box/tb_common/helpers.py
# Purpose:   General stuff to assist testing
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
import unittest
import os
import optparse
import subprocess

import lokai.tool_box.tb_common.configuration as config
import lokai.tool_box.tb_common.notification as notify

#-----------------------------------------------------------------------
def do_command(list):
    #
    # Execute a command in a shell
    #
    # Return the complete output of the command, just in case it
    # contains anything that can be used by the caller.
    
    p = subprocess.Popen(list,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    f = p.stdout
    op = []
    l = f.readline()
    op.append(l)
    while l:
        ##print l
        l = f.readline()
        op.append(l)

    return ''.join(op)

#-----------------------------------------------------------------------

def compare_dict_base(a, b):
    #
    # Compare two dictionaries for matching keys only.
    resp = []
    bk_set = b.keys()
    for ak,av in a.iteritems():
        if ak in bk_set:
            bv = b[ak]
            if av != bv:
                #
                # Try boolean
                if type(av) == type(' '):
                    if av.upper() in 'YES':
                        av = True
                    elif av.upper() in 'NO':
                        av = False
                if type(bv) == type(' '):
                    if bv.upper() in 'YES':
                        bv = True
                    elif bv.upper() in 'NO':
                        bv = False
                if av != bv:
                    resp.append("Fail to match key %s, %s != %s" %
                                (ak, str(a[ak]), str(b[ak])))
        else:
            resp.append("%s not found in %s" % (ak, bk_set))
    return resp

#-----------------------------------------------------------------------

def compare_dict(a, b):
    #
    # Compare two dictionaries exactly.
    ak = a.keys()
    bk = b.keys()
    if len(ak) != len(bk):
        ak.sort()
        bk.sort()
        return 'Key set %s != key set %s' % (ak, bk)
    return compare_dict_base(a, b)

#-----------------------------------------------------------------------

def compare_dict_2(a, b):
    #
    # Compare two dictionaries for shortest set of matching keys only.
    ak = a.keys()
    bk = b.keys()
    if len(ak) < len(bk):
        return compare_dict_base(a, b)
    else:
        return compare_dict_base(b, a)
#-----------------------------------------------------------------------

def compare_files(f1, f2):

    f1h = open(f1, 'r')
    f2h = open(f2, 'r')

    chunk = 1024
    f1c = f1h.readline()
    f2c = f2h.readline()
    while f1c or f2c:
        if f1c.strip() != f2c.strip():
            return False
        f1c = f1h.readline()
        f2c = f2h.readline()
    return True

#-----------------------------------------------------------------------
def compare_file_first_line(file1, string):
    if hasattr(file1, 'readline') :
        filehandler = file1
    else:
        filehandler = open(file1 , 'r')
    line1 = filehandler.readline()
    #print line1
    #print string
    if line1.strip() != string.strip():
        return (False, line1.strip())
    else:
        return (True, line1.strip())

#-----------------------------------------------------------------------

def repo(dict):

    op = []
    pfx = "{"
    k_set = dict.keys()
    k_set.sort()
    for k in k_set:
        op.append("%s%s: %s"%(pfx, str(k), str(dict[k])))
        pfx = " "
    op.append("}")
    return '\n'.join(op)

#-----------------------------------------------------------------------

class TestAccessNotSupported(Exception):

    pass


def check_tests_allowed():

    try:
        status = config.get_global_config()['all']['site_status']
    except KeyError:
        raise TestAccessNotSupported(
            "parameter setting 'site_status' not found in section 'all'")
    if status != 'test_database-items_may_be_deleted':
        raise TestAccessNotSupported(
            "Not possible to work under these conditions.\n"
            "The configuration file is not marked as a test configuration\n"
            "site status has the value %s")%str(status)

#-----------------------------------------------------------------------

def options_for_publish():
    """ Read command line options for testing
    """
    usage = ("usage: %prog [options] [test list]\n\n"
              "    [test list] is an optional list of test names")
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-v", "--verbose",
                  action="count", dest="verbose",
                  help="Increase the verbosity of the code being tested")

    parser.add_option("-r", "--reporting",
                  action="count", dest="reporting",
                  help="Increase the verbosity of the test report")

    return parser.parse_args()

def logging_for_publish(options):
    """ Initialise logging
    """
    import logging
    log_level = {1:logging.WARNING,
                 2:logging.INFO,
                 3:logging.DEBUG
                 }
    notify.setLogName(
        os.path.splitext(
        os.path.basename(sys.argv[0]))[0])
    logging.basicConfig(level=log_level.get(min(options.verbose, 3),
                                            logging.ERROR))

    
def publish(options, test_set, *target_test_objects):
    """ Publish one or more test obects to the command line.

        A set of test names on the command line will execute only
        those tests from the given test objects.

        Logging is supported as the output method. This is nowhere
        near as sophisticated as nosetests, but it does provide the
        selecti-test-from-command-line option.
    """

    if len(target_test_objects) == 1 and len(test_set) > 0:
        suite = unittest.TestSuite()
        for tt in test_set:
            suite.addTest(target_test_objects[0]("test_%s"%tt))
    else:
        suite_set = []
        for k in target_test_objects:
            if not isinstance(k, unittest.TestSuite):
                k = unittest.makeSuite(k)
            suite_set.append(k)
        suite = unittest.TestSuite(suite_set)
    reporting = 2
    if options.reporting:
        reporting = options.reporting
    unittest.TextTestRunner(verbosity = reporting).run(suite)

#-----------------------------------------------------------------------

def can_remove_root(top):
    """ Test to see if we are allowed to remove this directory.

        The directory must be in or under the current working
        directory. If it isn't then there is a possibility we are
        deleting something strange. This is for use in a test
        environment, after all.
        
    """
    if top[0] == '/':
        # do not allow absolute paths - too dangerous
        raise SystemExit, (
            "Try to delete absolute path %s"% top)
    cwd = os.getcwd()
    tgt = os.path.abspath(os.path.expanduser(top))
    upper = os.path.dirname(tgt)
    if not cwd == os.path.commonprefix([cwd, upper]):
        raise SystemExit, (
            "Path %s is not under %s"% (tgt, cwd))
    return True

def remove_root(top):
    local_top = os.path.expanduser(top)
    if os.path.exists(local_top) and can_remove_root(local_top):
        if not os.path.isdir(local_top):
            raise SystemExit, (
                "Path %s is not a directory"% os.path.abspath(local_top))
        for root, dirs, files in os.walk(local_top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(local_top)

def make_root(top):
    if not os.path.exists(top):
        os.makedirs(os.path.abspath(os.path.expanduser(top)))


#-----------------------------------------------------------------------
