
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

import numpy as np
from scipy import log10, exp
# ==============================================================================
def convert_alpha_to_linear( alpha_dB = 0.0 ):
   """
   :param double alpha_dB: Logarithmic attenuation factor
   :return: Linear attenuation factor
   :rtype: double

   Converts a logarithmic attenuation factor to a linear attenuation factor

   .. deprecated:: 0.8
      Use :func:`convert_alpha_to_linear` from linearity instead.
      This function may be removed before version 1.0 is released.
   """
   # ===========================================================================
   factor = 10.0 * log10( exp(1.0) )
   return alpha_dB / factor
# ==============================================================================
def convert_alpha_to_dB( alpha_linear = 0.0 ):
   """
   :param double alpha_linear: Linear attenuation factor
   :return: Logarithmic attenuation factor
   :rtype: double

   Converts a linear attenuation factor to a logarithmic attenuation factor

   .. deprecated:: 0.8
      Use :func:`convert_alpha_to_dB` from linearity instead.
      This function may be removed before version 1.0 is released.
   """
   # ===========================================================================
   factor = 10.0 * log10( exp(1.0) )
   return alpha_linear * factor
# ==============================================================================
class Attenuation():
   """
   :param double alpha: Attenuation factor
   :param string sim_type: Type of simulation, "default" or "wdm"
   :param bool use_cache: Cache exponential calculation optimisation

   Attenuation is used by fibre to generate an attenuation array.

   .. deprecated:: 0.8
      This class has been subsumed into the linearity class.
      This function may be removed before version 1.0 is released.
   """
   # ===========================================================================
   def __init__( self, alpha = None, sim_type = None, use_cache = False ):

      self.alpha = alpha
      # ========================================================================
      self.generate_attenuation = getattr( self, "%s_attenuation" % sim_type,
                                           self.default_attenuation )

      self.att = getattr( self, "%s_f" % sim_type, self.default_f )

      if( use_cache ):
         self.exp_att = getattr( self, "%s_exp_f_cached" % sim_type,
                                 self.default_exp_f_cached )
      else:
         self.exp_att = getattr( self, "%s_exp_f" % sim_type,
                                 self.default_exp_f )
      # ========================================================================
      self.cached_factor = None
   # ===========================================================================
   def __call__( self, domain ):

      return self.generate_attenuation( domain )
   # ===========================================================================
   def default_attenuation( self, domain ):
      if( self.alpha is None ):
         self.factor = 0.0
      else:
         self.factor = -0.5 * self.alpha

      return self.factor
   # ===========================================================================
   def wdm_attenuation( self, domain ):
      if( self.alpha is None ):
         self.factor = [0.0, 0.0]
      else:
         self.factor = [-0.5 * a for a in self.alpha]

      return self.factor
   # ===========================================================================
   def default_f( self, A, z ):
      return self.factor * A
   # ===========================================================================
   def default_exp_f( self, A, h ):
      return np.exp( h * self.factor ) * A
   # ===========================================================================
   def default_exp_f_cached( self, A, h ):
      if( self.cached_factor is None ):
         print "Caching attenuation factor"
         self.cached_factor = np.exp( h * self.factor )
      # ========================================================================
      return self.cached_factor * A
   # ===========================================================================
   def wdm_f( self, As, z ):
      return np.asarray([ self.factor[0] * As[0], self.factor[1] * As[1] ])
   # ===========================================================================
   def wdm_exp_f( self, As, h ):
      return np.asarray([ np.exp(h * self.factor[0]) * As[0], \
                          np.exp(h * self.factor[1]) * As[1] ])
   # ===========================================================================
   def wdm_exp_f_cached( self, As, h ):
      if( self.cached_factor is None ):
         print "Caching attenuation factor"
         self.cached_factor = [ np.exp(h * self.factor[0]),
                                np.exp(h * self.factor[1]) ]
      # ========================================================================
      return np.asarray([ self.cached_factor[0] * As[0],
                          self.cached_factor[1] * As[1] ])
# ==============================================================================
