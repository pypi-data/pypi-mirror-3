
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

from domain import Domain
# ==============================================================================
def calculate_regenerator_factor( alpha, D, gamma, length, peak_power,
                                  using_alpha_dB = False ):

   """
   :param double alpha: Attenuation factor
   :param double D: Dispersion
   :param double length: Fibre length
   :param double peak_power: Pulse peak power
   :param bool using_alpha_dB: Whether using a logarithmic attnuation factor
   :return: Maximum nonlinear phase and a factor indicating regeneration
   :rtype: double, double
   """
   # ===========================================================================
   if( using_alpha_dB ):
      factor = 10.0 * np.log10( np.exp(1.0) )
      alpha /= factor
   # ===========================================================================
   effective_length = ( 1.0 - np.exp(-alpha * length) ) / alpha
   # ===========================================================================
   max_nonlinear_phase = gamma * peak_power * effective_length
   regenerator_factor = abs( D * length ) / max_nonlinear_phase
   # ===========================================================================
   return (max_nonlinear_phase, regenerator_factor)
# ==============================================================================
class Metrics():
   """
   Calculate useful metrics using a domain and a field. An example metric is Q.
   """
   # ===========================================================================
   def __init__( self, domain = None, field = None ):

      if( (domain is None) or (field is None) ):
         raise Exception( "Metrics require a domain AND a field" )
      # ========================================================================
      self.domain = domain
      self.field = field
      # ========================================================================
      self.max_Q_dB = None
      self.sample_time = None
      self.sample_threshold = None
      # ========================================================================
      self.ones = None
      self.zeros = None
      # ========================================================================
      self.mean_peak_power_ones = None
      self.mean_peak_power_zeros = None
      # ========================================================================
      self.amplitude_jitter = None
      self.extinction_ratio = None
   # ===========================================================================
   def __repr__( self ):
      print "\nmax_Q = %f dB\nsample_time = %f ps\nthreshold = %f W" % \
         (self.max_Q_dB, self.sample_time, self.sample_threshold)
      print "\n<P_0,ones> = %f W\n<P_0,zeros> = %f W" % \
         (self.mean_peak_power_ones, self.mean_peak_power_zeros)
      print "\nextinction_ratio = %f dB" % self.extinction_ratio
      print "\namplitude_jitter = %f" % self.amplitude_jitter
   # ===========================================================================
   def calculate( self ):

      maximum_absolute_difference = -1.0
      sample_threshold = -1
      maximum_Q = -1.0
      sample_time = -1.0
      # ========================================================================
      for spb in range(0, self.domain.samples_per_bit):
         data = []
         for tb in range(0, self.domain.total_bits):
            P = abs( self.field[tb * self.domain.samples_per_bit + spb] )**2
            data.append( P )
         # =====================================================================
         threshold = sum( data ) / self.domain.total_bits
         # =====================================================================
         zeros = []
         ones = []
         for datum in data:
            if( datum < threshold ):
               zeros.append( datum )
            else:
               ones.append( datum )
         # =====================================================================
         if( (len(zeros) < 4) or (len(ones) < 4) ):
            print "Not enough ones and zeros to calculate Q"
#            raise Exception( "Not enough ones and zeros to calculate Q" )
         # =====================================================================
         absolute_difference = abs( np.mean(ones) - np.mean(zeros) )
         if( absolute_difference > maximum_absolute_difference ):
            maximum_absolute_difference = absolute_difference
            maximum_Q = absolute_difference / \
               ( np.std(ones) + np.std(zeros) )
            sample_time = spb * self.domain.dt
            sample_threshold = threshold
            # ==================================================================
            # Store ones and zeros arrays:
            self.ones = ones
            self.zeros = zeros
      # ========================================================================
      if( maximum_Q < 0.0 ):
         raise Exception( "Unable to calculate maximum Q!" )
      # ========================================================================
      self.max_Q_dB = 10.0 * np.log10( maximum_Q )
      self.sample_time = sample_time
      self.sample_threshold = sample_threshold
      # ========================================================================
      self.mean_peak_power_ones = np.mean( self.ones )
      self.mean_peak_power_zeros = np.mean( self.zeros )
      # ========================================================================
#      AJ = np.std( self.ones ) / np.mean( self.ones )
      AJ = (np.max(self.ones) - np.min(self.ones)) / (2.0 * np.mean(self.ones))
      self.amplitude_jitter = AJ

      ER = max(self.zeros) / ( np.mean(self.ones) * (1.0 - AJ) )
      self.extinction_ratio = -10.0 * np.log10( ER )

#      self.extinction_ratio = -10.0 * np.log10( max( self.zeros ) /
#                                                min( self.ones ) )
# ==============================================================================
