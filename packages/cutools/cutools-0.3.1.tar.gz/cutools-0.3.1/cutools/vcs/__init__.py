from collections import defaultdict

class VCSInterface(object):
    """Interface to create VCS objects to perform an upgrade check.
    """

    def __init__(self, upstrem):
        """Sets the upstream to perform the upgrade check.
        """
        raise NotImplementedError()
    
    def get_md5_files(self):
        """Must return a list of list of tuples with (md5, filename) modified
        in working directory.
        
        [('43f6e228690472109d1c825bdcd1625b', 'README.rst),
         ('3af3d58716ec0776500dc970020a5100', 'src/foo.py)]
        """
        raise NotImplementedError()

    @property
    def local_rev(self):
        """Returns local revision of HEAD.
        """
        raise NotImplementedError()

    @property
    def remote_rev(self):
        """Returns remote revision of HEAD
        """
        raise  NotImplementedError()


    def get_commits(self, check_file, rev_from, rev_to):
        """Returns a list of commits beetwen rev_from and rev_to for check_file
        """
        raise NotImplementedError()

    def get_chunks(self, commit, check_file):
        """Returns the chunks from a commit.
        """
        raise NotImplementedError()

    def get_remote_file(self, check_file):
        """Returns the content of the remote file
        """
        raise NotImplementedError()
