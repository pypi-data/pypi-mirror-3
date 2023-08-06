
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

from pyofss.modules.stepper import Stepper

from numpy.testing.utils import assert_almost_equal # uses decimal places
from numpy.testing.utils import assert_equal

import numpy as np
from scipy.fftpack import fft, ifft, ifftshift

import unittest
# ==============================================================================
class Default_parameters( unittest.TestCase ):
   def default_function( A, z ):
      return A
   # ===========================================================================
   def test_default( self ):
      """ Should use default values (except for f) """
      stepper = Stepper( f = self.default_function )
      # ========================================================================
      self.assertEqual( stepper.traces, 1 )
      self.assertEqual( stepper.local_error, 1e-6 )
      self.assertEqual( stepper.method, "RK4" )
      self.assertEqual( stepper.length, 1.0 )
      self.assertEqual( stepper.total_steps, 100 )
      self.assertEqual( stepper.adaptive, False )
# ==============================================================================
class Bad_parameters( unittest.TestCase ):
   def test_too_low( self ):
      """ Should fail when parameters are too low """
      pass
   # ===========================================================================
   def test_too_high( self ):
      """ Should fail when parameters are too high """
      pass
   # ===========================================================================
   def test_wrong_type( self ):
      """ Should fail if wrong type """
      pass
# ==============================================================================
class Check_core_routines( unittest.TestCase ):
   r"""
   ODE: $\frac{ dA }{ dz } + 2A - 3 \exp{-4z} = 0$
   Initial value: A(0) = 1.0
   Exact solution: $A(z) = \frac{5 \exp{-2z} - 3 \exp{-4z} }{ 2 }$
   A(0.5) = 0.71669567807368684
   """
   def simple( self, A, z ):
      """ Example of derivative to use for integration """
      return 3.0 * np.exp(-4.0 * z) - 2.0 * A
   # ===========================================================================
   def setUp( self ):
      """ Store common parameters for each test """
      self.parameters = { "traces" : 1, "local_error" : 1.0e-6,
                          "method" : None, "f" : self.simple, 
                          "length" : 0.5, "total_steps" : 50 }
      self.A_initial = 1.0
      self.A_analytical = 0.71669567807368684
   # ===========================================================================
   def test_euler( self ):
      """ A_numerical should be approximately equal to A_analytical """
      self.parameters[ "method" ] = "EULER"
      # ========================================================================
      self.parameters[ "total_steps" ] = 50
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_equal( A_numerical, 0.72152686293820223 )
      # ========================================================================
      self.parameters[ "total_steps" ] = 500
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_equal( A_numerical, 0.71717199224362427 )
   # ===========================================================================
   def test_midpoint( self ):
      """ A_numerical should be approximately equal to A_analytical """
      self.parameters[ "method" ] = "MIDPOINT"
      # ========================================================================
      self.parameters[ "total_steps" ] = 50
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_equal( A_numerical, 0.71663952968427402 )
      # ========================================================================
      self.parameters[ "total_steps" ] = 500
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_equal( A_numerical, 0.71669512731047913 )
   # ===========================================================================
   def test_rk4( self ):
      """ A_numerical should be approximately equal to A_analytical """
      self.parameters[ "method" ] = "RK4"
      # ========================================================================
      self.parameters[ "total_steps" ] = 50
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_almost_equal( A_numerical, self.A_analytical )
      assert_equal( A_numerical, 0.71669567757603803 )
      # ========================================================================
      self.parameters[ "total_steps" ] = 500
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_almost_equal( A_numerical, self.A_analytical )
      assert_equal( A_numerical, 0.71669567807363854 )
   # ===========================================================================
   def test_bs( self ):
      """ A_numerical should be approximately equal to A_analytical """
      self.parameters[ "method" ] = "BS"
      # ========================================================================
      self.parameters[ "total_steps" ] = 50
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_equal( A_numerical, 0.71671160608028039 )
      # ========================================================================
      self.parameters[ "total_steps" ] = 500
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_equal( A_numerical, 0.71669583430970152 )
   # ===========================================================================
   def test_rkf( self ):
      """ A_numerical should be approximately equal to A_analytical """
      self.parameters[ "method" ] = "RKF"
      # ========================================================================
      self.parameters[ "total_steps" ] = 50
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_almost_equal( A_numerical, self.A_analytical )
      assert_equal( A_numerical, 0.71669567807672185 )
      # ========================================================================
      self.parameters[ "total_steps" ] = 500
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_almost_equal( A_numerical, self.A_analytical )
      assert_equal( A_numerical, 0.71669567807368773 )
   # ===========================================================================
   def test_ck( self ):
      """ A_numerical should be approximately equal to A_analytical """
      self.parameters[ "method" ] = "CK"
      # ========================================================================
      self.parameters[ "total_steps" ] = 50
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_almost_equal( A_numerical, self.A_analytical )
      assert_equal( A_numerical, 0.71669567804234302 )
      # ========================================================================
      self.parameters[ "total_steps" ] = 500
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_almost_equal( A_numerical, self.A_analytical )
      assert_equal( A_numerical, 0.71669567807368351 )
   # ===========================================================================
   def test_dp( self ):
      """ A_numerical should be approximately equal to A_analytical """
      self.parameters[ "method" ] = "DP"
      # ========================================================================
      self.parameters[ "total_steps" ] = 50
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_almost_equal( A_numerical, self.A_analytical )
      assert_equal( A_numerical, 0.71669567807314427 )
      # ========================================================================
      self.parameters[ "total_steps" ] = 500
      stepper = Stepper( **self.parameters )
      A_numerical = stepper( self.A_initial )
      assert_almost_equal( A_numerical, self.A_analytical )
      assert_equal( A_numerical, 0.71669567807368462 )
# ==============================================================================
class Check_methods( unittest.TestCase ):
   r"""
   Soliton example with analytical solution:

   """
   class Function():
      def __init__( self, domain ):
         self.beta_2 = -1.0
         self.gamma = 1.0
         # =====================================================================
         self.Domega = domain.omega - domain.centre_omega
         self.factor = 1j * ifftshift( 0.5 * self.beta_2 * self.Domega**2 )
      # ========================================================================
      def l( self, A, z ):
         return fft( self.factor * ifft(A) )
      # ========================================================================
      def n( self, A, z ):
         return 1j * self.gamma * np.abs(A)**2 * A
      # ========================================================================
      def linear( self, A, h ):
         return fft( np.exp( h * self.factor ) * ifft(A) )
      # ========================================================================
      def nonlinear( self, A, h, B = None ):
         if( B is None ):
            B = A

         return np.exp( h * 1j * self.gamma * np.abs(A)**2 ) * B
   # ===========================================================================
   def setUp( self ):
      from pyofss.domain import Domain
      from pyofss.modules.sech import Sech
      # ========================================================================
      domain = Domain( bit_width = 200.0, samples_per_bit = 2048 )
      sech = Sech( peak_power = 4.0, width = 1.0 )
      # ========================================================================
      function = self.Function( domain )
      self.parameters = { "traces" : 1, "local_error" : 1.0e-6,
                          "method" : None, "f" : function, 
                          "length" : 0.5 * np.pi, "total_steps" : 1000 }
      # ========================================================================
      self.A_analytical = 2.0
      self.P_analytical = np.abs( self.A_analytical )**2
      self.A_in = sech.generate( domain.t )
   # ===========================================================================
   def test_ssfm( self ):
      self.parameters[ "method" ] = "SSFM"
      stepper = Stepper( **self.parameters )
      A_out = stepper( self.A_in )
      # ========================================================================
      assert_almost_equal( max( np.abs(A_out)**2 ), self.P_analytical, 3 )
   # ===========================================================================
   def test_ssfm_reduced( self ):
      self.parameters[ "method" ] = "SSFM_REDUCED"
      stepper = Stepper( **self.parameters )
      A_out = stepper( self.A_in )
      # ========================================================================
      assert_almost_equal( max( np.abs(A_out)**2 ), self.P_analytical, 3 )
   # ===========================================================================
   def test_sym_ssfm( self ):
      self.parameters[ "method" ] = "SSFM_SYM"
      stepper = Stepper( **self.parameters )
      A_out = stepper( self.A_in )
      # ========================================================================
      assert_almost_equal( max( np.abs(A_out)**2 ), self.P_analytical, 0 )
   # ===========================================================================
   def test_sym_ssfm_rk4( self ):
      self.parameters[ "method" ] = "SSFM_SYM_RK4"
      stepper = Stepper( **self.parameters )
      A_out = stepper( self.A_in )
      # ========================================================================
      assert_almost_equal( max( np.abs(A_out)**2 ), self.P_analytical, 3 )
   # ===========================================================================
   def test_sym_ssfm_rkf( self ):
      self.parameters[ "method" ] = "SSFM_SYM_RKF"
      stepper = Stepper( **self.parameters )
      A_out = stepper( self.A_in )
      # ========================================================================
      assert_almost_equal( max( np.abs(A_out)**2 ), self.P_analytical, 3 )
   # ===========================================================================
   def test_rk4ip( self ):
      self.parameters[ "method" ] = "RK4IP"
      stepper = Stepper( **self.parameters )
      A_out = stepper( self.A_in )
      # ========================================================================
      assert_almost_equal( max( np.abs(A_out)**2 ), self.P_analytical, 5 )
# ==============================================================================
class Check_functions( unittest.TestCase ):
   def test_standard_stepper( self ):
      """ Stepper should integrate function using fixed step-size """
      pass
   def test_adaptive_stepper( self ):
      """ Stepper should integrate function using adaptive step-size """
      pass
# ==============================================================================
if __name__ == "__main__":
   unittest.main()
# ==============================================================================

