import sys

if sys.platform.startswith('linux'): 
    from pynotify import init, Notification
    init("GitBox")
elif sys.platform.startswith('darwin'):
    from subprocess import Popen, PIPE

def notify(title, msg='', msgtype="info", timeout=10000):
    print title + ': ' + msg
    if sys.platform.startswith('linux'): 
        n = Notification(title, msg)
        n.set_timeout(timeout)
        return n.show()

    elif sys.platform.startswith('darwin'):
        args = ['growlnotify']
        args.append('-t')
        args.append(title)
        args.append('-m')
        args.append(msg)
        # TODO change icon of growl notify message!
#        args.append('--iconpath')
#        args.append('icon.png')
        process = Popen(args, stdout=PIPE, stderr=PIPE)
        process.wait()
        return process.returncode == 0

    else:
        print title + ': ' + msg
        return False
