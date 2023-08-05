import os

my_path = os.path.dirname(__file__)
data_path = os.path.join(my_path, 'data.py')

with open(data_path, 'wb') as fh:
    pass # Do writing stuff to fhs
    
print my_path
print data_path
