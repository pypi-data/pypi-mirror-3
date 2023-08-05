""" This module contains a function that implements an artificial neuron model."""
def spike(w, s, th):
	""" Artificial Neuron Simulation

	    w : this neuron's synaptic weights, 1D array, w_i
		In biological manner, all components of w have the same sign.
                e.g. all positive numbers or all minus numbers.
	    s : synaptic input signals, 1D, s_i for i-th synapse in the dendrite
		So w and s have the same size(the type is 'list')
	    th : threshold of this neuron, 1 single value, th

	    This version implement a 'binary threshold signal function'. """
	# Step 1. Find an internal activation 'x'
	x = 0
	for i in range(len(w)):
		x = x + (w[i] * s[i])
	x = x + th
	
	# Step 2. x transformed through a Signal function.
	ret = 0;
	if x >= 0: ret = 1;
	return ret
