#!/usr/bin/env python2

import optparse, pp

import threading

from gitbox.watchman import WatchLocal, WatchRemote
from gitbox.notify import notify

from Pubnub import Pubnub

def main():
    p = optparse.OptionParser(
        description='GitBox != DropBox',
        prog='gbcli',
        version='gitbox 0.1',
        usage='%prog -n myProject -p ./')


    p.add_option('--id', '-i', dest="pid",  help="the project id")
    p.add_option('--key', '-k', dest="key",  help="your pupnub subscription key")
    p.add_option('--path', '-p', dest="path", help='path to your local git repository')

    options, arguments = p.parse_args()


    if options.pid and options.pid and options.path:
        try:
            wr = WatchRemote(options.pid, options.path, options.key)
            wr= threading.Thread(target=wr.start, args=())
            #wr.setDaemon(True)
            wr.start()
            wl = WatchLocal(options.pid, options.path)
            wl = threading.Thread(target=wl.start, args=())
            #wl.setDaemon(True)
            wl.start()
        except KeyboardInterrupt:
            pass

    else: 
        print p.print_help()

if __name__ == '__main__':
    main()


