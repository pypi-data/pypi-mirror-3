#!/usr/bin/env python2

import optparse

from gitbox.watchman import WatchMan

def main():
    p = optparse.OptionParser(
        description='GitBox != DropBox',
        prog='gbcli',
        version='gitbox 0.1',
        usage='%prog -n myProject -p ./')


    p.add_option('--project', '-n', default="NoName Project")
    p.add_option('--path', '-p')

    options, arguments = p.parse_args()

    if not options.path:
        print p.print_help()
    else: 
        try:
            wm = WatchMan(options.project, options.path)
            wm.start()
        except KeyboardInterrupt:
            wm.stop()    

if __name__ == '__main__':
    main()


