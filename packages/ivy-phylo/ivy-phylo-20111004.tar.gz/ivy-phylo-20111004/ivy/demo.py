import sys
from IPython.demo import IPythonDemo, ClearIPDemo
from IPython.genutils import Term
from time import sleep
from random import random

class Demo(ClearIPDemo):
    def show(self,index=None):
        """Show a single block on screen"""

        index = self._get_index(index)
        if index is None:
            return

        if self.speed:
            for c in self.src_blocks_colored[index]:
                Term.cout.write(c)
                sleep(random()*0.1*(1.0/self.speed))
                sys.stdout.flush()
        else:
            print >> Term.cout, self.src_blocks_colored[index]
            sys.stdout.flush()

        s = "Hit <Enter>, then type %next to proceed or %back to go back one step."
        print >> Term.cout, s
        sys.stdout.flush()
    

def demo(src, speed=1):
    __demo__ = Demo(src)
    __demo__.speed = speed
    def n(*args): __demo__()
    def b(*args):
        __demo__.back(2)
        __demo__()
    import IPython.ipapi
    ip = IPython.ipapi.get()
    ip.expose_magic('n', n)
    ip.expose_magic('next', n)
    ip.expose_magic('b', b)
    ip.expose_magic('back', b)
    __demo__()
