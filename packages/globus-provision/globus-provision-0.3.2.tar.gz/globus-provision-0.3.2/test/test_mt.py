from globus.provision.common.utils import DemoGridThread, MultiThread, SIGINTWatcher, SSH
import sys

class SSHTestThread(DemoGridThread):
    def __init__(self, multi, name, fail = 0, depends = None):
        DemoGridThread.__init__(self, multi, name, depends)
        
    def run2(self):
        ssh_out = sys.stdout
        ssh_err = sys.stderr
        raise Exception("FAIL")
        print "%s - Establishing SSH connection" % self.name
        ssh = SSH("borja", "polaris.cs.uchicago.edu", "/home/borja/.ssh/id_rsa", ssh_out, ssh_err)
        ssh.open()
        print "%s - SSH connection established" % self.name
        
        ssh.run("date; /bin/hostname")
        
def killed():
    print "Killed"
    
SIGINTWatcher(killed) 

mt = MultiThread()

t1 = SSHTestThread(mt, "T1", fail = 0)
t2 = SSHTestThread(mt, "T2", fail = 0)
t3 = SSHTestThread(mt, "T3", fail = 0, depends = t1)

print "foo"
mt.add_thread(t1)
mt.add_thread(t2)
mt.add_thread(t3)
print "bar"        
mt.run()
print mt.all_success()

for th in mt.threads.values():
    print th.name, th.status

