#
# Copyright John Reid 2006
#

import infpy.mvn_mixture, unittest


class MultivariateNormalMixtureModelTest( unittest.TestCase ):
    def testCreation( self ):
        """test multi-variate normal mixture creation"""
        model = infpy.mvn_mixture.Model()
        if len( model.sigma ) != model.K:
            raise RuntimeError( 'Should have K sigmas' )
        if len( model.mu ) != model.K:
            raise RuntimeError( 'Should have K mu' )
        if len( model.V ) != model.K:
            raise RuntimeError( 'Should have K v\'s' )
        if len( model.theta ) != model.K:
            raise RuntimeError( 'Should have K theta' )
        if len( model.Z ) != model.N:
            raise RuntimeError( 'Should have N z\'s' )
        if len( model.X ) != model.N:
            raise RuntimeError( 'Should have N x\'s' )
        if not infpy.check_is_close( 1.0, sum( model.theta ) ):
            raise RuntimeError(
                    'Mixture model theta should sum to 1.0: %g'
                    % sum( mixture_model.theta )
            )
        for i in xrange( model.K ):
            if model.sigma[i].shape != (model.d, model.d):
                raise RuntimeError( 'All sigmas should be dxd arrays' )
            if model.mu[i].shape != (model.d,):
                raise RuntimeError( 'All mus should be length d arrays' )
            if not isinstance( model.V[i], float ):
                raise RuntimeError( 'All v\'s should be floats' )
            if not isinstance( model.theta[i], float ):
                raise RuntimeError( 'All thetas should be floats' )
        for n in xrange( model.N ):
            if not isinstance( model.Z[n], int ):
                raise RuntimeError( 'All z\'s should be ints' )
            if model.X[n].shape != (model.d,):
                raise RuntimeError( 'All x\'s should be length d arrays' )

if __name__ == "__main__":
    unittest.main()
