"""Minimal teaching kernels. No production simulations or output overwrites.

Arrays use (paths, time steps), unlike the time-major nonaffine.py kernel.
Run this file only for small deterministic implementation checks.
"""
import numpy as np


def coarsen(dw_fine, n_coarse):
    """Sum neighbouring increments; retain the same Brownian realization."""
    m, n_fine = dw_fine.shape
    if n_coarse < 1 or n_fine % n_coarse:
        raise ValueError("n_coarse must divide the fine-grid size")
    return dw_fine.reshape(m, n_coarse, n_fine // n_coarse).sum(axis=2)


def gbm_terminal(dw, s0=100., mu=.05, sigma=.3, T=1.):
    h = T / dw.shape[1]
    exact = s0 * np.exp((mu - .5*sigma**2)*T + sigma*dw.sum(axis=1))
    multiplier = 1 + mu*h + sigma*dw
    em = s0 * np.prod(multiplier, axis=1)
    mil = s0 * np.prod(multiplier + .5*sigma**2*(dw**2-h), axis=1)
    return exact, em, mil


def correlated_increments(z1, z2, h, rho=-.7):
    """Inputs must be independent arrays of standard normal observations."""
    return np.sqrt(h)*z1, np.sqrt(h)*(rho*z1 + np.sqrt(1-rho**2)*z2)


def nonaffine_terminal(dw1, dw2, T=1.):
    if dw1.shape != dw2.shape:
        raise ValueError("The two increment arrays must have the same shape")
    m, n = dw1.shape
    h = T/n
    x, y = np.full(m, np.log(100.)), np.zeros(m)
    for k in range(n):
        sigmoid = np.exp(-np.logaddexp(0., -y))
        g = .1 + .4*sigmoid
        x_new = x + (.05-.5*g*g)*h + g*dw1[:, k]
        y_new = y + 2*(-.2-y)*h + .6*np.hypot(1., y)*dw2[:, k]
        x, y = x_new, y_new
    return np.exp(x)


def estimate(values):
    """Approximate pointwise 95% CI for the mean of independent paths."""
    values = np.asarray(values)
    if values.ndim != 1 or len(values) < 2:
        raise ValueError("Need at least two path observations")
    mean = float(values.mean())
    se = float(values.std(ddof=1) / np.sqrt(len(values)))
    return dict(mean=mean, se=se, lower=mean-1.96*se, upper=mean+1.96*se)


def error_summaries(coarse, reference, strike=100.):
    strong = estimate(np.abs(coarse-reference))
    payoff_difference = np.maximum(coarse-strike, 0)-np.maximum(reference-strike, 0)
    weak = estimate(payoff_difference)
    return strong, weak


def self_check():
    # Fixed values check arithmetic, not statistical convergence.
    fine = np.array([[.10, -.20, .05, .15], [-.05, .08, -.12, .09]])
    coarse = coarsen(fine, 2)
    np.testing.assert_allclose(coarse.sum(axis=1), fine.sum(axis=1))
    np.testing.assert_allclose(gbm_terminal(fine)[0], gbm_terminal(coarse)[0])
    h = .25
    em, mil = np.full(2, 100.), np.full(2, 100.)
    for k in range(4):
        factor = 1+.05*h+.3*fine[:, k]
        em *= factor
        mil *= factor+.5*.3**2*(fine[:, k]**2-h)
    np.testing.assert_allclose(gbm_terminal(fine)[1], em)
    np.testing.assert_allclose(gbm_terminal(fine)[2], mil)
    one1, one2 = np.array([[.12], [-.08]]), np.array([[-.09], [.10]])
    # The first price update uses g(Y_0)=0.3 and cannot use the new Y.
    expected = 100*np.exp((.05-.5*.3**2)+.3*one1[:, 0])
    np.testing.assert_allclose(nonaffine_terminal(one1, one2), expected)
    z1, z2 = fine, fine[:, ::-1]
    a, b = correlated_increments(z1, z2, .25)
    np.testing.assert_allclose(a, .5*z1)
    np.testing.assert_allclose(b, .5*(-.7*z1+np.sqrt(.51)*z2))
    assert estimate(np.array([-1., 1.]))['mean'] == 0
    print('PASS: aggregation, GBM updates, old-state log-EM, noise formula, mean.')


if __name__ == '__main__':
    self_check()
