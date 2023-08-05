"""Driver for gradient calculations."""

__authors__   = "James Bergstra"
__copyright__ = "(c) 2011, Universite de Montreal"
__license__   = "3-clause BSD License"
__contact__   = "theano-dev <theano-dev@googlegroups.com>"

__docformat__ = "restructuredtext en"

import logging
_logger = logging.getLogger('theano.gradient')
import sys

import numpy #for numeric_grad

import gof #, gof.variable
from gof.python25 import all
import gof.utils

from raise_op import Raise

_msg_retType = 'op.grad(...) returned a non-list'
_msg_badlen = 'op.grad(...) returned wrong number of gradients'

def grad_sources_inputs(sources, graph_inputs, warn_type=True):
    """
    :type sources: list of pairs of Variable: (v, gradient-on-v)
    :param sources: gradients to back-propagate using chain rule
    :type graph_inputs: list of Variable
    :param graph_inputs: variables considered to be constant (do not backpropagate through
    them)

    :rtype: dictionary whose keys and values are of type `Variable`
    :return: mapping from each Variable encountered in the backward traversal to the gradient with respect to that Variable.

    It is assumed that there is some objective J shared between all members of
    sources, so that for each v, gradient-on-v is the gradient of J with respect to v




    """
    gmap = {}
    for (r, g_r) in sources:
        if not hasattr(r, 'type'):
            raise TypeError('sources must be Variables', r)
        if g_r is not None:
            if r in gmap:
                gmap[r] = gmap[r] + g_r
            else:
                gmap[r] = g_r

    graph_outputs = gof.utils.uniq([r for r,g in sources])

    if graph_inputs is None:
        graph_inputs = gof.graph.inputs(graph_outputs)

    for node in gof.graph.io_toposort(graph_inputs, graph_outputs).__reversed__():
        g_outputs = [gmap.get(o,None) for o in node.outputs]

        #if all output gradients are None, continue
        if all(map(lambda x:x is None, g_outputs)): continue

        output_arg = g_outputs
        input_arg = node.inputs

        # Each Op's grad function requires inputs and output_grads
        # If the Op destroys any input, but the grad expression uses it, then chances are the
        # resulting graph will have a dependency cycle.  We avoid this cycle by passing
        # (symbolic) copies of each destroyed input.
        try:
            dinputs = [node.inputs[x[0]] for x in node.op.destroy_map.values()]
        except AttributeError:
            dinputs = []

        new_input_arg = []
        for input in input_arg:
            if input in dinputs and hasattr(input, 'copy'):
                new_input_arg.append(input.copy())
            else:
                new_input_arg.append(input)
        input_arg = new_input_arg

        #note that this function is not in a try-except block
        # the rationale:
        #  If the op implements grad, then any exception should be passed to the
        #  caller
        #  If the op doesn't implement grad, this entire function should fail.
        #  Other possibilities:
        #    * return a partial back-prop
        #
        op_grad = node.op.grad(input_arg, output_arg)
        if not isinstance(op_grad, (list,tuple)):
            raise ValueError(_msg_retType, node.op)
        g_inputs = op_grad
        assert isinstance(g_inputs, (list, tuple))
        if len(g_inputs) != len(node.inputs):
            raise ValueError(_msg_badlen,
                    node.op,
                    len(g_inputs),
                    len(node.inputs))
        for ii, (r, g_r) in enumerate(zip(node.inputs, g_inputs)):
            if warn_type:
                if g_r and (getattr(r,'type',0) != getattr(g_r,'type', 1)):
                    r_type = getattr(r,'type', None)
                    g_r_type = getattr(g_r,'type', None)
                    _logger.warning('%s.grad returned a different type (%s) '
                            'for input %i of type (%s)',
                            node.op, g_r_type, ii, r_type)
            if g_r and len(sources) == 1 and sources[0][0].name and r.name:
                g_r.name = "(d%s/d%s)" % (sources[0][0].name, r.name)
            if g_r is not None:
                assert r is not None
                if r in gmap:
                    gmap[r] = gmap[r] + g_r
                else:
                    gmap[r] = g_r
    return gmap

def unimplemented_grad(op, x_pos, x):
    """
    DO NOT USE. Remove this function after all usage of it has been removed from theano.

    Return an un-computable symbolic variable of type `x.type`.

    If any function tries to compute this un-computable variable, an exception
    (NotImplementedError) will be raised indicating that the gradient on the
    `x_pos`'th input of `op` has not been implemented.

    """

    #raise Exception("""
    #                    unimplemented_grad is not a safe function to use.
    #                    It depends on catching errors at the run-time of a theano function.
    #                    However, it could be removed by the optimization during the compilation
    #                    of the theano function, for example, if it is multiplied by 0. This
    #                    results in theano functions returning 0 for gradients that are actually
    #                    undefined. """)

    msg = '%s.grad not implemented for input %i'%(op, x_pos)
    return Raise(msg=msg)(x)
