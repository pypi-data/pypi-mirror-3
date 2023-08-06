
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
                  gamma = 2.2, total_steps = 400, traces = 100,
                  method = 'ARK4IP', local_error = 1e-6) )
system.run()
# ==============================================================================
storage = system['fibre'].stepper.storage
(x, y, z) = storage.get_plot_data( reduced_range = (140.0, 360.0) )
# ==============================================================================
# Split step_sizes (list of tuples) into separate lists; distances and steps:
(distances, steps) = zip( *storage.step_sizes )
# ==============================================================================
print np.sum( steps)
# ==============================================================================
single_plot( distances, steps, labels["z"], "Step size, h (km)", 
             filename = "steps" )
# ==============================================================================
map_plot( x, y, z, labels["t"], labels["P_t"], labels["z"],
          filename = "map" )
# ==============================================================================
waterfall_plot( x, y, z, labels["t"], labels["z"], labels["P_t"],
                filename = "waterfall", y_range = (0.0, 0.02) )
# ==============================================================================
