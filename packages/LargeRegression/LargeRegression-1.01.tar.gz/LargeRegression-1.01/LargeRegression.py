import sys
import numpy as np
import logging
import time

logging.basicConfig()
logger = logging.getLogger('LargeRegression')
logger.setLevel(logging.INFO)

class NumpyShapeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def regression_gradient_descent(Y, X, B = None, w = None, alpha = None,
                                convergence_threshold = 0.0001,
                                min_iters = 0, max_iters = 150, penalty = 0,
                                intercept = False, update_only = False,
                                XTX = None, XTY = None, verbose = True):
    """
    Computes the coefficient matrix for the linear regression problem using
    OLS and/or L2 normalization

    Uses batch gradient descent in order to iteratively determine the
    coefficient matrix.  This technique can be scaled with map reduce very easily
    as update steps are only computed using the error terms and the (fixed)
    design matrix.  This implies that each compute node only need a horizontal
    block of the response matrix and design matrix, and a vertical block of
    the coefficient matrix.

    For very large regressions, OLS regression estimates have high variance
    in predicted values and can be partially corrected for by using L2
    normalization.  Another approach is to use L1 normalization, but this
    cannot be implemented using batch gradient descent.  Another python
    module may or may not be developed for L1 normalization.

    Parameters
    ----------
    Y: 2d np.array
        A matrix representing the response variables of the linear regression
    X: 2d np.array
        A matrix representing the features of the observations.  This should
        not include the ones vector, which traditionally represents the
        intercept term
    B: 2d np.array
        A matrix representing an initial guess of what the coefficient matrix
        would be.  If intercept = True, this matrix should have px+1 rows 
        where px is the number of features found in X, and py columns where py
        is the number of different response variables found in Y.  If no
        intercept is included, then B should have px rows
    w: 1d np.array
        A 1d array of weights to be used for weighted linear regression.  If
        None, then this function defaults to the standard OLS problem.  The
        weighted least squares problem minimizes the sum of squared weighted
        residuals, as in sum ((w_i error_i)^2)
    alpha: float
        The learning rate.  When gradient descent moves B in the direction of
        the gradient, the step is scaled by alpha.  The default value of alpha
        is 1 / sqrt(Y.shape[0]).  This was found by experimentation,
        there is no proper evidence that it needs to be this rate.
    convergence_threshold: float
        This value determines when the iterative process should end.  A matrix
        B_new is created each update containing the coefficients after taking
        1 step in the direction of the gradient.  If the square of the
        Frobenius norm of (B_new - B) is less than convergence_threshold, then
        the algorithm terminates
    min_iters: int
        The minimum number of iterations this process must take before it is
        allowed to converge
    max_iters: int
        The maximum number of iterations used before this process terminates
        and reports that it could not converge
    penalty: float or 2d np.array
        The penalty added onto the RSS objective function for L2 normalization.
        The objective function then becomes ||Y-XB||_2^2 + penalty * ||B||_2.
        Note that penalty = 0 represents the traditional OLS.
        penalty may also be a 2d np.array, in which case a different penalty
        is applied to each value of B.  This allows us to weigh the features
        differently for each smaller, univariate regression
    intercept: boolean
        If True, append the intercept column in the design matrix
    update_only: boolean
        If True, return the update step in the direction of the gradient.
        If False, return the new coefficient matrix after taking 1 update step
    XTX: 2d np.array
        An optional argument.  The precomputed value of X.T * X, where X is the
        design matrix of the regression.  For X with many columns, X.T * X
        might NOT fit in memory
    XTY: 2d np.array
        An optional argument.  The precomputed value of X.T * Y, where X is the
        design matrix and Y is the response matrix of the regression
    verbose: boolean
        If True, print the status of the algorithm on the screen

    Returns
    -------
    out: 2d np.array
        The coefficient matrix minimizing the linear regression objective
        function

    Examples
    --------
    Y = np.random.randn(1000,10)
    X = np.random.randn(1000,20)
    B = np.random.randn(20,10)
    regression_gradient_descent(Y,X,B)
    np.linalg.lstsq(X,Y)[0]

    weights = range(Y.shape[0])
    regression_gradient_descent(Y,X,B,w=weights)

    penalty = np.random.randn(20,10)
    regression_gradient_descent(Y,X,penalty=penalty)
    """

    if Y.ndim != 2:
        raise NumpyShapeError("Y must be a 2d np.array")
    if X.ndim != 2:
        raise NumpyShapeError("X must be a 2d np.array")
    if Y.shape[0] != X.shape[0]:
        raise NumpyShapeError("Y and X must have the same amount of rows")
    if B is not None:
        if B.ndim != 2:
            raise NumpyShapeError("B should be a 2d np.array")
        if B.shape[1] != Y.shape[1]:
            raise NumpyShapeError("B should have the same number of columns as Y")
    if w is not None:
        if w.ndim != 1:
            raise NumpyShapeError("w should be a 1d np.array")
        if len(w) != Y.shape[0]:
            raise NumpyShapeError("w should have exactly 1 element for %s" % (
                                  "each row of Y"))
    if max_iters < min_iters:
        raise NameError("max_iters must be greater than min_iters")
    if penalty is None:
        penalty = 0
    n, xp = X.shape
    yp = Y.shape[1]

    if alpha is None:
        alpha = 1. / np.sqrt(n)
    if B is None:
        if intercept:
            B = np.zeros((xp + 1, yp))
        else:
            B = np.zeros((xp, yp))
    if intercept:
        intercept_vec = np.ones((n,1))
        design = np.hstack((intercept_vec, X))
    else:
        design = X
    
    if update_only:
        XB = np.dot(design, B)
        if w is None:
            return (alpha * (np.dot(design.T, Y - XB) + penalty * B))
        else:
            return (alpha * (np.dot(design.T * (W**2), Y - XB) + penalty * B))
 
    #Precomputed values used for optimization
    if XTY is None:
        if w is None:
            XTY = np.dot(design.T, Y)
        else:
            XTY = np.dot(design.T * (w**2), Y)
    if XTX is None:
        if w is None:
            XTX = np.dot(design.T, X)
        else:
            XTX = np.dot(design.T * (w**2), X)

    converged = False
    for i in xrange(max_iters):
        error = np.dot(XTX,B) - XTY
        gradient = error + penalty*B
        step_size = alpha / (np.linalg.norm(gradient, 'fro'))
        B_new = B - step_size * gradient
        if np.sum(np.isnan(B_new)) > 0:
            logger.warn("Warning, nan found in iteration %s" % (i))
        if (((np.linalg.norm(B_new-B, 'fro')**2) < convergence_threshold * yp) &
            (i > min_iters)):
            if verbose:
                logger.debug("Converged on iteration " + str(i))
            B = B_new
            converged = True
            break
        else:
            if verbose:
                logger.debug("End iteration " + str(i))
            B = B_new
    if converged == False & verbose:
        logger.warn("Gradient descent did not converge")
    return (B)

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
    test = regression_gradient_descent(Y, X, B, intercept=False, min_iters=100, alpha=1)
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
