from manager import run


# Temporary data file for testing.
temp_file = 'testingTEMP11.dat'  # Data file.
layout = (1,)  # 1 display for now.
normalise_time_data = True  # Should we re-normalise the times of the data between 0 and 30 sec?

run(temp_file, layout, normalise_time_data)

