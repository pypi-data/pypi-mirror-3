
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

from pyofss import *
# ==============================================================================
system = System( Domain(bit_width = 100.0, samples_per_bit = 4096) )
system.add( Sech(peak_power = 1.0, width = 1.0) )
system.add( Fibre(length = 0.5 * np.pi, beta = [0.0, 0.0, -1.0, 0.0],
                  gamma = 9.0, traces = 100, method = 'ARK4IP') )
system.run()
# ==============================================================================
stepper = system['fibre'].stepper
# ==============================================================================
x = system.domain.nu
temp = [ spectral_power(A) for A in stepper.storage.As ]
factor = max( temp[0] )
y = [ t / factor for t in temp ]
z = stepper.storage.z
# ==============================================================================
x, y = reduce_to_range( x, y, 191.1, 195.1 )
# ==============================================================================
map_plot( x, y, z, labels["nu"], labels["P_nu"], labels["z"],
          "lanczos", True, "5-6_map_nu.png", 100 )
# ==============================================================================
waterfall_plot( x, y, z, labels["nu"], labels["z"], labels["P_nu"],
                True, 0.2, "5-6_waterfall_nu.png", 100, (0.0, 1.0) )
# ==============================================================================
animated_plot( x, y, z, labels["nu"], labels["P_nu"], "$z = {0:7.3f} \, km$", 
               (x[0], x[-1]), (0.0, 1.1), fps = stepper.traces / 5,
               frame_prefix = "nu_", filename = "5-6_animation_nu.avi" )
# ==============================================================================
stepper.storage.reduce_to_range( 46.0, 54.0 )
# ==============================================================================
x = stepper.storage.t
y = [ temporal_power(A) for A in stepper.storage.As ]
z = stepper.storage.z
# ==============================================================================
map_plot( x, y, z, labels["t"], labels["P_t"], labels["z"],
          "lanczos", True, "5-6_map_t.png", 100 )
# ==============================================================================
waterfall_plot( x, y, z, labels["t"], labels["z"], labels["P_t"],
                True, 0.2, "5-6_waterfall_t.png", 100, (0.0, 6.0) )
# ==============================================================================
animated_plot( x, y, z, labels["t"], labels["P_t"], "$z = {0:7.3f} \, km$", 
               (x[0], x[-1]), (0.0, 6.1), fps = stepper.traces / 5,
               frame_prefix = "t_", filename = "5-6_animation_t.avi" )
# ==============================================================================
