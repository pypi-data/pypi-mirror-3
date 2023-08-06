
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

import matplotlib.pyplot as plt
import numpy as np
import os.path
from itertools import cycle
# ==============================================================================
methods = [ "SSFM", "SSFM_REDUCED", "SSFM_SYM", "SSFM_SYM_MIDPOINT", \
            "SSFM_SYM_RK4", "SSFM_SYM_RKF", "RK4IP" ]

data_directory = "data_soliton"
# ==============================================================================
# Generate a range of line and mark styles to cycle through:
lines = [ "-", ":", "--" ]
line_cycler = cycle( lines )

#~marks = [ "v", "<", ">", "^", "*" ]
marks = [ "*", "o", "s", "D", "^" ]
mark_cycler = cycle( marks )
# ==============================================================================
x_label = "Number of steps"
y_label = "Average relative error"
# ==============================================================================
for method in methods:
   steps = []
   results = []
   # ===========================================================================
   filename = ".".join( (str(method),"dat") )
   filename = os.path.join( data_directory, filename )
   with open( filename, "r" ) as f:
      lines = f.readlines()
      # remove title line:
      del lines[0]
      for line in lines:
         elements = line.split("\t")
         steps.append( elements[0] )
         results.append( float(elements[-1]) )
   # ===========================================================================
   plt.xlabel( x_label )
   plt.ylabel( y_label )

   plt.plot( steps, results, label = method.lower(), \
             linestyle = next(line_cycler), marker = next(mark_cycler) )
# ==============================================================================
plt.legend( loc = "upper center", bbox_to_anchor = (0.5, 1.3), \
            fancybox = True, shadow = True, ncol = int(len(methods) / 2) )

plt.legend( loc = "lower left", frameon = False, prop = {"size":14} )

plt.xscale( "log" )
plt.yscale( "log" )
#~plt.tight_layout()
#~plt.show()
plt.savefig( "soliton_error_vs_steps.png" )
# ==============================================================================
