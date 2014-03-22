#!/usr/bin/env python
from errno import EEXIST, ENOENT
from os import listdir, makedirs, path, remove, rename, symlink
from socket import gethostname

# TODO write README
# TODO are the links not full paths?

class Linker(object):
    def __init__(self, target=None, exclude_common=False, delete_existing=False,
                 dry_run=False, verbose=False, interactive=False):
        self.target = target or path.dirname(__file__)
        self.exclude_common = exclude_common
        self.delete_existing = delete_existing
        self.dry_run = dry_run
        self.verbose = verbose
        self.interactive = interactive

        # TODO implement interactive mode to approve individual links
        if self.interactive: raise NotImplementedError

        if self.dry_run:
            self.verbose = True
            print """
THIS IS A DRY RUN
NOTHING WILL ACTUALLY BE CREATED / DESTROYED / MOVED
"""

    def fetch_file_list(self, dirname):
        try:
            return [f for f in listdir(dirname) if not f.startswith('.') and \
                    not f.endswith('.dontlink')]
        except OSError as e:
            if e.errno == ENOENT:
                return []
            else:
                raise

    def find_files(self, target):
        files = self.fetch_file_list(path.join(target, gethostname()))
        if not self.exclude_common:
            files += self.fetch_file_list(path.join(target, 'common'))
        return files

    def mkdir_p(self, path):
        try:
            makedirs(path)
        except OSError as e:
            if e.errno == EEXIST and path.isdir(path):
                pass
            else:
                raise

    def make_links(self, files=None):
        if files is None:
            files = self.find_files(self.target)

        errors = []
        for target in files:
            link = target.replace('_', '/')
            if self.verbose:
                print "linking %s to %s" % (target, link)

            directory = path.dirname(link)
            if not path.exists(directory):
                if self.verbose:
                    print "directory %s doesn't exist... creating it" % \
                    directory
                if not self.dry_run:
                    mkdir_p(directory)

            try:
                if path.exists(link) and not path.islink(link):
                    if self.verbose:
                        print "%s already exists... " % link,
                    if self.delete_existing:
                        if self.verbose:
                            print "deleting"
                        if not self.dry_run:
                            remove(link)
                    else:
                        if self.verbose:
                            print "moving to %s.back" % link
                        if not self.dry_run:
                            rename(link, link + '.back')
                if not self.dry_run:
                    symlink(target, link)
            except OSError:
                errors.append("linking %s failed" % link)

        if errors:
            print "failed to make some links\n%s\nmaybe you need `sudo !!`" % \
            "\n".join(errors)

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('--interactive', '-i', help="Prompt for all changes",
                      dest='interactive', action='store_true')
    parser.add_option('--verbose', '-v', help="Print all changes",
                      dest='verbose', action='store_true')
    parser.add_option('--dry-run', '-d',
                      help="Print all changes, but DON'T DO THEM",
                      dest='dry_run', action='store_true')
    parser.add_option('--target-dir', '-t',
                       help="target directory (where to start)", dest='target')
    parser.add_option('--exclude-common', '-x', dest='exclude_common',
                      action='store_true',
                      help=("default is to link files in `hostname` and "
                            "'common' dirs. this will only link `hostname`"))
    parser.add_option('--delete-existing', dest='delete_existing',
                      action='store_true',
                      help=("delete existing files instead of moving them to "
                            "original_name.back"))
    (opts, args) = parser.parse_args()

    linker = Linker(target=opts.target, exclude_common=opts.exclude_common,
                    delete_existing=opts.delete_existing, dry_run=opts.dry_run,
                    verbose=opts.verbose, interactive=opts.interactive)
    linker.make_links()
