
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

from scipy import power, sqrt, log
# ==============================================================================
class Bit():
   """
   :param double position: Position of pulse
   :param double width: Width of pulse
   :param double peak_power: Peak power of pulse
   :param double offset_nu: Offset frequency of pulse
   :param Uint m: Order parameter
   :param double C: Chirp parameter
   :param double initial_phase: Initial phase of the pulse
   :param bool using_fwhm: Determines whether the width parameter is a full-
                           width at half maximum measure, or a half-width at 
                           1/e maximum measure

   Each bit is represented by a pulse.
   """
   # ===========================================================================
   def __init__( self, position = 0.5, width = 10.0, peak_power = 1e-3,
                 offset_nu = 0.0, m = 1, C = 0.0, initial_phase = 0.0,
                 using_fwhm = False ):

      self.data = { "position" : position, "width" : width,
                    "peak_power" : peak_power, "offset_nu" : offset_nu,
                    "m" : m, "C" : C, "initial_phase" : initial_phase }
      # ========================================================================
      if( using_fwhm ):
         # Convert from FWHM to HWIeM:
         if( m > 0 ):
            # Super-Gaussian pulse
            self.data["width"] *= 0.5 / power( log(2.0), 1.0 / (2 * m) )
         else:
            # Hyperbolic-secant pulse
            self.data["width"] *= 0.5 / log( 1.0 + sqrt(2.0) )
   # ===========================================================================
   def __getitem__( self, key ):
      return self.data[key]
   # ===========================================================================
   def __setitem__( self, key, value ):
      self.data[key] = value
   # ===========================================================================
   def __delitem__( self, key ):
      del self.data[key]
   # ===========================================================================
   def __call__( self ):
      return self.data
   # ===========================================================================
   #~def __repr__( self ):
      #~return "Bit with data:\n", self.data
# ==============================================================================
def generate_bitstream():
   return [ Bit() ]
# ==============================================================================
class Bit_stream():
   """
   A bit_stream consists of a number of bits.
   """
   # ===========================================================================
   def __init__( self ):

      self.bits = []
      self.prbs = []
   # ===========================================================================
   def __getitem__( self, key ):
      return self.bits[key]
   # ===========================================================================
   def add( self, bit ):
      self.bits.append( bit )
   # ===========================================================================
   def __add__( self, bit ):
      self.add( bit )
   # ===========================================================================
   #~def __repr__( self ):
      #~return "Bit stream containing bits:\n", self.bits
# ==============================================================================
def generate_prbs( domain = None, bit = Bit(), amplitude_jitter = 0.0,
                   ghost_pulse = 0.0 ):
   """
   :param object domain: Domain to use for calculations
   :param object bit: Bit parameters to use for generating a pulse
   :param double amplitude_jitter: Amount of amplitude jitter to add to pulse
   :param double ghost_pulse: Relative power for ghost pulses
   :return: A bitstream with paramaters to generate pulses
   :rtype: object

   * amplitude_jitter: percentage of variation in peak power of pulse 
                       representing bit.

   * ghost_pulse: maximum peak power of a pulse representing a zero bit, as a 
                  percentage of the mean peak power of pulses representing ones.
   """

   import random
   import copy
   # ===========================================================================
   if( domain is None ):
      print "Require domain for generating prbs"
      return
   # ===========================================================================
   # The peak power of the bit will be stored as the mean peak power of ones:
   mean_peak_power = bit["peak_power"]
#   print "mean_peak_power: %f" % mean_peak_power
   # One bits will have a peak power in the range given by the following tuple:
   one_range = ( mean_peak_power * (1.0 - amplitude_jitter),
                 mean_peak_power * (1.0 + amplitude_jitter) )
#   print "one_range: ", one_range
   # Zero bits will have peak_power in range given by the following tuple:
   ghost_range = ( 0.0, ghost_pulse * mean_peak_power )
#   print "ghost_range: ", ghost_range
   # ===========================================================================
   # Store the relative position for each pulse within a bit width:
   relative_position = bit["position"]
   # ===========================================================================
   bit_stream = []

   for b in range(0, domain.total_bits):
      # Decide if one or zero bit:
      is_one = random.randint(0, 1)
#      print "\nis_one: %d" % is_one
      # ========================================================================
      if( is_one ):      
         # If one: generate a peak_power within one_range
         peak_power = random.uniform( one_range[0], one_range[1] )
#         peak_power = random.gauss( mean_peak_power, 
#                                    amplitude_jitter * mean_peak_power )
      else:
         # If zero: generate a peak_power within ghost_range
         peak_power = random.uniform( ghost_range[0], ghost_range[1] )
      # ========================================================================
#      print "\npeak_power: %f" % peak_power
      # ========================================================================
      # Add bit to bit_stream
      # Note that without using deepcopy, peak_power would be the same for each
      # bit!
      next_bit = copy.deepcopy( bit )
      next_bit["peak_power"] = peak_power
      next_bit["position"] = (b + relative_position) / domain.total_bits
      bit_stream.append( next_bit )

   return bit_stream
# ==============================================================================
