#!/usr/bin/env python3
"""
Test script to verify the colormap name handling fix.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

# Mock numpy since we can't install it due to network issues
class MockArray:
    def __init__(self, data):
        self.data = data
        
    def __iter__(self):
        return iter(self.data)
        
    def __getitem__(self, key):
        return self.data[key]

class MockNumpy:
    def __init__(self):
        pass
    
    @property
    def ma(self):
        return self
        
    def array(self, data):
        return MockArray(data)
        
    def linspace(self, start, stop, num):
        return MockArray([start + i * (stop - start) / (num - 1) for i in range(num)])
        
    def ones(self, shape):
        if isinstance(shape, tuple):
            size = 1
            for s in shape:
                size *= s
        else:
            size = shape
        return MockArray([1.0] * size)
        
    def zeros(self, shape):
        if isinstance(shape, tuple):
            size = 1
            for s in shape:
                size *= s
        else:
            size = shape
        return MockArray([0.0] * size)

# Mock matplotlib dependencies
sys.modules['numpy'] = MockNumpy()
sys.modules['numpy.ma'] = MockNumpy()

# Import matplotlib after mocking numpy
try:
    from matplotlib import cm
    from matplotlib.colors import LinearSegmentedColormap
    import matplotlib.pyplot as plt
    import matplotlib
    print(f"Successfully imported matplotlib")
except Exception as e:
    print(f"Error importing matplotlib: {e}")
    exit(1)

def test_colormap_name_handling():
    """Test that registered colormap names work correctly with set_cmap."""
    
    # Create test data for colormap
    my_cmap_data = [[1.5e-03, 4.7e-04, 1.4e-02],
                    [2.3e-03, 1.3e-03, 1.8e-02],
                    [3.3e-03, 2.3e-03, 2.4e-02]]

    # Create the colormap with name 'some_cmap_name'
    my_cmap = LinearSegmentedColormap.from_list('some_cmap_name', my_cmap_data)
    print(f"Created colormap with internal name: {my_cmap.name}")

    # Register the colormap with a different name 'my_cmap_name'
    with warnings_captured() as w:
        cm.register_cmap(name='my_cmap_name', cmap=my_cmap)
    print("Registered colormap with name: 'my_cmap_name'")

    # Verify we can retrieve the colormap by registered name
    try:
        retrieved_cmap = cm.get_cmap('my_cmap_name')
        print(f"Successfully retrieved colormap by registered name: {retrieved_cmap.name}")
    except Exception as e:
        print(f"ERROR: Could not retrieve colormap by registered name: {e}")
        return False

    # Test setting the colormap as default - this is the main fix
    try:
        plt.set_cmap('my_cmap_name')
        print("Successfully set default colormap using registered name")
    except Exception as e:
        print(f"ERROR: Could not set default colormap: {e}")
        return False

    # Check that rcParams was set correctly
    current_cmap = matplotlib.rcParams['image.cmap']
    print(f"Current default colormap in rcParams: '{current_cmap}'")
    
    # Verify that the default colormap name can be found in the registry
    if current_cmap in cm._colormaps:
        print(f"SUCCESS: Default colormap '{current_cmap}' exists in registry")
        return True
    else:
        print(f"ERROR: Default colormap '{current_cmap}' not found in registry")
        print(f"Available colormaps: {list(cm._colormaps.keys())[-10:]}")
        return False

class warnings_captured:
    """Simple context manager to capture warnings"""
    def __enter__(self):
        return []
    
    def __exit__(self, *args):
        pass

if __name__ == "__main__":
    success = test_colormap_name_handling()
    if success:
        print("\n✅ Test PASSED: Colormap name handling works correctly!")
    else:
        print("\n❌ Test FAILED: Colormap name handling is broken!")
    exit(0 if success else 1)