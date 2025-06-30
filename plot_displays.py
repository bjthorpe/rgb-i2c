import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
from manager import process_data
from display import Display
from parameters import DEFAULT_I2C_ADDR
import pickle
def get_sim_displays(layout=None):
    from numpy import ceil, sqrt
    if layout is not None:
        if isinstance(layout, int):
            layout = (layout,)  # If a single number is supplied, turn it into a tuple.
        else:
            assert isinstance(layout, tuple)
            assert all(isinstance(i, int) for i in layout)

    addresses = [DEFAULT_I2C_ADDR]

    # If a layout was supplied, ensure we have at least enough devices.
    if layout is not None:
        if len(addresses) < sum(layout):
                addresses *= 1 + sum(layout) // len(addresses)  # Duplicate addresses until we have enough.

        # We only keep the addresses that are needed if a layout is supplied.
        addresses = addresses[:sum(layout)]

    else:  # Just create a dummy layout if none was supplied.
        layout = (len(addresses),)

    # Let's now create the Display objects.
    displays = []

    # The side, X and Y data for each display.
    coordinates = [[divmod(n, int(ceil(sqrt(side_size)))) for n in range(side_size)] for side_size in layout]

    current_ID = 0

    for (side, YXs) in enumerate(coordinates):
        for Y, X in YXs:  # divmod() gives (Y, X) co-ordinates so need to be careful.
            displays.append(Display(side=side, X=X, Y=Y, ID=current_ID, address=addresses[current_ID]))
            current_ID += 1

    return displays

def update(i, pixels,event):
    """
    Update the pixel values based on the provided data.
    
    Parameters:
    i (int): Index of the current data point.
    data (DataFrame): Data containing 'x', 'y', and 'energy' columns.
    data_raw (DataFrame): Raw data containing 'energy' column for maximum value.
    """
    pos_y = [0,0,8,8]
    pos_x = [0,8,0,8]

    for k, disp_ID in enumerate(event[i].display_IDs):
        det_x = event[i].x_values[k] + pos_x[(disp_ID % 4)]
        det_y = event[i].y_values[k] + pos_y[(disp_ID % 4)]
        det_ID=int(np.floor(disp_ID)/4)
# Update the pixel at the specified coordinates with the energy value
        pixels[det_ID][det_x,det_y] = event[i].colors[k]

    for j,disp in enumerate(pixels):
        ax[j].imshow(pixels[j], interpolation="nearest", origin="upper",cmap='jet',vmax=255)
    return 


def draw_screen(ax,layout=(4,4)):
    from matplotlib.patches import Rectangle

    for screen_id in range(len(layout)*2):
        ax[screen_id].set_xlim(-1, 16 + 1)
        ax[screen_id].set_ylim(-1, 16 + 1)
        ax[screen_id].set_aspect('equal')
        # Draw the screen

        for i in range(2):
            for j in range(2):
                bound_x = i * 8
                bound_y = j * 8
                screen = Rectangle((bound_x, bound_y), 8, 8, linewidth=1, edgecolor='black', facecolor='none')
                ax[screen_id].add_patch(screen)
        # set title ect..
        ax[screen_id].set_title(f'Detector {screen_id + 1}')
        ax[screen_id].axis('off')  # Hide axes


# pixels=[np.zeros((16,16))]
if __name__=='__main__':
    layout = (4,4,4,4,4,4)

    pixels = []  # List to hold pixel arrays for each screen
    for i in range(len(layout)*2):
        # Create a 16x16 pixel array for each screen
        # Initialize with zeros (black)
        pixels.append(np.zeros((16,16)))

    file_ = 'test_data/big.csv'  # Data file.
    
    force_displays = False  # If we request more displays than addresses found, should we reuse displays anyway?

    displays = get_sim_displays(layout=layout)
    # process data into stream of events

   # data = process_data(file_, displays, mode='normal', energy_method='tick', normalise=True)
    print ('loading data from Processed_data/example1')
    dbfile = open('Processed_data/example1', 'rb')    
    data = pickle.load(dbfile)
    dbfile.close()
    print ('Data loaded')
    #setup plots 
    fig, ax = plt.subplots(1,len(layout)*2, figsize=(8,8))

    draw_screen(ax,layout=layout)

    ani = animation.FuncAnimation(fig, update, len(data), interval=2000, fargs=[pixels,data], blit=False,repeat=True)
    plt.show()
    # save as animated gif
    #ani.save('animation_drawing.gif', writer='imagemagick',fps=1)

