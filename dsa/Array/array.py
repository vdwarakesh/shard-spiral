# An Array stores elements sequentially in contiguous memory.
# In Python, standard built-in lists act as dynamic arrays that can hold elements of any data type (integers, strings, objects, etc.).
arr = [10, 20, 30, 40, 50]

# For strict, homogeneous (single data type) contiguous memory arrays in Python, the built-in 'array' module is used ('i' represents signed integers, but you can also use 'f' for floats, 'd' for doubles, etc.).
import array
homogeneous_arr = array.array('i', [10, 20, 30, 40, 50])