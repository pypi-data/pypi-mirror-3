#
# Copyright John Reid 2006, 2010
#

import numpy, infpy.exp.mvn

class Model( object ):
    """A mixture of multivariate normals

    N: number of data points
    K: number of mixtures (level of truncation of dirichlet process)
    alpha: Truncated dirichlet process parameter
    nu, S: Parameters for inverse-wishart conjugate prior on variances
    mu_0, kappa: Parameters for normal conjugate prior on means
    """

    def __init__(
            self,
            d = 2,
            N = 100,
            K = 10,
            S = None,
            nu = 10.0,
            mu_0 = None,
            kappa = .01,
            alpha = 3.0
    ):
        """Initialise a mixture of MVNs"""
        if None == S: S = numpy.eye( d, dtype = numpy.float64 )
        if None == mu_0: mu_0 = numpy.zeros( d, dtype = numpy.float64 )
        self.d = d
        self.N = N
        self.K = K
        self.nu = nu
        self.S = S
        self.mu_0 = mu_0
        self.kappa = kappa
        self.alpha = alpha
        self._set_up()

    def _set_up( self ):
        self.sigma = [
                numpy.linalg.inv(
                        infpy.exp_family.mvn.draw_from_wishart( self.nu, self.S )
                )
                for i
                in xrange( self.K )
        ]
        self.mu = [
                numpy.random.multivariate_normal(
                        mean = self.mu_0,
                        cov = s / self.kappa
                )
                for s
                in self.sigma
        ]
        self.V = numpy.random.beta( 1.0, self.alpha, self.K )
        self.V[-1] = 1.0
        self.theta = [
                self.V[i] *
                numpy.multiply.reduce(
                        [
                                1.0 - self.V[j]
                                for j
                                in xrange( i )
                        ]
                )
                for i
                in xrange( self.K )
        ]
        Z = [
                numpy.random.multinomial( 1, self.theta )
                for n
                in xrange( self.N )
        ]
        self.Z = [ numpy.nonzero( z )[0][0] for z in Z ]
        self.X = [
                numpy.random.multivariate_normal(
                        mean = self.mu[ self.Z[i] ],
                        cov = self.sigma[ self.Z[i] ]
                )
                for i
                in xrange( self.N )
        ]

def plot(
        X,
        mixtures,
        colours = [ 'k', 'b', 'g', 'r', 'c', 'm', 'y' ],
        styles = [ 'o', 'x', 's', '+', 'x', 'D', '^', 'v', '<', '>' ]
):
    """Plots first 2 dimensions of mixture distributions"""
    import pylab
    num_colours = len( colours )
    num_styles = len( styles )
    for x, mixture in zip( X, mixtures ):
        if mixture >= num_colours * num_styles:
            raise RuntimeError( 'Too many mixtures: need to define more styles' )
        marker = '%s%s' % (
                colours[ mixture % num_colours ],
                styles[ mixture / num_colours ]
        )
        pylab.plot( [ x[0] ], [ x[1] ], marker )


if '__main__' == __name__:
    import pylab
    raise
    model = Model()
    plot( model.X, model.Z )
    pylab.show()
