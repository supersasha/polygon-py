from _nnet import ffi
import numpy as np
import ctypes

lib = ffi.dlopen('/usr/local/lib/libdoublefann.2.dylib')

SIZE_OF_DOUBLE = 8

class Net(object):
    def __init__(self, sizes=None, net=None):
        if sizes is None:
            if net is not None:
                num_layers = lib.fann_get_num_layers(net)
                layers = ffi.new('unsigned int[]', num_layers)
                lib.fann_get_layer_array(net, layers)
                sizes = list(layers)
            else:
                raise "Either 'sizes' or 'net' param must be specified"
        self.n_input = sizes[0]
        self.n_hiddens = sizes[1:-1]
        self.n_output = sizes[-1]
        self.n_by_layer = sizes
        self.n_b_by_layer = [n + 1 for n in self.n_by_layer[:-1]] + [self.n_output]
        self.output = np.zeros(self.n_output)
        sizes = ffi.new('unsigned int[]', self.n_by_layer)
        if net is None:
            self.net = lib.fann_create_standard_array(len(sizes), sizes)
            lib.fann_set_activation_function_hidden(self.net, lib.FANN_SIGMOID_SYMMETRIC)
            lib.fann_set_activation_function_output(self.net, lib.FANN_LINEAR)
            lib.fann_set_training_algorithm(self.net, lib.FANN_TRAIN_INCREMENTAL)
        else:
            self.net = net
        self.n_conn = lib.fann_get_total_connections(self.net)
        self.conns = ffi.new('struct fann_connection[]', self.n_conn)
    
    @staticmethod
    def create_from_file(filename):
        net = lib.fann_create_from_file(filename)
        return Net(net=net)

    def run(self, inp):
        out = lib.fann_run(self.net, ffi.cast('double *', inp.ctypes.data))
        ctypes.memmove(self.output.ctypes.data, int(ffi.cast('unsigned long', out)), SIZE_OF_DOUBLE * self.n_output)
        return self.output

    def train(self, inp, out):
        lib.fann_train(self.net, ffi.cast('double *', inp.ctypes.data),
                                 ffi.cast('double *', out.ctypes.data))

    def init_weights(self, min_weight, max_weight):
        #lib.fann_init_weights(self.net, self.train_data)
        lib.fann_randomize_weights(self.net, min_weight, max_weight)

    def get_weights(self):
        lib.fann_get_connection_array(self.net, self.conns)
        for w in self.conns:
            print w.from_neuron, '->', w.to_neuron, ':', w.weight
        layers = []
        for shape in zip(self.n_b_by_layer[:-1], self.n_by_layer[1:]):
            layers.append(np.zeros(shape))
        for c in self.conns:
            (layer_from, pos_from) = self.layer_and_pos_of_neuron(c.from_neuron)
            (layer_to, pos_to) = self.layer_and_pos_of_neuron(c.to_neuron)
            layers[layer_from][pos_from, pos_to] = c.weight
        return layers
        #return self.conns

    def print_connections(self):
        lib.fann_print_connections(self.net)

    def print_params(self):
        lib.fann_print_parameters(self.net)

    def layer_and_pos_of_neuron(self, n):
        # Including input layer and biases
        sum_sizes = 0
        for (layer_num, layer_size) in enumerate(self.n_b_by_layer):
            if n < layer_size + sum_sizes:
                pos = n - sum_sizes
                return (layer_num, pos)
            sum_sizes += layer_size
        return (-1, -1)
    def save(self, filename):
        lib.fann_save(self.net, filename)

def new_network():
    net = Net([2, 30, 20, 10, 1])
    net.init_weights(-0.1, 0.1)
    return net

def load_network(filename):
    net = Net.create_from_file(filename)
    return net

def test(net):
    ws = net.get_weights()
    for w in  ws:
        print w
    #print (ws[0].from_neuron, ws[0].to_neuron, ws[0].weight)
    net.print_connections()
    print lib.FANN_LINEAR, lib.FANN_SIGMOID
    net.print_params()
    net.save('my_fann_net_1')
    print net.run(np.array([1.0, 1.0]))
    arr_in = np.array([1.0, 1.0])
    arr_out = np.array([0.3333333333])
    for i in xrange(1000000):
        net.train(arr_in, arr_out)
    print net.run(arr_in)
    #
    #for w in ws:
    #    print w.from_neuron, '->', w.to_neuron, ':', w.weight

def test_cast():
    arr = np.array([1.0, 2, 3])
    for i in xrange(1000000):
        #x = ffi.cast('double*', arr.ctypes.data)
        x = arr.ctypes.data

if __name__ == '__main__':
    #net = load_network('my_fann_net_1')
    net = new_network()
    test(net)
    ws = net.get_weights()
    for w in  ws:
        print w
    net.print_connections()
    #test_cast()
