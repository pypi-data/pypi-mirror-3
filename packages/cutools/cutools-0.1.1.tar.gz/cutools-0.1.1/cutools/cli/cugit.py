from hashlib import md5
from subcmd.app import App
from subcmd.decorators import arg
from cutools.vcs.git import Git
from cutools.diff import get_hashed_chunks, clean_chunk, print_diff
from cutools import VERSION
from clint.textui import puts, colored

class CuGitApp(App):
    name = "cugit"
    version = VERSION

    @arg('upstream', help='Upstream branch')
    def do_check(self, options):
        """Checks local modifcations if are in upstream.
        """
        git = Git(options.upstream)
        n_files = 0
        n_chunks = 0
        for pymd5, check_file in git.get_md5_files():
            if md5(open(check_file, 'r').read()).hexdigest() != pymd5:
                local_chunks = get_hashed_chunks(git.get_chunks(check_file))
                rev_from = git.local_rev
                rev_to = git.remote_rev
                for commit in git.get_commits(check_file, rev_from, rev_to):
                    remote_chunks = [
                        md5(unicode(x).encode('utf-8')).hexdigest()
                        for x in git.get_chunks(check_file, commit)
                    ]
                    for lchunk in local_chunks.keys():
                        if lchunk in remote_chunks:
                            del local_chunks[lchunk]
                        else:
                            rfile = git.get_remote_file(check_file)
                            chunk = clean_chunk(local_chunks[lchunk])
                            if rfile.find(chunk) >= 0:
                                del local_chunks[lchunk]
                if local_chunks:
                    n_files += 1
                    for chunk in local_chunks.values():
                        print_diff(chunk)
                        n_chunks += 1
                    puts(colored.red("[x] %s %s" % (pymd5, check_file)))
            else:
                puts(colored.green("[o] %s %s" % (pymd5, check_file)))

app = CuGitApp()
