from os import remove, devnull
from hashlib import md5, sha1
from cutools.vcs import VCSInterface
from cutools.diff import get_chunks
from plumbum.cmd import git
from plumbum.commands import ProcessExecutionError

class Git(VCSInterface):
    """Git implementation for Check Upgrade Tools.
    """
    def __init__(self, upstream):
        self.upstream = upstream

    def get_md5_files(self, files=None):
        res = []
        cmd = git['ls-files', '-m', '-o', '--exclude-standard']
        if files:
            cmd.args += tuple(files)
        files = [x for x in cmd().split('\n') if x]
        for fl in files:
            cmd = git['show', '%s:%s' % (self.upstream, fl)]
            try:
                pymd5 = md5(unicode(cmd()).encode('utf-8')).hexdigest()
                res += [(pymd5, fl)]
            except ProcessExecutionError:
                res += [(' ' * 32, fl)]
                continue
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

    def exists(self, check_file):
        """Check if exists check_file in remote branch.
        """
        try:
            cmd = git['show', '%s:%s' % (self.upstream, check_file)]()
            return True
        except ProcessExecutionError:
            return False

    def is_binary(self, check_file):
        """Hacky version to know if git says if is binary file.
        """
        res = git['diff', '--numstat', devnull, check_file](retcode=(0,1))
        return res.startswith('-\t-\t')

    def get_diff(self, check_file=None, commit=None):
        if check_file:
            if self.exists(check_file):
                if commit:
                    cmd = git['diff', '%s^1..%s' % (commit, commit), check_file]
                else:
                    cmd = git['diff', check_file]
            else:
                cmd = git['diff', devnull, check_file]
        else:
            cmd = git['diff']
        return cmd(retcode=(0,1))

    def get_remote_file(self, check_file):
        return git['show', '%s:%s' % (self.upstream, check_file)]()
