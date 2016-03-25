import math
import numpy
import random
import neurolab as nl

def main():
    net = nl.net.newff([[-10.0, 10.0]], [10, 1])
    net.trainf = nl.train.train_gdx

    print net.step([1.0])
    print net.step([1.0])

    for i in xrange(100000):
        net.train([[1.0], [2.0], [3.0], [4.0]], [[math.sin(1.0)], [math.sin(2.0)], [math.sin(3.0)], [math.sin(4.0)]], epochs=1, adapt=True, show=None, goal=0.0)

    print net.step([1.0])

main()
