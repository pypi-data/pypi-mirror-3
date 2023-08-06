
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
system = System( Domain(bit_width = 600.0, samples_per_bit = 4096) )
system.add( Gaussian(peak_power = 1.0, width = 1.0, m = 3) )
system.add( Fibre(length = 6.0, beta = [0.0, 0.0, 0.0, 1.0],
                  traces = 200, method = 'RK4IP') )
system.run()
# ==============================================================================
stepper = system['fibre'].stepper
stepper.storage.reduce_to_range( 290.0, 340.0 )
# ==============================================================================
x = stepper.storage.t
y = [ temporal_power(A) for A in stepper.storage.As ]
z = stepper.storage.z
# ==============================================================================
map_plot( x, y, z, labels["t"], labels["P_t"], labels["z"],
          "lanczos", True, "3-7_map.png", 100 )
# ==============================================================================
waterfall_plot( x, y, z, labels["t"], labels["z"], labels["P_t"],
                True, 0.2, "3-7_waterfall.png", 100 )
# ==============================================================================
animated_plot( x, y, z, labels["t"], labels["P_t"], "$z = {0:7.3f} \, km$",
               (290.0, 320.0), (0.0, 1.6), fps = stepper.traces / 10,
               frame_prefix = "t_", filename = "3-7_animation.avi" )
# ==============================================================================
