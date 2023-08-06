from billiard import Process


class P(Process):

    def run(self):
        for i in xrange(10):
            print("ITER: %r" % (i, ))
            from time import sleep
            sleep(5)
