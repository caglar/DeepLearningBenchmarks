import time
import socket
import numpy as np
import math

from theano import config

#Emulate the C-like enums in python
class RunMode(object):
    FLOAT_32 = "float_32"
    FLOAT_64 = "float_64"
    GPU = "gpu"


"""
Just a basic enum-like class for storing the algorithms
"""
class Algorithms(object):
    MLP = 1
    CONVNET = 2
    RBM = 3
    AA = 4

class ExecutionTimes(object):
    expected_times_64 = None
    expected_times_32 = None
    expected_times_gpu = None

    #Recalculate the expected times for the array.
    def __init__(self):
        self.algo = ['logistic_sgd',
            'logistic_cg',
            'mlp',
            'convolutional_mlp',
            'dA',
            'SdA',
            'DBN',
            'rbm',
            'aa'
            ]

        to_exec = [False] * len(self.algo)
        to_exec[2] = True #enable mlp
        to_exec[3] = True #enable covnet
        to_exec[7] = True #enable rbm

        #Timing expected are from the buildbot that have
        # an i7-920 @ 2.67GHz with hyperthread enabled for the cpu
        # and an GeForce GTX 285 for the GPU.

        self.expected_times_64 = np.array([10.7, 23.7, 84.8, 74.9, 124.6,
                                           384.9, 414.6, 558.1])
        self.expected_times_32 = np.array([9.8, 25.1, 56.7, 66.5, 85.4,
                                       211.0, 245.7, 432.8])
        # Number with just 1 decimal are new value that are faster with
        # the Theano version 0.5rc2 Other number are older. They are not
        # updated, as we where faster in the past!
        # TODO: find why and fix this!

        # Here is the value for the buildbot on February 3th 2012.
        #              sgd,         cg           mlp          conv        da
        #              sda          dbn          rbm
        #    gpu times[3.72957802,  9.94316864,  29.1772666,  9.13857198, 25.91144657,
        #              18.30802011, 53.38651466, 285.41386175]
        #    expected [3.076634879, 7.555234910, 18.99226785, 9.58915591, 24.130070450,
        #              24.77524018, 92.66246653, 322.340329170]
        #              sgd,         cg           mlp          conv        da
        #              sda          dbn          rbm
        #expected/get [0.82492841,  0.75984178,  0.65092691,  1.04930573, 0.93125138
        #              1.35324519 1.7356905   1.12937868]
        self.expected_times_gpu = np.array([3.07663488, 7.55523491, 18.99226785,
                                        9.1, 24.13007045,
                                        18.3,  53.4, 285.4])

        self.expected_times_64 = [s for idx, s in enumerate(self.expected_times_64)
                         if to_exec[idx]]
        self.expected_times_32 = [s for idx, s in enumerate(self.expected_times_32)
                         if to_exec[idx]]
        self.expected_times_gpu = [s for idx, s in enumerate(self.expected_times_gpu)
                          if to_exec[idx]]

    def get_expected_times(self):
        return (self.expected_times_32, self.expected_times_64, self.expected_times_gpu)

class StopWatch(object):
    def __init__(self):
        self._delta = 0
        self._start = 0
        self._end = 0

    def start(self):
        self._start = time.time()
    
    def stop(self):
        self._end = time.time()
        self._delta = self._end - self._start
        return self._delta

    def get_elapsed_time(self):
        return self._delta



"""
    A general class that measures the time for given theano function.
"""
class BenchmarkReporter(object):

    def __init__(self, num_examples=0, batch_size=0, batch_flag=False,
         algo=Algorithms.MLP, niter=2, n_in=1024, n_out=1024):
        self.num_examples = num_examples 
        self.batch_size = batch_size
        self.stop_watch = StopWatch()
        self.batch_flag = batch_flag
        self.algorithm = algo
        self.niter = niter
        self.n_in = n_in
        self.n_out = n_out
        self.speeds = {
            (RunMode.FLOAT_64 + "_times"):[],
            (RunMode.FLOAT_64 + "_times"):[],
            (RunMode.GPU + "_times"):[]
        }
    
    def _bmark_name(self, name):
        return open("outs/%s%s_%s_%s.bmark" % (socket.gethostname(), name,
            config.device, config.floatX), 'w')

    def get_bmark_name(self):
        if self.algorithm == Algorithms.MLP:
            return self._bmark_name("mlp")
        if self.algorithm == Algorithms.CONVNET:
            return self._bmark_name("convnet")
        if self.algorithm == Algorithms.RBM:
            return self._bmark_name("rbm")

    def add_speed(self, time):
        mode = self.get_mode()
        self.speeds[mode + "_times"].append(time)

    def get_speeds(self):
        mode = self.get_mode()
        return self.speeds[mode + "_times"]

    def eval_model(self, train, name):
        if self.algorithm == Algorithms.MLP:
            self._eval_model_mlp(train, name)
        if self.algorithm == Algorithms.CONVNET:
            self._eval_model_convnet(train, name)
        if self.algorithm == Algorithms.RBM:
            self._eval_model_rbm(train, name)

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    def _eval_model_mlp(self, train, mode, name):
        bmark = self.get_bmark_name()
=======
=======
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.
=======
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.
    def simple_eval_model(self, train, name):
        bmark = self.get_bmark_name(name)
        self.stop_watch.start()
        train.fn(n_calls=self.num_examples)
        time = self.stop_watch.stop()
        self.add_speed(time)
        self._report_model(name, self.batch_size, self.stop_watch.stop(),
                bmark)

    def _eval_model_mlp(self, train, name):
        bmark = self.get_bmark_name(name)
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.
        if self.batch_flag:
            self.stop_watch.start()
            for i in xrange(self.num_examples):
                cost = train(i * self.batch_size, self.batch_size)
            time = self.stop_watch.stop()
            self.add_speed(time)
            self._report_model(name, self.batch_size, time, bmark)
        else:
            self.stop_watch.start()
            minibatch_size = math.ceil(self.num_examples / self.batch_size)
            for i in xrange(minibatch_size):
                cost = train(i * self.batch_size, self.batch_size)
                if not (i % 20):
                    print i * self.batch_size, cost
            time = self.stop_watch.stop()
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
            self.add_speed(time, mode)
            self._report_model(name, self.batch_size, self.stop_watch.stop(), mode, bmark)
=======
            self.add_speed(time)
            self._report_model(name, self.batch_size, self.stop_watch.stop(),
                    bmark)
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.
=======
            self.add_speed(time)
            self._report_model(name, self.batch_size, self.stop_watch.stop(),
                    bmark)
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.
=======
            self.add_speed(time)
            self._report_model(name, self.batch_size, self.stop_watch.stop(),
                    bmark)
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.

    def _eval_model_convnet(self, train, name):
        assert self.num_examples % self.batch_size
        bmark = self.get_bmark_name()
        self.stop_watch.start()
        minibatch_size = math.ceil(self.num_examples / self.batch_size)
        for i in xrange(minibatch_size):
            cost = train(i * self.batch_size, self.batch_size)
            if not (i % (1000 / self.batch_size)):
                print i * self.batch_size, cost
        elapsed_time = self.stop_watch.stop()
        self.add_speed(elapsed_time)
        expsec = self.num_examples / time
        self._report_model(name, self.batch_size, expsec, bmark)

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    def _eval_model_rbm(self, train, mode, name):
        bmark = self.get_bmark_name()
=======
=======
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.
=======
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.
    def _eval_model_rbm(self, train, name):
        bmark = self.get_bmark_name(name)
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.
        self.stop_watch.start()
        for i in xrange(self.niter):
            train(i * self.batch_size, self.batch_size)
        elapsed_time = self.stop_watch.stop()
        self.add_speed(time)
        self._report_model(name, self.batch_size, elapsed_time, bmark)

    def _report_model(self, name, batch_size, elapsed_time, bmark):
        if self.algorithm == Algorithms.MLP:
            self._report_model_mlp(name, batch_size, elapsed_time, bmark)
        if self.algorithm == Algorithms.CONVNET:
            self._report_model_convnet(name, batch_size, elapsed_time, bmark)
        if self.algorithm == Algorithms.RBM:
            self._report_model_rbm(name, batch_size, elapsed_time, bmark)

    def _report_model_mlp(self, name, batch_size, elapsed_time, bmark):
        bmark.write("%s\t" % name)
        if config.floatX == 'float32':
            prec = 'float'
        else:
            prec = 'double'
        bmark.write("theano{%s/%s/%i}\t" % (
        config.device[0], prec, batch_size))
        bmark.write("%.2f\n"%(self.num_examples/elapsed_time)) # report examples / second

    def _report_model_convnet(self, name, batch_size, expsec, mode, bmark):
        bmark.write("%s\t" % name)
        if config.floatX == 'float32':
            prec = 'float'
        else:
            prec = 'double'
        bmark.write("theano{%s/%s/%i}\t" % (
            config.device[0], prec, batch_size))
        bmark.write("%.2f\n" % expsec)

    def _report_model_rbm(self, name, batch_size, elapsed_time, bmark):
        bmark.write("cd1 %s %i_%i\t" % (name, self.n_in, self.n_out))
        if config.floatX == 'float32':
            prec = 'float'
        else:
            prec = 'double'
        bmark.write("theano{%s/%s/%i}\t" % (
        config.device[0], prec, batch_size))
        bmark.write("%.2f\n" % (self.niter * elapsed_time))
    
    def compare(self, x, y):
        ratio = x / y
        # If there is more then 5% difference between the expected
        # time and the real time, we consider this an error.
        return sum((ratio < 0.95) + (ratio > 1.05))

    def get_mode(self):
        if config.device.startswith("gpu"):
            return RunMode.GPU
        else:
            if config.floatX == "float32":
                return RunMode.FLOAT_32
            elif config.floatX == "float64":
                return RunMode.FLOAT_64

    def report_speed_info(self):
        mode = self.get_mode()
        speed_outfile= "outs/speeds"
        f = open(speed_outfile, "w")
        if mode == RunMode.FLOAT_32:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
            err = self.compare(ExecutionTimes.expected_times_32, self.float32_times) 
            print >>f, "speed_failure_float64=" + str(err)
        elif mode == RunMode.FLOAT_64:
            err = self.compare(ExecutionTimes.expected_times_64, self.float64_times) 
            print >>f, "speed_failure_float64=" + str(err)
        elif mode == RunMode.GPU:
            err = self.compare(ExecutionTimes.expected_times_gpu, self.gpu_times)
            print >>f, "speed_failure_gpu=" + str(err)
=======
            err = self.compare(ExecutionTimes.expected_times_32, self.get_speeds()) 
            print>>f, "speed_failure_float64=" + str(err)
        elif mode == RunMode.FLOAT_64:
            err = self.compare(ExecutionTimes.expected_times_64, self.get_speeds()) 
            print>>f, "speed_failure_float64=" + str(err)
        elif mode == RunMode.GPU:
=======
            err = self.compare(ExecutionTimes.expected_times_32, self.get_speeds()) 
            print>>f, "speed_failure_float64=" + str(err)
        elif mode == RunMode.FLOAT_64:
            err = self.compare(ExecutionTimes.expected_times_64, self.get_speeds()) 
            print>>f, "speed_failure_float64=" + str(err)
        elif mode == RunMode.GPU:
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.
=======
            err = self.compare(ExecutionTimes.expected_times_32, self.get_speeds()) 
            print>>f, "speed_failure_float64=" + str(err)
        elif mode == RunMode.FLOAT_64:
            err = self.compare(ExecutionTimes.expected_times_64, self.get_speeds()) 
            print>>f, "speed_failure_float64=" + str(err)
        elif mode == RunMode.GPU:
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.
            err = self.compare(ExecutionTimes.expected_times_gpu, self.get_speeds())
            print>>f, "speed_failure_gpu=" + str(err)
>>>>>>> 7e41484... Removed the unnecessary eval and report functions.

GlobalBenchReporter = BenchmarkReporter()
