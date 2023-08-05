import sys, os, os.path

class Mutex():
    def __init__(self):
        self.lockfile = '/tmp/%s' % sys.argv[0].split('/').pop()

    def already_running(self):
        if os.path.exists(self.lockfile):
            oldpid = open(self.lockfile, 'r').read().rstrip()
            if os.path.exists('/proc/%s' % oldpid):
                return True
            else:
                self.remove_lock()
                return False
        else:
            return False
    def create_lock(self):
        lockfile = open(self.lockfile, 'w')
        lockfile.write(str(os.getpid()) + '\n')
        lockfile.close()

    def remove_lock(self):
        os.remove(self.lockfile)#
