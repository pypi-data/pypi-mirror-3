import time
from distutils2.version import (NormalizedVersion,
				IrrationalVersionError,
				HugeMajorVersionNumError)
import operator
from .py25compat import next

class VersionManagement(object):
    """
    Version functions for HGRepoManager classes
    """
    
    increment = '0.0.1'

    def get_strict_versions(self):
        """
        Return all version tags that can be represented by a
        StrictVersion.
        """
        for tag in self.get_tags():
            try:
                yield NormalizedVersion(tag.tag)
            except ValueError:
                pass

    def get_tagged_version(self):
        """
        Get the version of the local working set as a NormalizedVersion or
        None if no viable tag exists. If the local working set is itself
        the tagged commit and the tip and there are no local
        modifications, use the tag on the parent changeset.
        """
        tag = self.get_tag()
        if tag == 'tip' and not self.is_modified():
            ptag = self.get_parent_tag('tip')
            if ptag:
                tag = ptag
        try:
            # use 'xxx' because StrictVersion(None) is apparently ok
            return NormalizedVersion(tag or 'xxx')
        except IrrationalVersionError:
            pass

    def get_latest_version(self):
        """
        Determine the latest version ever released of the project in
        the repo (based on tags).
        """
        versions = sorted(self.get_strict_versions(), reverse=True)
        return next(iter(versions), None)

    def get_current_version(self):
        """
        Return as a string the version of the current state of the
        repository -- a tagged version, if present, or the next version
        based on prior tagged releases.
        """
        ver = (
            self.get_tagged_version()
            or str(self.get_dev_version())
            )
        return str(ver)

    def get_dev_version(self):
        """
        Find the most recent tag and a tag distance and build
        a version from this.
        """
	tag, distance = self.get_distance()
	version = "%s.post%s" % (tag, distance)
	if self.is_modified():
	    version = "%s.dev%s" % (version, time.strftime('%Y%m%d'))
	return NormalizedVersion(version)
	

#-----------------------------------------------------------------------
