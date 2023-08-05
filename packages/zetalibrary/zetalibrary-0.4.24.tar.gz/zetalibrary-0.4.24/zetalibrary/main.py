import argparse
import os.path
import sys
import time

from zetalibrary import ZetaError, ZETALIBDIR, VERSION
from zetalibrary.parsers import PARSERS
from zetalibrary.utils import files_changed


COLORS = dict(
    okgreen = '\033[92m',
    warning = '\033[93m',
    fail = '\033[91m',
    endc = '\033[0m',
)


class Linker( object ):
    """ Link js and css files in to one.
    """
    def __init__(self, path, **kwargs):
        self.path = path
        self.no_comments = kwargs.get('no_comments')
        self.prefix = kwargs.get('prefix', '_')
        self.format = kwargs.get('format')

        self.imported = set()
        self.tree = list()
        self.basedir = os.path.abspath( os.path.dirname( path ))
        self.parser = None
        self.parsers = dict((k, p()) for k, p  in PARSERS.items())


    def link( self ):
        """ Parse and save file.
        """
        self.out("Packing '%s'." % self.path)
        self.parse_tree(self.path)
        out = ''
        parent = None
        for item in self.tree:
            current = item.get('current', '').replace(ZETALIBDIR, 'zeta:/')
            src = item['src'].strip()
            if not src:
                continue
            out += "".join([
                self.parser.comment_template % ("=" * 30),
                self.parser.comment_template % "Zeta import: '%s'" % current,
                self.parser.comment_template % "From: '%s'" % parent,
                src,
                "\n\n\n",
            ])
            parent = current

        pack_name = self.prefix + os.path.basename(self.path)
        pack_path = os.path.join(self.basedir, pack_name)

        try:
            open(pack_path, 'w').write(out)
            self.out("Linked file saved as: '%s'." % pack_path)
        except IOError, ex:
            raise ZetaError(ex)

    def parse_tree(self, path):
        """ Parse import structure.
        """
        path = path.strip()
        filetype = os.path.splitext(path)[1][1:] or ''
        try:
            f = self.format or filetype
            self.parser = self.parsers[f.lower()]
        except KeyError:
            raise ZetaError("Unknow format file: '%s'" % path)

        src = self.parser.parse(path, self)
        self.tree.append(dict(src=src, current=path))

    @staticmethod
    def out( message, error=False ):
        """ Out messages.
        """
        pipe = sys.stdout
        alert = ''
        if error:
            pipe = sys.stderr
            alert = '%sError: ' % COLORS['warning']
        pipe.write("\n  *  %s%s\n%s" % (alert,  message, COLORS['endc']))


def get_frameworks():
    path = os.path.join(ZETALIBDIR)
    for fname in os.listdir(path):
        fpath = os.path.join(path, fname)
        if os.path.isfile(fpath):
            description, version = open(fpath).readlines()[1:3]
            yield (fname, version, description)


def get_blocks():
    path = os.path.join(ZETALIBDIR, 'zeta')
    for bname in os.listdir(path):
        bpath = os.path.join(path, bname)
        if os.path.isdir(bpath):
            yield ( bname, '')


def route( path, prefix='_' ):
    """ Route files.
    """
    def test_file( filepath ):
        """ Test file is static and not parsed.
        """
        name, ext = os.path.splitext(os.path.basename(filepath))
        filetype = ext[1:].lower()
        return os.path.isfile(filepath) and not name.startswith(prefix) and filetype in PARSERS.keys()

    if os.path.isdir( path ):
        for name in os.listdir(path):
            filepath = os.path.join(path, name)
            if test_file(filepath):
                yield filepath

    elif test_file(path):
        yield path


def main():
    """ Parse arguments.
    """
    p = argparse.ArgumentParser(
            description="Parse file or dir, import css, js code and save with prefix.")

    p.add_argument('source', help="filename or dirname")

    p.add_argument(
        '-p', '--prefix', default='_', dest='prefix',
        help="Save result with prefix. Default is '_'.")

    p.add_argument(
        '-f', '--format', dest='format', help="Force use this format.")

    p.add_argument(
        '-n', '--no-comments', action='store_true', dest='no_comments',
        help="Clear comments.")

    p.add_argument(
        '-w', '--watch', action='store_true', dest='watch',
        help="Watch directory of file and recompile source if it edited.")

    p.add_argument(
        '-s', '--show-frameworks', action='store_true', dest='frameworks',
        help="Show available frameworks.")

    p.add_argument(
        '-z', '--show-blocks', action='store_true', dest='zeta',
        help="Show available zeta blocks.")

    args = p.parse_args()

    if args.frameworks:
        for framework in get_frameworks():
            sys.stdout.write('%s%s%s %s%s\n' % ( COLORS['okgreen'], framework[0], COLORS['endc'], framework[1], framework[2]))
        sys.exit()

    if args.zeta:
        for block in get_blocks():
            sys.stdout.write('%s%s%s%s\n' % ( COLORS['okgreen'], block[0], COLORS['endc'], block[1],))
        sys.exit()

    try:
        assert os.path.exists(args.source)
    except AssertionError:
        p.error("%s'%s' does not exist.%s" % (args.source, COLORS['fail'], COLORS['endc']))

    routes = list(route(args.source, args.prefix))

    if not args.watch:
        for path in routes:
            try:
                linker = Linker(path, prefix=args.prefix, no_comments=args.no_comments, format=args.format)
                linker.link()
            except ZetaError, ex:
                p.error("%s%s%s" % (ex, COLORS['fail'], COLORS['warning']))

    else:

        if not os.path.exists(args.source):
            p.error("%s%s%s" % ("Path don't exist: %s" % args.source, COLORS['fail'], COLORS['warning']))
            sys.exit(1)

        print 'Zeta-library v. %s watch mode' % VERSION
        print '================================'
        print 'Ctrl+C for exit\n'
        while True:
            try:
                if files_changed(args.source, args.prefix):
                    for path in routes:
                        linker = Linker(path, prefix=args.prefix, no_comments=args.no_comments, format=args.format)
                        linker.link()
                time.sleep(.2)
            except ZetaError, ex:
                p.error("%s%s%s" % (ex, COLORS['fail'], COLORS['warning']))
            except OSError:
                pass
            except KeyboardInterrupt:
                print "\nWatch mode stoped."
                break
