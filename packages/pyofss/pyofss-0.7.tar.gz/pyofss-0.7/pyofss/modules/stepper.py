
# ==============================================================================
"""
    Copyright (C) 2011, 2012  David Bolt

	 This file is part of pyofss.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# ==============================================================================

import numpy as np
from scipy import linalg

from storage import reduce_to_range
from storage import Storage
from solver import Solver
# ==============================================================================
class Stepper():
   """
   :param Uint traces: Number of ouput trace to use
   :param double local_error: Relative local error required in adaptive method
   :param string method: ODE solver method to use
   :param object f: Derivative function to be solved
   :param double length: Length to integrate over
   :param Uint total_steps: Number of steps to use for ODE integration

   method:
      * EULER -- Euler method;
      * MIDPOINT -- Midpoint method;
      * RK4 -- 4th order Runge-Kutta method;
      * BS -- Bogacki-Shampine method;
      * RKF -- Runge-Kutta-Fehlberg method;
      * CK -- Cash-Karp method;
      * DP -- Dormand-Prince method;
      * SSFM -- split-step Fourier method;
      * SSFM_SYM -- symmetrical version of SSFM;
      * SSFM_SYM_RK4 -- SSFM_SYM using RK4;
      * SSFM_SYM_RKF -- SSFM_SYM using RKF;
      * RK4IP -- Runge-Kutta in the interaction picture method.

      Each method may use an adaptive stepper by prepending an 'A' to the name.

   traces:
      * 0 -- Store A for each succesful step;
      * 1 -- Store A at final value (length) only;
      * >1 -- Store A for each succesful step then use interpolation to get A 
         values for equally spaced z-values, calculated using traces.
   """
   # ===========================================================================
   def __init__( self, traces = 1, local_error = 1.0e-6, method = "RK4",
                 f = None, length = 1.0, total_steps = 100 ):

      self.traces = traces
      self.local_error = local_error
      # ========================================================================
      # Check if adaptive stepsize is required:
      if( method[0].upper() == 'A' ):
         self.adaptive = True
         self.method = method[1:]
      else:
         self.adaptive = False
         self.method = method

#      print "Using {0} method".format( self.method )
      # ========================================================================
      # Delegate method and function to solver
      self.solver = Solver( self.method, f )
      self.step = self.solver
      # ========================================================================
      self.length = length
      self.total_steps = total_steps
      # ========================================================================
      # Use a list of tuples ( z, A(z) ) for dense output if required:
      self.storage = Storage()
   # ===========================================================================
   def __call__( self, A ):
      """ Delegate to appropriate function, adaptive- or standard-stepper """

      if( self.adaptive ):
         return self.adaptive_stepper( A )
      else:
         return self.standard_stepper( A )
   # ===========================================================================
   def standard_stepper( self, A ):
      """ Take a fixed number of steps, each of equal length """
      
#      print( "Starting ODE integration with fixed step-size... " ),
      # ========================================================================
      # Initialise:
      self.A_out = A
      # ========================================================================
      # Either set step-size according to required traces or total steps:
      if( self.traces > 1 ):
         h = self.length / self.traces
      else:
         h = self.length / self.total_steps
      # ========================================================================
      # Construct meshpoints for z:
      if( self.traces > 1 ):
         zs = np.linspace( 0.0, self.length, self.traces + 1 )
      else:
         zs = np.linspace( 0.0, self.length, self.total_steps + 1 )
      # ========================================================================
      # Make sure to store the initial A if more than one trace is required:
      if( self.traces > 1 ):
         self.storage.append( zs[0], self.A_out )
      # ========================================================================
      # Start at z = 0.0 and repeat until z = length - h (inclusive), i.e. z[-1]
      for z in zs[:-1]:
         # Currently at L = z.
         self.A_out = self.step( self.A_out, z, h )
         # Now at L = z + h
         # =====================================================================
         # If multiple traces required, store A_out at each relavant z value:
         if( self.traces > 1 ):
            self.storage.append( z + h, self.A_out )
      # ========================================================================
#      print( "done." )
      return self.A_out
   # ===========================================================================
   def adaptive_stepper( self, A ):
      """ Take multiple steps, with variable length, until target reached """
      
#      print( "Starting ODE integration with adaptive step-size... " ),
      # ========================================================================
      # Initialise:
      self.A_out = A
      z = 0.0
      # Require an initial step-size which will be adapted by the routine:
      h = (self.traces > 1) and (self.length / self.traces) \
                            or (self.length / self.total_steps)
      # ========================================================================
      # Calculate z-values at which to save traces.
      if( self.traces > 1 ):
         # zs contains z-values for each trace, as well as the initial trace:
         zs = np.linspace( 0.0, self.length, self.traces + 1 )
      # ========================================================================
      # Store initial trace:
      if( self.traces == 0 or self.traces > 1 ):
         self.storage.append( z, self.A_out )
      # ========================================================================
      # Limit the number of steps in case of slowly converging runs:
      steps_max = 4000
      for s in range(1, steps_max):
         # If step-size takes z our of range [0.0, length], then correct it:
         if( z + h > self.length ):
            h = self.length - z
         # =====================================================================
         # Take an adaptive step:
         safety_lower = 0.9
         safety_upper = 4.0

         total_attempts = 100
         # This starting value for attempts will be modified on success:
         attempts = total_attempts
         for ta in range(0, total_attempts):
            z_old = z
            h_half = 0.5 * h
            z_fine = z            
            # ==================================================================
            # Embedded methods have an estimate of the error. Other methods 
            # require step doubling for the error estimate:
            if( self.solver.embedded ):
               A_fine = self.step( self.A_out, z, h )
               z += h
               error_ratio = self.solver.error()
            else:
               # Fine solution uses two steps with half the step-size:
               A_fine = self.step( self.A_out, z_fine, h_half )
               z_fine += h_half
               A_fine = self.step( A_fine, z_fine, h_half )
               z_fine += h_half
               # ===============================================================
               # Coarse solution uses one step of full step-size:
               A_coarse = self.step( self.A_out, z, h )
               z += h
               # ===============================================================
               # Calculate the local error:
               error_ratio = linalg.norm(A_fine - A_coarse)
               error_ratio /= linalg.norm(A_fine)
            # ==================================================================
            error_ratio /= (2.0 * self.local_error)
            # ==================================================================
            # Modify step-size if necessary:
            h_temp = h
            h = safety_lower * h_temp * np.power( error_ratio, -0.2 )
            if( not h > (h_temp / safety_upper) ):
               h = h_temp / safety_upper
            if( not h < (safety_upper * h_temp) ):
               h = safety_upper * h_temp
            # ==================================================================
            # If error_ratio is reasonable then this was a succesful attempt:
            if( error_ratio < 1.0 ):
               self.A_out = A_fine
               # ===============================================================
#               self.storage.attempts = ta + 1
               # ===============================================================
               # Most dense storage (stores a trace for each successful step):
               if( self.traces == 0 or self.traces > 1 ):
                  self.storage.append( z, self.A_out )
                  self.storage.step_sizes.append( (z, h) )
               # ===============================================================
               break
         else:
#            self.storage.attempts = total_attempts
            raise Exception( "Failed to set suitable step-size" )
         # =====================================================================
#         print "\nStep = {0},\tAttempts = {1},\th = {2:.6f},\tz = {3}".format(\
#            s, attempts, h, z )
         # =====================================================================
         # If the desired z has been reached, then finish:
         if( z >= self.length ):
            # ==================================================================
            # Need to interpolate dense output to uniformly spaced A values:
            if( self.traces > 1 ):
               self.storage.interpolate_As_for_z_values( zs )
            # ==================================================================
#            print( "done." )
            return self.A_out
      # ========================================================================
      raise Exception( "Failed to complete with maximum steps allocated" )
# ==============================================================================
if __name__ == "__main__":
   """
   Exact solution: A(z) = 0.5 * ( 5.0 * exp(-2.0 * z) - 3.0 * exp(-4.0 * z) )
   A(0) = 1.0
   A(0.5) = 0.71669567807368684
   Numerical solution (RK4, total_steps = 5):      0.71668876283331295
   Numerical solution (RK4, total_steps = 50):     0.71669567757603803
   Numerical solution (RK4, total_steps = 500):    0.71669567807363854
   Numerical solution (RKF, total_steps = 5):      0.71669606109336026
   Numerical solution (RKF, total_steps = 50):     0.71669567807672185
   Numerical solution (RKF, total_steps = 500):    0.71669567807368773
   """
   # ===========================================================================
   import numpy as np
   import matplotlib.pyplot as plt
   # ===========================================================================
   def simple( A, z ):
      return 3.0 * np.exp(-4.0 * z) - 2.0 * A
   # ===========================================================================
   stepper = Stepper( f = simple, length = 0.5, total_steps = 50,
                      method = "RKF", traces = 50 )
   A = 1.0
   A_out = stepper( A )
   print "A_out = %.17f" % (A_out)
   # ===========================================================================
   x = stepper.storage.z
   y = stepper.storage.As
   # ===========================================================================
   title = r'$\frac{dA}{dz} + 2A = 3 e^{-4z}$'
   plt.title( r'Numerical integration of ODE:' + title )
   plt.xlabel( 'z' )
   plt.ylabel( 'A(z)' )
   plt.plot( x, y, label = 'RKF: 50 steps' )
   plt.legend()
   plt.show()
# ==============================================================================
