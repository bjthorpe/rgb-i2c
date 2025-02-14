from manager import run


# Temporary data file for testing.
temp_file = 'test_data/1.dat'  # Data file.
layout = (1,)  # 1 display for now.
normalise = True  # Should we re-normalise the times of the data to have on avg. 100 data points per 30 sec?

run(temp_file, layout, normalise)

