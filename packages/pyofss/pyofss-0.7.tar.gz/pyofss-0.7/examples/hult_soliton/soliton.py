
# ==============================================================================
"""
    Copyright (C) 2012  David Bolt

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

from pyofss import *

import os.path
# ==============================================================================
methods = [ "SSFM", "SSFM_REDUCED", "SSFM_SYM", "SSFM_SYM_MIDPOINT", \
            "SSFM_SYM_RK4", "SSFM_SYM_RKF", "RK4IP"]

steps = [ 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000 ]

data_directory = "data_soliton"
# ==============================================================================
def order_2_soliton( xi = 0.0, tau = 0.0 ):
   numerator = 4.0 * ( np.cosh(3.0 * tau) + \
                       3.0 * np.exp(4.0 * 1j * xi) * np.cosh(tau) ) * \
               np.exp(0.5 * 1j * xi)
   # ===========================================================================
   denominator = np.cosh(4.0 * tau) + 4.0 * np.cosh(2.0 * tau) + \
                 3.0 * np.cos(4.0 * xi)
   # ===========================================================================
   return numerator / denominator
# ==============================================================================
domain = Domain( bit_width = 200.0, samples_per_bit = 4096 )

offset = 0.5 * domain.bit_width
A_true = [ order_2_soliton(0.5 * np.pi, t - offset) for t in domain.t ]
P_true = np.abs( A_true )**2
# ==============================================================================
for method in methods:
   print "%s" % method

   filename = ".".join( (str(method),"dat") )
   filename = os.path.join( data_directory, filename )
   with open( filename, "w" ) as f:
      f.write( "steps\t\tresult\t\t\tmean relative power" )
   # ===========================================================================
   results = []
   for step in steps:
      print "\t%d" % step

      system = System( domain )
      system.add( Sech(peak_power = 4.0, width = 1.0) )
      system.add( Fibre("fibre", length = 0.5 * np.pi, 
                        beta = [0.0, 0.0, -1.0, 0.0], gamma = 1.0, 
                        method = method, total_steps = step) )
      system.run()
      # ========================================================================
      P_t = temporal_power( system.fields['fibre'] )

      mean_relative_error = np.sum( np.abs(P_t - P_true) ) / np.max( P_true )
      mean_relative_error /= np.max( P_true )

      results.append( (step, max(P_t), mean_relative_error) )
   # ===========================================================================
   with open( filename, "a" ) as f:
      for result in results:
         f.write( "\n%6d\t%.12f\t%.12e" % result )
# ==============================================================================
