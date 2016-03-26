from cffi import FFI

ffi = FFI()
ffi.set_source('_nnet', None)
ffi.cdef("""
    struct fann;
    struct fann_train_data;
    typedef double fann_type;
    
    struct fann_connection
    {
        /* Unique number used to identify source neuron */
        unsigned int from_neuron;
        /* Unique number used to identify destination neuron */
        unsigned int to_neuron;
        /* The numerical value of the weight */
        fann_type weight;
    };

    enum fann_activationfunc_enum
    {
        FANN_LINEAR = 0,
        FANN_THRESHOLD,
        FANN_THRESHOLD_SYMMETRIC,
        FANN_SIGMOID,
        FANN_SIGMOID_STEPWISE,
        FANN_SIGMOID_SYMMETRIC,
        FANN_SIGMOID_SYMMETRIC_STEPWISE,
        FANN_GAUSSIAN,
        FANN_GAUSSIAN_SYMMETRIC,
        /* Stepwise linear approximation to gaussian.
         * Faster than gaussian but a bit less precise.
         * NOT implemented yet.
         */
        FANN_GAUSSIAN_STEPWISE,
        FANN_ELLIOT,
        FANN_ELLIOT_SYMMETRIC,
        FANN_LINEAR_PIECE,
        FANN_LINEAR_PIECE_SYMMETRIC,
        FANN_SIN_SYMMETRIC,
        FANN_COS_SYMMETRIC,
        FANN_SIN,
        FANN_COS
    };
    
    enum fann_train_enum
    {
        FANN_TRAIN_INCREMENTAL = 0,
        FANN_TRAIN_BATCH,
        FANN_TRAIN_RPROP,
        FANN_TRAIN_QUICKPROP,
        FANN_TRAIN_SARPROP
    };
    
    enum fann_errorfunc_enum
    {
        FANN_ERRORFUNC_LINEAR = 0,
        FANN_ERRORFUNC_TANH
    };

    enum fann_stopfunc_enum
    {
        FANN_STOPFUNC_MSE = 0,
        FANN_STOPFUNC_BIT
    };
    
    struct fann * fann_create_standard_array(unsigned int num_layers,
        const unsigned int *layers);
    unsigned int fann_get_total_connections(struct fann * ann);
    fann_type * fann_run(struct fann *ann, fann_type * input);
    void fann_randomize_weights(struct fann * ann,
        fann_type min_weight, fann_type max_weight);
    void fann_train(struct fann * ann, fann_type * input, fann_type * desired_output);
    void fann_get_connection_array(struct fann *ann,
        struct fann_connection *connections);
    void fann_set_activation_function_hidden(struct fann *ann,
        enum fann_activationfunc_enum activation_function);
    void fann_set_activation_function_output(struct fann *ann,
        enum fann_activationfunc_enum activation_function);
    void fann_print_parameters(struct fann *ann);
    void fann_set_learning_rate(struct fann *ann, float learning_rate);

    void fann_set_training_algorithm(struct fann *ann,
        enum fann_train_enum training_algorithm);
    void fann_set_train_error_function(struct fann *ann,
        enum fann_errorfunc_enum train_error_function);    

    struct fann * fann_create_from_file(const char *configuration_file);
    int fann_save(struct fann *ann, const char *configuration_file);

    unsigned int fann_get_num_layers(struct fann *ann);
    void fann_get_layer_array(struct fann *ann, unsigned int *layers);

    //void * fann_create_standard(unsigned int num_layers, ...);
    //void fann_get_weights(void * ann, fann_type * weights);
    void fann_print_connections(struct fann *ann);
    void fann_init_weights(struct fann *ann, struct fann_train_data *train_data);
""")

if __name__ == '__main__':
    ffi.compile()



#print lib, dir(lib), lib.__dict__
#
#net = lib.fann_create_standard(3, ffi.cast('int', 2), ffi.cast('int', 2), ffi.cast('int', 1))
#
#nc = lib.fann_get_total_connections(net)
#
#weights = ffi.new('double[]', nc)
#
##lib.fann_print_connections(net)
##lib.fann_print_parameters(net)
#
#inp = ffi.new('fann_type[]', 2)
#inp[0] = 0
#inp[1] = 0
#out = lib.fann_run(net, inp)
#print out[0]
