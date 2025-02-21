from manager import run


# Temporary data file for testing.
temp_file = 'test_data/3.dat'  # Data file.
layout = (1,)  # 1 display for now.
force_displays = False  # If we request more displays than addresses found, should we reuse displays anyway?
normalise = False  # Should we re-normalise the times of the data to have on avg. 100 data points per 30 sec?

run(file_=temp_file, layout=layout, force_displays=force_displays, normalise=normalise)

