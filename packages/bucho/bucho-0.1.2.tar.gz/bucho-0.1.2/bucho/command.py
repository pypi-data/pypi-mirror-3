import os
import sys
import cmd
import optparse
import bucho
import pkg_resources
from bucho.compat import print_

description = '''
Actions are commands like "show", "latest_status" and "all_status".
If -i is specified or no action is specified on the command line, a
"shell" interpreting actions typed interactively is started. Use the
action "help" to find out about available actions.
'''

bucho_encoding = sys.stdout.encoding
if not bucho_encoding:
    bucho_encoding = 'utf-8'


class BuchoOptions(object):

    def __init__(self):
        programname = os.path.basename(sys.argv[0])
        base, ext = os.path.splitext(programname)
        if ext == ".py":
            if base.endswith('-script'):
                base = base[:-7]
            programname = base
        sys.argv[0] = programname

        usage = 'usage: %prog [options] command'
        parser = optparse.OptionParser(usage=usage, description=description)
        parser.add_option('-i', '--interactive',
                help='start an interactive shell after executing commands',
                dest='interactive',
                action='store_true', default=False)

        parser.add_option('-p', '--prompt',
                help='prompt string',
                dest='prompt',
                action='store', default=(programname+">"))
        parser.add_option('--plugin',
                help='command plugin',
                dest='plugin',
                action='store')
        self.options, self.args = parser.parse_args()


        if not self.args and not self.options.interactive:
            self.options.interactive = 1

    def __getattr__(self, name):
        if hasattr(self.options, name):
            return getattr(self.options, name)
        raise AttributeError(name)

    def __add__(self, obj):
        return obj


class BuchoCmd(cmd.Cmd):

    def __init__(self, options):
        self.options = options
        self.prompt = self.options.prompt + ' '
        if getattr(self.options, 'plugin'):
            cls = self.__class__
            dist = self.options.plugin
            for name, entry_point in pkg_resources.get_entry_map(dist, 'bucho.commands').iteritems():
                setattr(cls, "do_" + name, makeplugincmd(name, entry_point.load()))
                

        cmd.Cmd.__init__(self)

    def do_quit(self, arg):
        return 1

def makeplugincmd(n, func):
    def f(self, arg):
        t = func()
        t = t.encode(bucho_encoding, 'replace')
        t = t.decode(bucho_encoding, 'replace')
        print_(t)
        return 0
    return f
def makecmd(n):
    def f(self, arg):
        t = getattr(bucho, n)()
        t = t.encode(bucho_encoding, 'replace')
        t = t.decode(bucho_encoding, 'replace')
        print_(t)
        return 0
    return f

for name in ['show', 'latest_status', 'all_status', 'torumemo', 'show_gui']:
    setattr(BuchoCmd, "do_" + name, makecmd(name))


def main(options=None, cmdclass=BuchoCmd):
    try:
        if options is None:
            options = BuchoOptions()
        c = cmdclass(options)
    except Exception as e:
        print_(e)
        return

    if options.args:
        c.onecmd(" ".join(options.args))

    if options.interactive:
        try:
            import readline
        except ImportError:
            pass
        c.cmdloop()

def console():
    main()

if __name__ == '__main__':
    main()

