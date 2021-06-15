"""Make frames for gif of time-evolution."""

import os
import numpy as np
from landlab import RasterModelGrid, NodeStatus, values
from crater_functions import do_cratering
import matplotlib.pyplot as plt

# fix random seed
np.random.seed(1023)

# Set the colourmap
cmap = "Greys_r"  # old craters in gray (reversed color map)
cmap1 = "Greys" # (Greys, as is - i.e. not reversed)
cmap2 = "Spectral_r" # (Spectral, reversed)

# Define some Variables!
xy = 200  # Set the number of nodes in both x and y space
spacing = 1
zfactor = 10  # set factor to multiply random noise by

# Set up a LandLab model grid object, random topographic noise ~O(zfactor)
mg = RasterModelGrid((xy, xy), xy_spacing=spacing)  # see above for variables
# create an array of zeros for each node of the model grid
z = mg.add_zeros('topographic__elevation', at='node')
# add noise to the surface
noise = values.random(mg, "topographic__elevation", at='node',
                      where=NodeStatus.CORE, distribution='uniform',
                      high=z.max()*0.75, low=z.max()*0.25)
mg.at_node["topographic__elevation"] *= zfactor

# Set the "distribution" as weights, and choose a value from those weights
Kx = 1.0  # Scaling coefficient
delta = 2.0  # km, scaling exponent
#Ncraters = 100  # Number of craters to add
Ncraters = int(input("How many craters do you want to add? ")) # see console to add your own number!
# int(spacing*3) # min diameter (m), xy_spacing times 3
# i.e. more tha 3 cells in diameter
minD = 1
# int((mg.number_of_nodes)/4) #max diameter (m)
# i,e, a quarter of the total domain width
maxD = 100
NDs = []
for D in range(minD, maxD):
    ND = Kx * D ** - delta
    NDs.append(ND)

# make output folder if needed
if os.path.isdir('figs') is False:
    os.mkdir('figs')

# define where section is taken along y
stk = 100

# number of timesteps
nsteps = 10

# set vertical limits of plots (should be based on last timestep elevations)
zmin = -100
zmax = 20

# loop to make time-series frames
fig, ax = plt.subplots(1, 2, dpi=250, facecolor='w', figsize=(8, 3))
topo = mg.field_values('node', 'topographic__elevation').reshape((xy, xy)) #create an array of elevation values across the mg domain
hs = mg.calc_hillshade_at_node(elevs='topographic__elevation') #create a hillshade array
hill = np.reshape(hs, (xy, xy)) #reshape the hillshade array to be the same shape as the topo array
img1 = ax[0].imshow(hill, cmap=cmap1, alpha=1, vmin=zmin, vmax=zmax)
img2 = ax[0].imshow(topo, cmap=cmap2, alpha=0.6, vmin=zmin, vmax=zmax)
ax[0].set_title('Topography overlain on Hillshade')
cbar = plt.colorbar(img2, fraction=0.045, ax=ax[0], label = "Topography [m]")
cbar.set_label('Elevation [m]')
ax[0].set_xlabel('X')
ax[0].set_ylabel('Y')
ax[0].plot(np.linspace(0, xy), np.ones_like(np.linspace(0, xy))*stk,
           c='k', linestyle='--')
ax[0].set_xlim([0, xy])
ax[0].set_ylim([0, xy])

ax[1].plot(topo[stk, :], c=[0, 0, 0])
ax[1].set_title('Topographic Section at Y = ' + str(stk))
ax[1].set_ylabel('Topography [m]')
ax[1].set_xlabel('Distance along X')
ax[1].set_ylim([zmin, zmax])

plt.tight_layout()
plt.savefig('figs/' + '0'.zfill(4) + '.png', bbox_inches='tight')

# store old topo sections
old_arr = np.zeros((nsteps, xy))
old_arr[0, :] = topo[:, stk]

for i in range(1, nsteps):
    # crater landscape
    mg = do_cratering(Ncraters, NDs, minD, maxD, xy, mg, spacing)

    # update plot
    fig, ax = plt.subplots(1, 2, dpi=250, facecolor='w', figsize=(8, 3))
    topo = mg.field_values('node', 'topographic__elevation').reshape((xy, xy)) #create an array of elevation values across the mg domain
    hs = mg.calc_hillshade_at_node(elevs='topographic__elevation') #create a hillshade array
    hill = np.reshape(hs, (xy, xy)) #reshape the hillshade array to be the same shape as the topo array
    img1 = ax[0].imshow(hill, cmap=cmap1, alpha=1, vmin=0, vmax=1)
    img2 = ax[0].imshow(topo, cmap=cmap2, alpha=0.6, vmin=zmin, vmax=zmax)
    ax[0].set_title("Cratered surface evolution (t = %i)" %i)
    cbar = plt.colorbar(img2, fraction=0.045, ax=ax[0], label = "Topography [m]")
    cbar.set_label('Elevation [m]')
    ax[0].set_xlabel('X')
    ax[0].set_ylabel('Y')
    ax[0].plot(np.linspace(0, xy), np.ones_like(np.linspace(0, xy))*stk,
               c='k', linestyle='--')
    ax[0].set_xlim([0, xy])
    ax[0].set_ylim([0, xy])

    ax[1].plot(topo[stk, :], c=[0, 0, 0], zorder=10)
    for j in range(old_arr.shape[0]):
        if np.sum(old_arr[j, :]) != 0:
            ax[1].plot(old_arr[j, :], c=[1-j/nsteps, 1-j/nsteps, 1-j/nsteps])
    ax[1].set_title('Topographic section at Y = ' + str(stk))
    ax[1].set_ylabel('Topography [m]')
    ax[1].set_xlabel('Distance along X')
    ax[1].set_ylim() # I think making a dynamic scale is kind of fun, shows how much it changes? Instead of [zmin, zmax]

    plt.tight_layout()
    plt.savefig('figs/' + '0'.zfill(4) + '.png', bbox_inches='tight')    

    # retain old array section
    old_arr[i, :] = topo[stk, :]
