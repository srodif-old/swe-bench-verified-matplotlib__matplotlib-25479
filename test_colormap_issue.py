#!/usr/bin/env python3
"""
Test script to reproduce the colormap name handling issue.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

print(f"Matplotlib version: {matplotlib.__version__}")

# Create test data for colormap
my_cmap_data = [[1.5e-03, 4.7e-04, 1.4e-02],
                [2.3e-03, 1.3e-03, 1.8e-02],
                [3.3e-03, 2.3e-03, 2.4e-02]]

# Create the colormap with name 'some_cmap_name'
my_cmap = LinearSegmentedColormap.from_list('some_cmap_name', my_cmap_data)
print(f"Created colormap with name: {my_cmap.name}")

# Register the colormap with a different name 'my_cmap_name'
cm.register_cmap(name='my_cmap_name', cmap=my_cmap)
print("Registered colormap with name: 'my_cmap_name'")

# Try to get the colormap by registered name - this should work
try:
    retrieved_cmap = cm.get_cmap('my_cmap_name')
    print(f"Successfully retrieved colormap: {retrieved_cmap.name}")
except Exception as e:
    print(f"Error retrieving colormap: {e}")

# Set the default colormap - this should work
try:
    plt.set_cmap('my_cmap_name')
    print("Successfully set default colormap")
except Exception as e:
    print(f"Error setting default colormap: {e}")

# This is where the issue occurs - trying to use the colormap
# should fail because it looks for 'some_cmap_name' instead of 'my_cmap_name'
try:
    fig, ax = plt.subplots()
    im = ax.imshow([[1, 1], [2, 2]])
    print("Successfully created image with colormap")
    plt.close(fig)
except Exception as e:
    print(f"Error creating image: {e}")
    # Show that the colormap exists in the registry
    print(f"Available colormaps include: {list(cm._colormaps)[-10:]}")
    print(f"'my_cmap_name' in colormaps: {'my_cmap_name' in cm._colormaps}")
    print(f"'some_cmap_name' in colormaps: {'some_cmap_name' in cm._colormaps}")