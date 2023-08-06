
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
system = System( Domain(bit_width = 400.0, samples_per_bit = 4096) )
system.add( Sech(peak_power = 8.8e-3, width = (1.0 / 0.44), position = 0.625) )
system.add( Sech(peak_power = 8.8e-3, width = (1.0 / 0.44), position = 0.375,
                 offset_nu = -0.8) )
system.add( Fibre(length = 400.0, beta = [0.0, 0.0, -0.1, 0.0], 
                  gamma = 2.2, traces = 200, method = 'ARK4IP',
                  local_error = 1e-6) )
system.run()
# ==============================================================================
stepper = system['fibre'].stepper
stepper.storage.reduce_to_range( 140.0, 360.0 )
# ==============================================================================
x = stepper.storage.t
y = [ temporal_power(A) for A in stepper.storage.As ]
z = stepper.storage.z
# ==============================================================================
step_sizes = stepper.storage.step_sizes
distances = [s[0] for s in step_sizes]
steps = [s[1] for s in step_sizes]
# ==============================================================================
print len(distances)
print len(steps)
# ==============================================================================
single_plot( distances, steps, labels["z"], "Step size, h (km)", 
             filename = "steps.png" )

map_plot( x, y, z, labels["t"], labels["P_t"], labels["z"],
          filename = "map.png" )

waterfall_plot( x, y, z, labels["t"], labels["z"], labels["P_t"],
                use_poly = True, filename = "waterfall.png",
                y_range = (0.0, 0.02) )
# ==============================================================================
