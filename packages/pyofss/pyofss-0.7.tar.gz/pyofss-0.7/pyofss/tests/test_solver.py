
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

from pyofss.modules.solver import Solver
from pyofss.modules.solver import NoDerivativeFunctionError

import unittest2
# ==============================================================================
def default_function( A, z ):
   return A
# ==============================================================================
class Default_parameters( unittest2.TestCase ):
   def test_no_derivative_function( self ):
      """ Should raise exception if derivative function is None (default) """
      self.assertRaises( NoDerivativeFunctionError, Solver )
   # ===========================================================================
   def test_default( self ):
      """ Should use default values (except for f) """
      solver = Solver( f = default_function )
      # ========================================================================
      self.assertIsNone( solver.result, "result should default to None" )
      self.assertIsNone( solver.A_coarse, "A_coarse should default to None" )
      self.assertIsNone( solver.A_fine, "A_fine should default to None" )
      self.assertEqual( solver.method, solver.rk4, \
                        "method should default to rk4" )
      self.assertFalse( solver.embedded, "RK4 is not an embedded method" )
   # ===========================================================================
   def test_attributes( self ):
      """ Should list ODE integration methods """
      self.assertEqual( Solver.explicit_solvers, ["euler", "midpoint", "rk4"] )
      self.assertEqual( Solver.embedded_solvers, ["bs", "rkf", "ck", "dp"] )
      self.assertEqual( Solver.ssfm_solvers, \
                        ["ssfm", "ssfm_reduced", "ssfm_sym", \
                         "ssfm_sym_midpoint", "ssfm_sym_rk4", "ssfm_sym_rkf"] )
      self.assertEqual( Solver.other_solvers, [ "rk4ip" ] )
# ==============================================================================
class Check_functions( unittest2.TestCase ):
   def test_error( self ):
      solver1 = Solver( f = default_function )
      solver2 = Solver( f = default_function, method = "RKF" )
      solver2.A_fine = 2.0
      solver2.A_coarse = 1.0
      print solver2.error()
      # ========================================================================
      """ Should return None if not an embedded method """
      self.assertIsNone( solver1.error(), "Default method is not embedded" )
      self.assertIsNone( solver2.error(), "RKF method is an embedded method" )
# ==============================================================================
if __name__ == "__main__":
   unittest2.main()
# ==============================================================================
