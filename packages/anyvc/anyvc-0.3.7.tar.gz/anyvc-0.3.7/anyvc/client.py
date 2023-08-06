# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
"""
    Command line client for anyvc.

    :license: LGPL2 or later
    :copyright:
        * (c) 2008 Ali Afshar <aafshar@gmail.com>
        * (c) 2008 Ronny Pfannschmidt <Ronny.Pfannschmidt@gmx.de>
"""


import os, sys, logging

from optparse import OptionParser

from py.io import TerminalWriter

# XXX Translations
_ = lambda s: s

from . import workdir


def create_option_parser():
    usage = "usage: %prog [options] <command> [args ...]"

    parser = OptionParser(usage)

    # General options
    parser.add_option('-d', '--working-directory', dest='working_directory',
                      help='The working directory')
    parser.add_option('-r', '--revision', dest='revision',
                      help='The revision id')

    # List options
    parser.add_option('-a', '--list-all', dest='list_all',
                      action='store_true', help='List all files.')
    parser.add_option('-m', '--message', dest='commit_message',
                     action='store', help='The commit message')
    parser.add_option('-U', '--hide-unknown', dest='hide_unknown',
                      action='store_true', help='Hide unknown files')
    parser.add_option('-u', '--list-unchanged', dest='list_unchanged',
                      action='store_true', help='List unchanged files.')
    parser.add_option('-i', '--list-ignored', dest='list_ignored',
                      action='store_true', help='List ignored files.')
    parser.add_option('-n', '--list-nonrecursive', dest='list_nonrecursive',
                      action='store_true',
                      help='Only list files in the current working directory.')
    parser.add_option('-c', '--no-color', dest='no_color',
                       action='store_true',
                       help='Uncoloured terminal list output')

    # Miscellaneous options
    parser.add_option('-v', '--verbose', action="store_true", dest="verbose",
                      help='Show debugging information')
    return parser


def setup_logger(verbose):
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level, stream=sys.stderr, format='%(levelname)s: %(message)s')


list_letters = {
    'clean': '-',
    'unknown': '?',
    'modified': 'M',
    'added': 'A',
    'removed': 'D',
    'deleted': '!',
    'ignored': 'I',
}

list_colors = {
    'clean': None,
    'unknown': '*teal*',
    'modified': 'red',
    'added': 'blue',
    'removed': 'fuscia',
    'deleted': 'yellow',
    'ignored': 'turquoise',
}


def do_status(vc, opts, args):
    tw = TerminalWriter()

    def output_state(st):
        output = list_letters.get(st.state, '*').ljust(2)
        color = list_colors.get(st.state)
        tw.write(output, bold=True, **{color:True, })
        tw.line(st.relpath)

    hidden_states = []

    if not opts.list_all:

        if not opts.list_unchanged:
            hidden_states.append('clean')

        if not opts.list_ignored:
            hidden_states.append('ignored')

        if opts.hide_unknown:
            hidden_states.append('unknown')

    for st in vc.status(recursive=not opts.list_nonrecursive):
        if st.state not in hidden_states:
            output_state(st)

    return 0


def do_diff(vc, opts, args):
    tw = TerminalWriter()
    paths = tuple(args)
    diff = vc.diff(paths=paths).strip()
    for line in diff.splitlines():
        kw=dict(
            red=line[0] == '-',
            green=line[0] == '+',
            bold=line.split(' ', 1)[0] in ('diff','+++', '---'),
        )
        tw.line(line, **kw)


def do_commit(vc, opts, args):
    out = vc.commit(
        message=opts.commit_message,
        paths=args)
    sys.stdout.write(out)
    sys.stdout.flush()

def do_add(vc, opts, args):
    out = vc.add(paths=args)
    sys.stdout.write(out)
    sys.stdout.flush()


def do_push(vc, opts, args):
    repo = vc.repository
    if repo is None:
        print >> sys.stderr, "cant find local repo to push from"

    if not repo.local:
        #XXX: better handling
        print >> sys.stderr, "can't push from a non-local", repo.__class__.__name__
        exit(1)
    location = args[0] if args else None
    print repo.push(location, opts.revision)


# The available commands
#XXX: needs a better abstraction
commands = {
    'add': do_add,
    'status': do_status,
    'st': do_status,
    'diff': do_diff,
    'commit': do_commit,
    'ci': do_commit,
    'push': do_push,
}


def main(argv=sys.argv):
    parser = create_option_parser()
    opts, args = parser.parse_args(argv)

    setup_logger(opts.verbose)

    if opts.working_directory is None:
        cwd = os.getcwd()
    else:
        cwd = opts.working_directory

    logging.debug('Using working directory: %s' % cwd)

    vc = workdir.open(cwd)

    if vc is None:
        logging.error(_('Cannot detect version control system in %(cwd)s' %
                        {'cwd': cwd}))
        return -1

    logging.debug('Found VC: %s' % vc)

    pargs = args[:]
    called = pargs.pop(0)

    try:
        command = pargs.pop(0)
    except IndexError:
        logging.error(_('You must provide a command.'))
        logging.info(_('The available commands are: %(commands)s' %
                        {'commands': '%s' % ', '.join(commands.keys())}))
        parser.print_usage()
        return -1

    try:
        action = commands[command]
    except KeyError:
        logging.error(_('The command "%(command)s" is not available.' %
                        {'command': command}))
        logging.info(_('The available commands are: %(commands)s' %
                        {'commands': ', '.join(sorted(commands.keys()))}))
        return -1

    logging.debug('Calling %s' % command)

    return action(vc, opts, pargs)

