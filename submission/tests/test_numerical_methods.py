"""Independent deterministic checks; run with python -m unittest discover -s tests."""
import math
from pathlib import Path
import sys
import unittest

CODE = Path(__file__).resolve().parents[1]
if (CODE/"code").is_dir():
    CODE = CODE/"code"
sys.path.insert(0,str(CODE))
import numpy as np
import gbm
import nonaffine as na
import verify


class NumericalMethodsTests(unittest.TestCase):
    def test_gbm_recurrences_and_exact_moments(self):
        verify.check_gbm()

    def test_nonaffine_simultaneous_update_and_gbm_reduction(self):
        verify.check_nonaffine()

    def test_invalid_non_nested_grids_are_rejected(self):
        dw = np.zeros((8,2,2))
        for n in (0,3,6,9,2.5):
            with self.subTest(n=n), self.assertRaises(ValueError):
                na.em_terminal(dw,n,na.PARAMETERS)
        with self.assertRaises(ValueError):
            na.em_terminal(np.zeros((8,2)),4,na.PARAMETERS)

    def test_correlation_scaling_and_coarse_aggregation(self):
        p = na.PARAMETERS
        z = np.random.default_rng(77).standard_normal((16,7,2))
        actual = na.brownian_increments(np.random.default_rng(77),16,7,p)
        expected = z.copy()
        expected[:,:,1] = p["rho"]*z[:,:,0]+math.sqrt(1-p["rho"]**2)*z[:,:,1]
        expected *= math.sqrt(p["T"]/16)
        np.testing.assert_array_equal(actual,expected)
        direct = actual.reshape(4,4,7,2).sum(axis=1)
        direct_endpoint,_ = na.em_terminal(direct,4,p)
        aggregated_endpoint,_ = na.em_terminal(actual,4,p)
        np.testing.assert_array_equal(direct_endpoint,aggregated_endpoint)

    def test_increment_moments_use_time_not_time_squared(self):
        p = na.PARAMETERS
        dw = na.brownian_increments(np.random.default_rng(19),100,2000,p)
        covariance = np.cov(dw.reshape(-1,2),rowvar=False)
        target = p["T"]/100
        np.testing.assert_allclose(covariance.diagonal(),target,rtol=.02)
        correlation = covariance[0,1]/np.sqrt(covariance[0,0]*covariance[1,1])
        self.assertAlmostEqual(correlation,p["rho"],delta=.01)

    def test_control_variates_are_exactly_centered(self):
        # Independent Gaussian quadrature, not agreement with a plotted sample.
        nodes, weights = np.polynomial.hermite.hermgauss(30)
        h = .25
        dw = math.sqrt(2*h)*nodes
        density_weights = weights/math.sqrt(math.pi)
        tilted = np.exp(gbm.SIGMA*dw-.5*gbm.SIGMA**2*h)
        q = dw*dw-h
        h3 = dw*(dw*dw-3*h)
        checks = (tilted-1, tilted*(dw-gbm.SIGMA*h),
                  tilted*(q-gbm.SIGMA**2*h*h),
                  tilted*(h3-gbm.SIGMA**3*h**3),
                  tilted*(q*q-(2*h*h+4*gbm.SIGMA**2*h**3+gbm.SIGMA**4*h**4)))
        for values in checks:
            self.assertAlmostEqual(float(np.dot(density_weights,values)),0,places=13)

    def test_baseline_milstein_multiplier_is_positive(self):
        for n in gbm.LEVELS:
            h = gbm.T/int(n)
            minimum = .5+(gbm.MU-.5*gbm.SIGMA**2)*h
            self.assertGreater(minimum,0)
            dw = -1/gbm.SIGMA
            actual = 1+gbm.MU*h+gbm.SIGMA*dw+.5*gbm.SIGMA**2*(dw*dw-h)
            self.assertAlmostEqual(actual,minimum)


if __name__ == "__main__":
    unittest.main()
