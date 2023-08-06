
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

from bit import Bit
from gaussian import Gaussian
from sech import Sech
# ==============================================================================
class Generator():
   """
   :param string name: Name of this module
   :param object bit_stream: An array of Bit objects
   :param Uint channel: Channel to modify

   Generate a pulse with Gaussian or hyperbolic secant shape. Add this pulse 
   to appropriate field, determined by channel.
   """
   # ===========================================================================
   def __init__( self, name = "generator", bit_stream = None, channel = 0 ):
      
      self.name = name
      self.bit_stream = bit_stream
      self.channel = channel
      # ========================================================================
      # Always make a single bit as default, if no bitstream is passed:
      if( self.bit_stream is None ):
         self.bit_stream = [ Bit() ]
   # ===========================================================================
   # TODO: When calling self.shape.generate(), pass the temporal array for the 
   #       current bit, and not the whole time window.
   def __call__( self, domain, field ):
      """
      :param object domain: A Domain
      :param object field: Current field
      :return: Field after modification by Generator
      :rtype: Object
      """
      # ========================================================================
      self.field = field
      # ========================================================================
      for bit in self.bit_stream:
         if( bit["m"] > 0 ):
            self.shape = Gaussian( **bit() )
         else:
            self.shape = Sech( **bit() )
         # =====================================================================
         if( domain.channels > 1 ):
            self.field[ self.channel ] += self.shape.generate( domain.t )
         else:
            self.field += self.shape.generate( domain.t )
      # ========================================================================
      return self.field
# ==============================================================================
