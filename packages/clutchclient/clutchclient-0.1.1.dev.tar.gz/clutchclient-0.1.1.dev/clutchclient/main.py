import sys

from clutchclient import commands

COMMANDS = ['dev', 'upload', 'startapp', 'startscreen']

def main():
    namespace, extra = commands.PARSER.parse_known_args()
    if namespace.command not in COMMANDS:
        print >> sys.stderr, 'Invalid command specified, here are the available commands:'
        for command in COMMANDS:
            print >> sys.stderr, ' * ' + command
        sys.exit(1)
    
    getattr(commands, namespace.command)(namespace, extra)

if __name__ == '__main__':
    main()