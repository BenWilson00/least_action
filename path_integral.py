##################################################
# Demonstrate how the classical least-action
# principle arises from propagator path integrals
# in Feynman's formulation of quantum mechanics 
##################################################


from particle_class import Particle
import numpy as np
import time

MIN_PATH = 0
MAX_PATH = 1
STEPS = 200                # > 1
T = 1
Y = 1
X = 1
V0 = 10
V1 = 6.66
h = 5.0


p1 = Particle(
  # Kinetic energy (function of path):
  lambda x: 20*(np.sqrt(Y**2 + x**2)*V0 + np.sqrt(Y**2 + (X-x)**2)*V1),
  # Potential energy (function of path): 
  lambda path: 0,
  # Path space            
  np.linspace(MIN_PATH, MAX_PATH, STEPS),
  # Optional arguments
  show_extras = True,
  show_pos_only = False,
  timestep = 20, #ms
  repeat = True,
  colourmap = True,
  fullscreen = False,
  axes = [True, False, False, True],
  plots = [True]*4,
  # stop_time = 1,
  path_coords = ((-1, 1), (1, 0))
)

p1.animate()
#p1.save("test.mp4", 60)