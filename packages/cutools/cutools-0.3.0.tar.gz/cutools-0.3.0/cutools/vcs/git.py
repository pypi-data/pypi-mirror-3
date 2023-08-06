from hashlib import md5
from cutools.vcs import VCSInterface
from cutools.diff import get_chunks
from plumbum.cmd import git

class Git(VCSInterface):
    """Git implementation for Check Upgrade Tools.
    """
    def __init__(self, upstream):
        self.upstream = upstream

    def get_md5_files(self):
        res = []
        files = ['%s' % x for x in git['ls-files', '-m']().split('\n') if x]
        for fl in files:
            cmd = git['show', '%s:%s' % (self.upstream, fl)]
            pymd5 = md5(unicode(cmd()).encode('utf-8')).hexdigest()
            res += [(pymd5, fl)]
        return res

    def fetch(self, remote=None):
        if not remote:
            remote = self.upstream.split('/')[0]
        git['fetch', remote]()

    def checkout(self, check_file):
        git['checkout', '--', check_file]()

    def merge(self, upstream=None):
        if not upstream:
            upstream = self.upstream
        if '/' in upstream:
            self.fetch(upstream.split('/')[0])
        git['reset', '--hard', self.local_rev]()
        git['merge', upstream]()

    def apply_diff(self, diff):
        """Apply diff text.
        """
        patch_file = write_tmp_patch(diff)
        self.apply_patch(patch_file)
        remove(patch_file)

    def apply_patch(self, patch_file):
        """Apply patch file.
        """
        git['apply', patch_file]()

    @property
    def local_rev(self):
        return git['rev-parse', 'HEAD']().strip()

    @property
    def remote_rev(self):
        return git['rev-parse', self.upstream]().strip()

    def get_commits(self, check_file, rev_from, rev_to):
        hcommand = git['log', '--no-merges', '--pretty=oneline',
                           '%s..%s' % (rev_from, rev_to),
                           check_file]
        return [x.split(' ')[0] for x in hcommand().split('\n') if x]

    def get_chunks(self, check_file, commit=None):
        return get_chunks(self.get_diff(check_file, commit))

    def get_diff(self, check_file=None, commit=None):
        if check_file:
            if commit:
                cmd = git['diff', '%s^1..%s' % (commit, commit), check_file]
            else:
                cmd = git['diff', check_file]
        else:
            cmd = git['diff']
        return cmd()

    def get_remote_file(self, check_file):
        return git['show', '%s:%s' % (self.upstream, check_file)]()
