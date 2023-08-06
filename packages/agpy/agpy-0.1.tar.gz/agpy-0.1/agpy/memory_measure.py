import psi
import os

def print_memory(func):
    def wrapper(*arg,**kwargs):
        p = psi.process.Process(os.getpid())
        mem1 = p.rss
        print "Memory usage before program is %g MB" % (mem1 / 1024.**2)
        res = func(*arg,**kwargs)
        mem2 = p.rss
        print "Memory usage after program is %g MB" % (mem2 / 1024.**2)
        print "Difference is %g MB" % ((mem2-mem1) / 1024.**2)
        return res
    return wrapper

