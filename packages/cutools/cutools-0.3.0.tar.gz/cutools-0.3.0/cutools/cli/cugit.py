import os
import sys
from hashlib import md5
from tempfile import mkstemp
from subcmd.app import App
from subcmd.decorators import arg, option
from cutools.vcs.git import Git
from cutools.diff import get_hashed_chunks, clean_chunk, get_chunks
from cutools.diff import print_diff, header_diff
from cutools.diff import write_tmp_patch
from cutools import VERSION
from clint.textui import puts, colored
from clint.textui.prompt import yn


class CuGitApp(App):
    name = "cugit"
    version = VERSION

    @arg('upstream', help='Upstream branch')
    @option('--diff', action='store_true', default=False,
            help="Show the diff (default: %(default)s)")
    def do_check(self, options):
        """Checks local modifcations if are in upstream.
        """
        git = Git(options.upstream)
        git.fetch()
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
                    n_chunks += len(local_chunks.values())
                    puts(colored.red("FAIL %s %s" % (pymd5, check_file)))
                    if options.diff:
                        for chunk in local_chunks.values():
                            print_diff(chunk)
                else:
                 puts(colored.green("OK %s %s" % (pymd5, check_file)))
            else:
                puts(colored.green("OK %s %s" % (pymd5, check_file)))

    @arg('upstream', help='Upstream branch')
    def do_diff(self, options):
        """Print the diff to apply after the upgrade.
        """
        git = Git(options.upstream)
        git.fetch()
        diffs = []
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
                    diff = git.get_diff(check_file)
                    diffs.append((check_file, diff))
                    print_diff(diff)
        return diffs

    @arg('upstream', help='Upstream branch')
    @option('--interactive', action='store_true', default=False,
            help="Interactive mode (default: %(default)s)")
    def do_upgrade(self, options):
        git = Git(options.upstream)
        puts("Making a savepoint... ", newline=False)
        savepoint = git.savepoint()
        puts("Savepoint id: %s" % savepoint)
        try:
            diff_files = self.do_diff(options)
            diff_to_apply = []
            for check_file, diff in diff_files:
                header = header_diff(diff)
                for chunk in get_chunks(diff):
                    diff_to_apply.append(header + chunk)
                git.checkout(check_file)
            if git.local_rev == git.remote_rev:
                puts("Already up-to-date.")
            else:
                puts("Merging %s %s..%s " %
                     (options.upstream, git.local_rev[:7], git.remote_rev[:7]),
                     newline=False)
                git.merge()
                puts("Done!")
            if not diff_to_apply:
                puts("Nothing to apply.")
                sys.exit(0)
            puts("Applying patches...")
            for to_apply in diff_to_apply:
                print_diff(to_apply)
                apply = yn('Apply?')
                if not apply:
                    patch_file = write_tmp_patch(to_apply)
                    puts(colored.yellow("Skipped patch. Saved to %s"
                                        % patch_file))
                    continue
                git.apply_diff(to_apply)
        except (KeyboardInterrupt, Exception) as e:
            puts(colored.red(str(e)))
            # If anything goes wrong rollback to rescue!
            puts("Restoring savepoint %s " % savepoint, newline=False)
            git.restore(savepoint.identity)
            puts("Done!")


app = CuGitApp()
