
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

from numpy import pi
from scipy import exp, power, log

from pyofss.field import fft, ifft
# ==============================================================================
class Filter():
   """
   :param string name: Name of this module
   :param double width_nu: Frequency bandwidth
   :param double nu: Frequency at which to filter
   :param Uint m: Order parameter
   :param bool is_fwhm: Decides if width_nu is FWHM or HWIeM

   Generate a Gaussian filter.
   """
   # ===========================================================================
   def __init__( self, name = "filter", width_nu = 0.1,
                 nu = 193.1, m = 1, is_fwhm = False ):

      self.name = name
      self.omega = 2.0 * pi * nu
      self.width = 2.0 * pi * width_nu
      self.m = m
      # ========================================================================
      # If using a FWHM definition then need to convert to HWIeM:
      if( is_fwhm ):
         self.width *= (0.5 / power( log(2.0), 1 / (2 * self.m) ))
   # ===========================================================================
   def __call__( self, domain, field ):
      
      # Convert field to spectral domain:
      self.field = fft( field )
      # ========================================================================
      Domega = domain.omega - self.omega
      factor = power( Domega / self.width, (2 * self.m) )

       # Frequency values are in order, inverse shift to put in fft order:
      self.shape = exp( -0.5 * ifftshift(factor) )
      # ========================================================================
      if( domain.channels > 1 ):
         self.field[0] *= self.shape
         self.field[1] *= self.shape
      else:
         self.field *= self.shape
      # ========================================================================
      # convert field back to temporal domain:
      return ifft( self.field )
# ==============================================================================
