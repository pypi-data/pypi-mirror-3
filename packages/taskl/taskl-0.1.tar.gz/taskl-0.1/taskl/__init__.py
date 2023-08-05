import commands.add
import commands.show
import commands.pull
import commands.me
import commands.top

from consoleargs import command

@command(positional=('command',), all_help=False)
def main(command='show', *subargs):

    actions = {
        'show': commands.show.main,
        'add': commands.add.main,
        'pull': commands.pull.main,
        'top': commands.top.main,
        'me': commands.me.main,
    }

    actions[command](*subargs)

if __name__ == "__main__":
    main()
