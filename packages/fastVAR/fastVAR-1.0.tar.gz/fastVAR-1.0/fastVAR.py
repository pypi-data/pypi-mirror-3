import sys
import numpy as np
import logging
import time
import LargeRegression as LR

logging.basicConfig()
logger = logging.getLogger('fastVAR')
logger.setLevel(logging.INFO)

class NumpyShapeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def _check_dimensions(Y, order, B=None):
    """
    Check the dimensions of the VAR matrices
    Y should be a multivariate time series represented as a 2d np.array
    B is a matrix of coefficients represented as a 2d np.array

    Params:
    -------
    Y: 2d np.array
        The multivariate time series
    order: int
        The VAR order
    B: 2d np.array, optional
        The coefficient matrix
    """
    if Y.ndim != 2:
        raise NumpyShapeError("Y should be a 2d np.array")
    rows, cols = Y.shape
    if B is not None and B is not '':
        if B.ndim != 2:
            raise NumpyShapeError("B should be a 2d np.array")
        if B.shape[0] != (cols*order) or B.shape[1] != cols:
            raise NumpyShapeError("B should have shape (cols*order,cols)")

def var_regression_matrices(Y, p, start_col=None, end_col=None):
    """
    Create the response and design matrices appropriate for
    modeling a VAR(p) system.

    If start_col and end_col are specified, a block of the response
    matrix is returned.  This can be useful if multiple regressions
    will run in parallel to model the VAR(p), in which case each process
    would work on a specific subset of the response matrix.

    Parameters
    ----------
    Y: 2d np.array
        The multivariate time series
    p: int
        The lag order of the VAR(p) model
    start_col, end_col: int, optional
        The portion of the regression that will be worked on

    Returns
    -------
    As a tuple:
    response: 2d np.array
        The response matrix to be used in a regression
    design: 2d np.array
        The design matrix to be used in a regression

    Example
    -------
    Y = np.random.randn(1000,10)
    response, design = var_regression_matrices(Y,2)
    np.linalg.lstsq(design, response)[0]

    Note that the response matrix is a truncated form of Y, found by removing
    the first p rows.  The design matrix is found by taking p lags of Y
    and stacking them horizontally, that is

    design = [Y_{t-1} | Y_{t-2} | ... | Y_{t-p}]
    """

    _check_dimensions(Y, order = p)

    s = slice(start_col, end_col)
    response = Y[p:,s]

    m, n = Y.shape
    design = np.empty((m - p, n * p,))
    for lag in xrange(1, p + 1):
        s = slice((lag-1) * n, lag * n)
        design[:,s] = Y[(p - lag) : -lag]

    return (response, design)

def var(Y, p, B=None, start_col=None, end_col=None, weights=None,
        penalty=None, alpha=None, min_iters=1, max_iters=100):
    """
    Formulate the VAR(p) problem as a multivariate linear regression and
    solve for the coefficient matrix.  Can use L2 penalty for very large
    models. 

    If start_col and end_col are specified, a block of the coefficient
    matrix is returned.  This can be useful if multiple regressions
    will run in parallel to model the VAR(p), in which case each process
    would work on a specific subset of the solution.

    Parameters
    ----------
    Y: 2d np.array
        The multivariate time series
    p: int
        The lag order of the VAR(p) model
    B: 2d np.array, optional
        An initial guess of the coefficient matrix.  If None, use
        numpy's lstsq function.  If a 2d np.array is provided, use
        gradient descent with an initial guess of B.
    start_col, end_col: int, optional
        The portion of the regression that will be worked on
    weights: 1d np.array, optional
        Weights to be applied to the multivariate regression that estimates
        the VAR coefficient matrix.  See LR.regression_gradient_descent
    penalty: 1d np.array, optional
        Applies an L2 penalty.  Can be an array of values which may be
        useful in cross-validation to determine the optimal penalty.  An
        efficient function fits the full path, so there is very little
        cost to testing multiple penalties
    alpha: float, optional
        Only used if using the gradient descent function to estimate
        the VAR.  alpha represents the learning rate, i.e. the size of
        the steps in the direction of the gradient
    max_iters: int, optional
        Only used if using the gradient descent function to estimate
        the VAR.  max_iters is the maximum number of iterations of gradient
        descent that are run before the algorithm is aborted

    Returns
    -------
    B: 2d np.array
       The coefficient matrix

    Example
    -------
    Y = np.random.randn(1000,10)
    var(Y, 2)
    var(Y, 2, penalty=5)
    var(Y, 2, penalty=np.array([3,4])
    """

    _check_dimensions(Y, p, B)

    response, design = var_regression_matrices(Y, p, start_col, end_col)
    if B is None:
        if penalty is None:
            return (np.linalg.lstsq(design, response)[0])
        else:
            if isinstance(penalty, int) or isinstance(penalty, float):
                penalty = np.array([penalty])
            return (ridge_regression(response, design, penalty))
    else:
        s = slice(start_col, end_col)
        B = B[:,s]
        return LR.regression_gradient_descent(response, design, B,
                                           w = weights,
                                           alpha = alpha,
                                           min_iters = min_iters,
                                           max_iters = max_iters,
                                           penalty = penalty)

def var_predict(Y, n, order, B=None):
    """
    Computes the n-step ahead predicton
    
    Params:
    -------
    Y: 2d np.array
        A multivariate time series
    n: int
        The number of steps out to predict
    order: int
        The order of the VAR model
    B: 2d np.array, optional
        The coefficient matrix for the VAR.  If None, B is calculated using the
        "var" function

    Returns:
    --------
    A 2d np.array with n rows representing the n-step ahead prediction

    Example:
    --------
    Y = np.random.randn(100,10)
    order = 2
    B = var(Y,order)
    var_predict(Y,2,order,B)

    Notes:
    ------
    Compute the n-step ahead prediction by computing n 1-step ahead
    predictions.  Each 1-step ahead prediction is computed by constructing
    a "design vector" whose features are the [order] most recent lagged values
    of the multivariate time series.  i.e. for VAR(2):

    Y_{t+1} = B_1 Y_t + B_2 Y_{t-1}

    so computing the next step ahead only requires the 2 most recent values of
    the multivariate time series.
    
    The design vector is found in the same way that the design matrix is
    computed in var_regression_matrices.  Instead of reusing that function, we
    will use a less memory intensive process which involves extracting the last
    [order] values, reversing  them, and collapsing them into a row vector.
    Predicted values are appended to Y so that they can be used in the next
    1-step ahead prediction
    """

    _check_dimensions(Y, order, B)
    rows, cols = Y.shape
    if B is None:
        B = var(Y, order)

    Y = np.vstack([Y, np.zeros((n, cols))])
    for i in xrange(n):
        prediction = np.dot(Y[:(rows+i),][-order:,][ ::-1,:].reshape(1,-1), B)
        Y[(rows + i),:] = prediction
    return Y[rows:,]

def get_covariance_of_errors(Y, order, B):
    """
    Given a coefficient matrix, compute the residuals Y-XB.
    Then, compute the covariance matrix of these residuals

    Params:
    -------
    Y: 2d np.array
        A multivariate time series
    order: int
        The VAR order
    B: 2d np.array
        The coefficient matrix

    Returns:
    --------
    A 2d np.array representing the covariance matrix
    of the residuals

    Examples:
    ---------
    Y = np.random.randn(100,10)
    order = 2
    B = var(Y, 2)
    error_cov = get_covariance_of_errors(Y, order, B)
    var_simulate(Y, 10, order, error_cov, B)
    """
    
    _check_dimensions(Y, order, B)
    response, design = var_regression_matrices(Y, order)
    rows, cols = response.shape
    error = response - np.dot(design, B)
    #remove mean from error matrix
    mean = error.mean(axis = 0)
    error = error - mean[None, :]
    return 1./rows * np.dot(error.T, error)

def var_simulate(init, n, order, error_cov, B):
    """
    Using the structure of B, simulate n-steps of a VAR process with initial
    conditions [init].
    Simulation differs from prediction in that simulation models the noise terms.
    By doing so, we illustrate all extremes of where the VAR process can go.
    In prediction, we seek the expected value of the next observation,
    and since the noise terms have mean 0 they are discarded in the function.

    Params:
    -------
    init: 2d np.array
        Initial conditions to create a new time series.  If None, extend
        the time series in Y.
    n: int
        The number of steps to simulate
    order: int
        The order of the VAR model
    error_cov: 2d np.array
    B: 2d np.array
        The coefficient matrix for how the VAR evolves.  If None,
        B is calculated using the var function

    Returns:
    --------
    A 2d np.array with n rows representing a simulation with structure B.
    Note that if init has m rows, only n-m extra rows are simulated

    Examples:
    ---------
    Y = np.random.randn(100,10)
    order = 2
    B = var(Y, 2)
    error_cov = get_covariance_of_errors(Y, order, B)
    var_simulate(Y, 10, order, error_cov, B)

    """
    
    if init.ndim != 2:
        raise NumpyShapeError("initial conditions should be a 2d np.array")
    rows, cols = init.shape
    if rows <= order:
        raise NumpyShapeError("initial conditions must have more rows than order")
    init = np.vstack([init, np.zeros((n, cols))])
    for i in xrange(n):
        prediction = np.dot(init[:(rows+i),][-order:,][ ::-1,:].reshape(1,-1), B)
        shock = np.random.multivariate_normal(np.zeros(cols), error_cov)
        init[(rows + i),:] = prediction + shock
    return init[rows:,]

def ridge_regression(Y, X, penalty):
    """
    Fits the full path for linear regression with L2 regularization
    Uses the SVD solution to the ridge regression, which allows us to
    efficiently compute the coefficient matrix with different penalty values

    Parameters
    ----------
    Y: 2d np.array
        The response matrix of the regression
    X: 2d np.array
        The design matrix of the regression
    penalty: 1d np.array
        An array of penalties to be used for L2 regularization

    Returns
    -------
    A generator that will produce the coefficient matrices corresponding
    to the penalties provided

    Example
    -------
    Y = np.random.randn(1000,10)
    X = np.random.randn(1000, 20)
    penalty = np.array([1,2,3])
    coefficients = ridge_regression(Y,X,penalty)
    for B in coefficients:
        print(B)

    """

    u, s, v = np.linalg.svd(X, False)
    suty = s * np.dot(u.T, Y)
    for p in penalty:
        singular_values_augmented = 1./ (s**2 + p)
        yield np.dot(v.T * singular_values_augmented, suty)

def main():
    n = 1000
    p = 20
    numY = 10

    X = np.random.randn(n,p)
    Btrue = np.random.randn(p,numY)
    Y = np.dot(X, Btrue)
    B = np.random.randn(p, numY)

    #Time gradient descent
    start_time = time.time()
    test = LR.regression_gradient_descent(Y, X, B, intercept=False, min_iters=100, alpha=1)
    end_time = time.time()
    elapsed = end_time - start_time

    #Time numpy's least squares
    start_time_np = time.time()
    test2 = np.linalg.lstsq(X,Y)
    end_time_np = time.time()
    elapsed_np = end_time_np - start_time_np

    print("True values of B:")
    print(Btrue)
    print("Estimated values from gradient descent:")
    print(test)
    print("Estimated values from numpy:")
    print(test2[0])
    print("gradient descent took " + str(elapsed) + " seconds")
    print("numpy took " + str(elapsed_np) + " seconds")

    return 0

if __name__ == "__main__":
    sys.exit(main())
