from numpy import *
from tables import *

# Open a new empty HDF5 file
fileh = openFile("array2.h5", mode = "w")
# Shortcut to the root group
root = fileh.root

# Create an array
a = array([1, 2.7182818284590451, 3.141592], float)
print "About to write array:", a
print "  with shape: ==>", a.shape
print "  and dtype ==>", a.dtype

# Save it on the HDF5 file
hdfarray = fileh.createArray(root, 'carray', a, "Float array")

# Get metadata on the previously saved array
print
print "Info on the object:", repr(root.carray)

# Close the file
fileh.close()

# Open the previous HDF5 file in read-only mode
fileh = openFile("array2.h5", mode = "r")
# Get the root group
root = fileh.root

# Get metadata on the previously saved array
print
print "Info on the object:", repr(root.carray)

# Get the actual array
b = root.carray.read()
print
print "Array read from file:", b
print "  with shape: ==>", b.shape
print "  and dtype ==>", b.dtype

# Close the file
fileh.close()
