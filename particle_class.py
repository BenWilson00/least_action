#######################################################
# Does most of the heavy lifting from path_integral.py
#######################################################

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import colourmap as cmap
import time

class Particle:

  def __init__(self, T_a, V_a, path_range, **kwargs):

    # Assign basic variables
    self.T = T_a
    self.V = V_a
    self.path_range = path_range
    self.history = [[], []]


    # Set up kwargs
    self.startpos = 0+0j
    self.timestep = 10
    self.show_extras = True
    self.show_pos_only = False
    self.repeat = False
    self.cum_colourmap = False
    self.fullscreen = False
    plots_shown = [True, True, False, True]
    self.axes_shown = [True, False, False, True]
    self.n_paths = 30
    self.stop_time = 0
    self.path_coords = ((-1, 0), (1, 0))

    if "startpos" in kwargs: self.startpos = kwargs["startpos"]
    if "timestep" in kwargs: self.timestep = kwargs["timestep"]
    if "show_extras" in kwargs: self.show_extras = kwargs["show_extras"]
    if "show_pos_only" in kwargs: self.show_pos_only = kwargs["show_pos_only"]
    if "repeat" in kwargs: self.repeat = kwargs["repeat"]
    if "colourmap" in kwargs: self.cum_colourmap = kwargs["colourmap"]
    if "fullscreen" in kwargs: self.fullscreen = kwargs["fullscreen"]
    if "plots" in kwargs: plots_shown = kwargs["plots"]
    if "axes" in kwargs: self.axes_shown = kwargs["axes"]
    if "n_paths" in kwargs: self.n_paths = kwargs["n_paths"]
    if "stop_time" in kwargs: self.stop_time = kwargs["stop_time"] 
    if "path_coords" in kwargs: self.path_coords = kwargs["path_coords"]

    if not any(plots_shown):
      print "no plots shown"
      exit()

    # Run to completion to find out what graph bounds should be
    min_x, max_x = self.startpos.real, self.startpos.real
    min_y, max_y = self.startpos.imag, self.startpos.imag

    for i, pos, a, b, c in self.pos_gen():
      min_x = min(pos.real, min_x)
      max_x = max(pos.real, max_x)
      min_y = min(pos.imag, min_y)
      max_y = max(pos.imag, max_y)

    min_x -= 0.1*(max_x-min_x)
    max_x += 0.1*(max_x-min_x)
    min_y -= 0.1*(max_y-min_y)
    max_y += 0.1*(max_y-min_y)



    # Set up colour map

    action_arr = [self.action(path) for path in self.path_range]
    
    d_action = [(action_arr[i]-action_arr[i-1]) for i in range(1, len(self.path_range))]
    
    min_da, max_da, zero_point = min(d_action), max(d_action), min([abs(i) for i in d_action])

    range_da = max(abs(max_da - zero_point), abs(zero_point - min_da))
    
    n_colours = cmap.LEN-1
    
    scale_factor = n_colours/range_da

    self.get_path_colour = lambda i: cmap.green_yellow[max(100, int(cmap.LEN- 0.5 - scale_factor*abs(d_action[max(0, i-1)])))]


    # Set up function to tell which paths to draw

    approx_steps_per_path_draw = int(len(self.path_range)/self.n_paths)
    self.true_if_draw_path = lambda step: step%approx_steps_per_path_draw==0


    # Initialise the right number of plots

    self.axarr = plots_shown
    n_plots = sum(plots_shown)
    print n_plots

    if n_plots < 4:
      self.fig, axarr1 = plt.subplots(1, n_plots)

      if type(axarr1) != np.ndarray: axarr1 = [axarr1]
      j = 0
      for i in range(4):

        if self.axarr[i]:

          self.axarr[i] = axarr1[j]
          j += 1

    else:
      self.fig, axarr1 = plt.subplots(2, 2)
      self.axarr = [
        axarr1[0, 0], axarr1[0, 1],
        axarr1[1, 0], axarr1[1, 1]
      ]


    # Hide axes if requested

    for i in range(len(self.axarr)):
      if not self.axes_shown[i] and self.axarr[i]: self.axarr[i].set_axis_off()



    # Set up requested plots

    self.lines0 = ()
    if self.axarr[0]:    
      # Cumulative phase plot

      self.lines0 += (
        self.axarr[0].plot([], [], "ko")[0],
      )

      if not self.cum_colourmap:
        self.lines0 += (self.axarr[0].plot([], [], lw=2)[0],)
      
      self.axarr[0].set_title("Cumulative Propagator Phase")
      self.axarr[0].set_ylim(min_y, max_y)
      self.axarr[0].set_xlim(min_x, max_x)

    self.lines1 = ()
    if self.axarr[1]:   
      # Phase diagram plot

      self.axarr[1].set_title("Current Propagator Phase")

      self.axarr[1].axis("equal")

      self.lines1 += (
        self.axarr[1].plot([], [], "k", lw=4)[0],
        self.axarr[1].plot([1.5, 1.5], [-1, 1],  "r--", lw=1)[0],
        self.axarr[1].plot([-1, 1], [-1.5, -1.5], "r--", lw=1)[0],
        self.axarr[1].plot([], [], "k--", lw=1)[0],
        self.axarr[1].plot([], [], "k--", lw=1)[0],
        self.axarr[1].plot([], [], "ko")[0]
      )

      circle1 = plt.Circle((0, 0), 1, fill=False, lw=1, color="k")
      self.axarr[1].add_artist(circle1)

      self.axarr[1].set_ylim(-2,   1.5)
      self.axarr[1].set_xlim(-1.5, 2)

    self.lines2 = ()
    if self.axarr[2]:
      # Path plot

      self.axarr[2].set_title("Paths Used")

      self.axarr[2].set_ylim(self.path_range[0]*0.9-self.path_range[-1]*0.1, self.path_range[-1]*1.1 - self.path_range[0]*0.1)
      self.axarr[2].set_xlim(-1.5, 1.5)

    self.lines3 = ()
    if self.axarr[3]:
      # Action vs path plot

      self.axarr[3].set_title("Action vs. Path")

      self.lines3 += (
        self.axarr[3].plot(self.path_range, self.action(self.path_range), "g", lw=2)[0],
        self.axarr[3].plot([], [], "ko")[0]
      )



  def get_path_colour(self, path):
    pass


  def lines(self):
    return self.lines0 + self.lines1 + self.lines2 + self.lines3


    
  def action(self, path):
    return self.T(path) - self.V(path)


  def pos_gen(self):
    '''
    Generator function yielding cumulative position
    (& some other values since they're already calculated)
    '''
    pos = self.startpos

    for i in range(len(self.path_range)):

      path = self.path_range[i]
      action = self.action(path)
      action_exp = np.exp(1j*action)
      pos += action_exp

      yield i, pos, action_exp, action, path

  def run(self, data):

    i, newpos, action_exp, action, path = data

    if self.axarr[0]:
      # Cumulative phase plot
      self.history[0].append(newpos.real)
      self.history[1].append(newpos.imag)

      if self.cum_colourmap:
        if i == 0:
          self.lines0 = self.lines0[:1]
        new_line, = self.axarr[0].plot(self.history[0][-2:], self.history[1][-2:], color=self.get_path_colour(i), lw=4)
        self.lines0 += (new_line,)

      else:
        self.lines0[1].set_data(self.history)

      if i == len(self.path_range) - 1:
        self.lines0[0].set_data(-1e10, -1e10)

      else:
        self.lines0[0].set_data(newpos.real, newpos.imag)


    if self.axarr[1]:
      # Phase plot
      self.lines1[0].set_data([[0, action_exp.real], [0, action_exp.imag]])
      self.lines1[0].set_color(self.get_path_colour(i))
      self.lines1[3].set_data([action_exp.real, action_exp.real], [-1.5, action_exp.imag])
      self.lines1[4].set_data([1.5, action_exp.real], [action_exp.imag, action_exp.imag])
      self.lines1[5].set_data([[action_exp.real, 1.5, action_exp.real], [action_exp.imag, action_exp.imag, -1.5]])
      

    if self.axarr[2]:
      # Path plot


      if i == 0:
        self.lines2 = ()
      
      if self.true_if_draw_path(i):

        if i > 0:
          self.lines2[-1].set_color(self.prev_line_colour)

        new_line, = self.axarr[2].plot([self.path_coords[0][0], 0, self.path_coords[1][0]], [self.path_coords[0][1], path, self.path_coords[1][1]], "r")
        
        self.prev_line_colour = self.get_path_colour(i)
        self.lines2 += (new_line,)


    if self.axarr[3]:
      # Action plot
      self.lines3[1].set_data([path, self.action(path)])

    return self.lines()


  def animate(self):
    '''
    Run animation
    '''

    self.ani = animation.FuncAnimation(self.fig, 
      self.run, self.pos_gen, blit=True, 
      interval=self.timestep, repeat=self.repeat)

    if self.fullscreen:
      figManager = plt.get_current_fig_manager()
      figManager.window.showMaximized()

    plt.show()



  def save(self, savename, _fps=30):

    self.ani = animation.FuncAnimation(self.fig, 
      self.run, self.pos_gen, blit=True, 
      interval=self.timestep, repeat=self.repeat)

    print "saving to", savename
    Writer = animation.writers["ffmpeg"]
    writer = Writer(fps=5)
    self.ani.save(savename, writer=writer)
    print "Saved successfully"