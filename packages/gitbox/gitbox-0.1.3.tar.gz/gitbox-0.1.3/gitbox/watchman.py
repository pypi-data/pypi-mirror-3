import os, sys, time, subprocess, threading

from fnmatch import fnmatch
from Queue import Queue

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from notify import notify

from Pubnub import Pubnub


class EventHandler(FileSystemEventHandler):
    def __init__(self, queue):
        self.queue = queue
        self.ignore = ['.*','~*','*.bac']

    def on_any_event(self, event):
        head, tail = os.path.split(event.src_path) 
        match = [fnmatch(tail, p) for p in self.ignore]
        if True not in match and '.git' not in head:
            self.queue.put(tail)


class WatchLocal():
    def __init__(self, pid, path ):
        self.pid = pid
        self.path = path
       
        self.queue = Queue()
        event_handler = EventHandler(self.queue)

        self.observer = Observer()
        self.observer.schedule(event_handler, path, recursive=True)

        # Ensure we do NOT use kqueue on MacOSX.
        if sys.platform.startswith('darwin'):
            for ermitter in self.observer._emitters:
                if ermitter.__class__.__name__ != 'FSEventsEmitter':
                    raise AssertionError, 'Found unsupported observer on MacOSX: ' + ermitter.__class__.__name__

    def get_changes(self):
        files = []
        for i in range(self.queue.qsize()):
            item = self.queue.get() 
            if item not in files:
                files.append(item)  
            self.queue.task_done()
        
        return files

    def start(self):
        notify('GitBox Start', 'monitoring %s' % self.path )
        self.observer.start()
        qsize = self.queue.qsize()
        lastchange = time.time()
        while True:
            if qsize != self.queue.qsize():
                lastchange = time.time()

            if time.time()-lastchange >= 10 and self.queue.qsize() > 0:
                files = self.get_changes()
                notify('GitBox Upload', 'send new and changed files in %' )
                cmd = 'git add .'
                process = subprocess.Popen(cmd.split(' '), cwd=self.path)
                process.communicate()
            
                cmd = 'git commit -am auto-commit'
                process = subprocess.Popen(cmd.split(' '), cwd=self.path)
                process.communicate()
                
                cmd = 'git push'
                process = subprocess.Popen(cmd.split(' '), cwd=self.path)
                process.communicate()
                
            qsize = self.queue.qsize()
            time.sleep(1)


    def stop(self):
        self.observer.stop()
        self.observer.join()



class WatchRemote():
    """monitoring remote repository"""

    def __init__(self, pid, path, key ):
        self.pid = pid
        self.path = path
        self.pubnub = Pubnub( None, key, None, False )

    
    def receive(self,message) :
        notify('GitBox Download', 'receiving new and changed files in %s' % self.path)
        cmd = 'git push'
        process = subprocess.Popen(cmd.split(' '), cwd=self.path)
        process.communicate()
        return True

    def start(self):
        ## Initiat Class
        self.pubnub.subscribe({'channel'  : self.pid, 'callback' : self.receive })

    def stop(self):
        pass
