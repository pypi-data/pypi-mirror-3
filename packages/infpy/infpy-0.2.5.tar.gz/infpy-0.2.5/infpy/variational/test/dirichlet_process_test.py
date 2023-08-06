#
# Copyright John Reid 2006, 2010
#

import infpy.mvn_mixture, infpy.exp_family.mvn
import infpy.variational.dirichlet_process
import unittest, numpy.random

family = infpy.exp_family.mvn

def plot_mvn_mixture_dp_model_mixtures( model ):
    phi = [ family.phi( model.tau[i] ) for i in xrange( model.K ) ]
    for p in phi:
        infpy.plot_gaussian( p.mu_0, p.S / p.kappa )

def plot_mvn_mixture_dp_model( model, num_steps = 20 ):
    import pylab
    X = [ family.x( T ) for T in model.data ]
    x0_min = min( [ x[0] for x in X ] ) - 1.0
    x0_max = max( [ x[0] for x in X ] ) + 1.0
    x1_min = min( [ x[1] for x in X ] ) - 1.0
    x1_max = max( [ x[1] for x in X ] ) + 1.0
    spread0, spread1 = ( x0_max - x0_min, x1_max - x1_min )
    X = numpy.zeros( (num_steps + 1, num_steps + 1), dtype = numpy.float64 )
    Y = numpy.zeros( (num_steps + 1, num_steps + 1), dtype = numpy.float64 )
    Z = numpy.zeros( (num_steps + 1, num_steps + 1), dtype = numpy.float64 )
    for i0 in xrange( num_steps + 1 ):
        x0 = x0_min + i0 * ( x0_max - x0_min ) / num_steps
        for i1 in xrange( num_steps + 1 ):
            x1 = x1_min + i1 * ( x1_max - x1_min ) / num_steps
            X[i0,i1] = x0
            Y[i0,i1] = x1
            Z[i0,i1] = model.p_T( family.T( [ x0, x1 ] ) )
    pylab.contour( X, Y, Z, 40 )
    for x in X:
        pylab.plot( [ x[0] ], [ x[1] ] )

def testBeta():
    """
    Test variational dirichlet process mixture of beta distributions.
    """
    print 'Seeding numpy.random'
    numpy.random.seed( 3 )


def testMVN():
    """Test variational dirichlet process with a 2 dimensional multi-
    variate normal"""

    print 'Seeding numpy.random'
    numpy.random.seed( 3 )

    d = 2 # dimensions
    N = 70 # data
    K = 4 # mixtures
    DP_K = K + 1 # truncation parameter for DP

    # hyper-parameters
    phi = family.Phi(
            nu = 5.0,
            S = numpy.eye( d, dtype = numpy.float64 ),
            mu_0 = numpy.zeros( d, dtype = numpy.float64 ),
            kappa = 0.001
    )

    # Create a mixture model of multivariate gaussians
    print 'Generating %d %d-dimensional data points from %d mixtures' % (
            N, d, K
    )
    mixture_model = infpy.mvn_mixture.Model(
            K = K,
            N = N,
            nu = phi.nu,
            S = phi.S,
            mu_0 = numpy.array( phi.mu_0 ).reshape( (d,) ),
            kappa = phi.kappa,
    )

    x0_min, x0_max = (
            min( [ x[0] for x in mixture_model.X ] ) - 1.0,
            max( [ x[0] for x in mixture_model.X ] ) + 1.0
    )
    x1_min, x1_max = (
            min( [ x[1] for x in mixture_model.X ] ) - 1.0,
            max( [ x[1] for x in mixture_model.X ] ) + 1.0
    )

    # Build a DP model on this data
    # for i in range( 10 ):
    #       theta = family.draw_theta( lambda_ )
    #       infpy.plot_gaussian( theta.mu, theta.sigma() )
    # pylab.show() ; raise
    print 'Creating dirichlet process mixture model truncated at %d mixtures' % (
            DP_K
    )
    variational_model = infpy.variational.dirichlet_process.ExpFamilyDP(
            mixture_model.X,
            K = DP_K,
            alpha = 5.0,
            family = family,
            lambda_ = family.tau( phi )
    )


    def plot_it( i, LL ):
        """Plot the likelihood contours, the data points and the variational
        gaussians
        """
        import pylab
        print 'Log likelihood: %g' % LL
        #pylab.ioff()
        pylab.figure()
        plot_mvn_mixture_dp_model_mixtures( variational_model )
        plot_mvn_mixture_dp_model( variational_model )
        infpy.mvn_mixture.plot( mixture_model.X, mixture_model.Z )
        pylab.axis([x0_min,x0_max,x1_min,x1_max])
        pylab.title( 'Iteration %d: LL = %g' % ( i, LL ) )
        #pylab.show()
        #pylab.ion()

    last_LL = LL = variational_model.log_likelihood()
    plot_it( 0, LL )

    for i in xrange( 10 ):
        # Run one update on the model
        variational_model.update()
        LL = variational_model.log_likelihood()
        plot_it( i + 1, LL )
        if infpy.check_is_close( last_LL, LL ):
            break
        last_LL = LL


class DirichletProcessTest( unittest.TestCase ):

    def testWithMVN( self ):
        testMVN()


if __name__ == "__main__":
    testBeta()
    #testMVN()
    # unittest.main()
