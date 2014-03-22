#!/usr/bin/env python
from optparse import OptionParser
from os import listdir, path, remove, rename, symlink
from socket import gethostname

# TODO write README

def fetch_file_list(dirname):
    return [f for f in listdir(dirname) if not f.startswith('.') and \
            not f.endswith('.dontlink')]

def find_files(target):
    files = fetch_file_list(path.join(target, gethostname()))
    if not opts.exclude_common:
        files += fetch_file_list(path.join(target, 'common'))
    return files

def make_links(files):
    errors = []
    for target in files:
        link = target.replace('_', '/')
        if opts.verbose:
            print "linking %s to %s" % (target, link)

        try:
            # TODO create missing dirs
            if path.exists(link) and not path.islink(link):
                if opts.verbose:
                    print "%s already exists... " % link,
                if opts.delete_existing:
                    if opts.verbose:
                        print "deleting"
                    if not opts.dry_run:
                        remove(link)
                else:
                    if opts.verbose:
                        print "moving to %s.back" % link
                    if not opts.dry_run:
                        rename(link, link + '.back')
            if not opts.dry_run:
                symlink(target, link)
        except OSError:
            errors.append("linking %s failed" % link)

    if errors:
        print "failed to make some links\n%s\nmaybe you need to `sudo !!`" % \
        "\n".join(errors)
                    
def get_opts():
    usage = "usage: %prog [options]"

    parser = OptionParser(usage=usage)
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
    # TODO implement interactive mode to approve individual links
    if opts.interactive: raise NotImplementedError
    return opts

def main():
    if opts.dry_run:
        opts.verbose = True
        print """
THIS IS A DRY RUN
NOTHING WILL ACTUALLY BE CREATED / DESTROYED / MOVED
"""

    make_links(find_files(opts.target or path.abspath('.')))

if __name__ == '__main__':
    opts = get_opts()
    main()
