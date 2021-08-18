import functools
import math
import numpy as np
import scipy.optimize as opt

def sort_polyn_power_arr(arr):
  """ Sort the lines of a 2D array that represents the power of a polynomial.
      Sort so that result is in order:
        const, lin x0, lin x1, ..., quad x0, quad x1, ..., mixed (x0,x1), ...
  """
  rl_ordered = arr[np.lexsort(arr.T)]
  nonzero_order = np.count_nonzero(rl_ordered, axis=1, keepdims=True).T
  sum_order = np.sum(rl_ordered,axis=1,keepdims=True).T
  combined_order = np.concatenate( ( nonzero_order , sum_order), axis=0 )
  return rl_ordered[np.lexsort( combined_order )]
  
def cartesian_coord(*arrays):
  """ NumPy-way to get an array that holds all combinations of the numbers in 
      a given array for n drawing.
      -> Usage: cartesian_coord(*n_drawings*[number_array])
      E.g. n_drawings = 3, number_array = [0,1]
        => Result: [[0,0,0],[0,0,1],[0,1,0],[1,0,0],[0,1,1],...,[1,1,1]]
  """
  grid = np.meshgrid(*arrays)        
  coord_list = [entry.ravel() for entry in grid]
  points = np.vstack(coord_list).T
  return points

def polynomial_powers(order, n_pars):
  """ Get an array where each element describes the powers in the parameters for 
      a polynomial of the given order.
      Array is sorted (e.g. first constant term, then lin in x, lin in y, ...)
      for predictable behaviour.
  """
  powers = np.arange(1+order)
  all_power_combs = cartesian_coord(*n_pars*[powers])
  return sort_polyn_power_arr(
          all_power_combs[np.sum(all_power_combs,axis=1)<=order] )
  

def general_polynomial(pars, coefs, par_order_arr):
  """ Calculate the value of a n-dimensional array (n = len(pars)), given the 
      coefficients for the parameter-order-combinations given in par_order_arr.
      E.g. for 3 pars x,y,z
        par_order_arr = [
          [0,0,0], # -> Constant term
          [1,0,0], # -> Linear term in x
          [0,0,2], # -> Quadratic term in z
          [0,1,1]  # -> y*z term
        ]
  """
  if pars.ndim == 1:
    return np.sum(coefs * np.prod(pars**par_order_arr,axis=1))
  else:
    # Asking for multiple parameter points, requires some reshaping
    n_coefs = len(coefs)
    # NumPy array magic
    # Result: Factor for each coefficient for each par point
    coef_factors = np.prod( np.power(
        pars.repeat(n_coefs,axis=0).reshape(
          (len(pars),n_coefs,len(pars[0])) ), par_order_arr ), 
        axis=2)
    return np.sum(coefs * coef_factors, axis=1)
    

def n_polyn_coefs(order, dim):
  """ Get the number of coefficients for a polynomial of given dimension and 
      order.
  """  
  return int( np.sum([ 
          np.prod([dim + i for i in range(o)]) / math.factorial(o)
          for o in range(order+1) ]) )

def get_pol_coef(par_points, par_order_arr, point_results, res_unc):
  """ Get an initial guess for the coefficients of the polynomial for which the
      parameter-orders for each coefficient are given, using the results at the 
      given parameter points.
  """
  n_coefs = len(par_order_arr)
  if len(point_results) < n_coefs:
    raise Exception("Insufficient points, need at least {} and got {}".format(
                    n_coefs, len(point_results)) )
  
  # Select the first n points, n = number coefs
  used_points = par_points[:n_coefs]
  used_results = point_results[:n_coefs]
                    
  # NumPy array magic
  # Result: Factor for each coefficient for each par point
  coef_factors = np.prod( np.power(
      used_points.repeat(n_coefs,axis=0).reshape(
        (len(used_points),n_coefs,len(used_points[0])) ), par_order_arr ), 
      axis=2)
      
  # Solve the linear equation system to find a first guess
  ini_coefs = np.linalg.solve(coef_factors, used_results)
  
  # Prepare polynomial function
  def fit_polyn(par_points, *coefs):
    return general_polynomial(par_points, np.array([coefs]), par_order_arr)
  
  # Perform fit
  coefs, cov = opt.curve_fit(fit_polyn, par_points, point_results, 
                             sigma=res_unc, p0=ini_coefs)
  return coefs
  


# 
# 
# 
# # n_pars = 8
# # order = 3 # Third order polynomial
# # print(1 + n_pars + n_pars*(n_pars+1)/2 + n_pars*(n_pars+1)*(n_pars+2)/(2*3))
# # print(len(polynomial_powers(order, n_pars)))
# 
# order = 2 # Third order polynomial
# 
# pars = np.array([1,0.5,2])
# coefs = np.linspace(0.3,0.9,10)
# 
# par_order_arr = polynomial_powers(order, len(pars))
# print(par_order_arr)
# print(general_polynomial(pars, coefs, par_order_arr))
# # [general_polynomial(pars, coefs, polynomial_powers(order, len(pars))) for i in range(1000)]
# 
# 
# _pars = np.concatenate(([[pars + np.random.normal(size=pars.shape)] for i in range(10)]), axis=0)
# test_pars = np.concatenate(([[pars + np.random.normal(size=pars.shape)] for i in range(150)]), axis=0)
# 
# test_coefs = np.logspace(0.01,0.9,n_polyn_coefs(order, len(pars)))
# 
# 
# test_point_results = np.array([general_polynomial(_p, test_coefs, par_order_arr) for _p in test_pars])
# test_point_results += np.random.normal(size=test_point_results.shape, scale=0.01)
# 
# print(test_coefs)
# # print(test_point_results)
# 
# print(get_pol_coef(test_pars, par_order_arr, test_point_results, res_unc=0.1*np.ones_like(test_point_results)))
# 
# # readied_pars = _pars.repeat(len(powers),axis=0).reshape((len(_pars),len(powers),len(_pars[0])))
# # print(np.power(readied_pars,powers))
# # print(np.prod(np.power(readied_pars,powers),axis=2))