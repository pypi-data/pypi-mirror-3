
import numpy as np

d1 = map(lambda x: np.array([[5,6]]), xrange(0, 4))
d2 = map(lambda x: np.array([[1,2]]), xrange(0, 4))
print map(lambda (x, y): np.vstack((x,y)) if len(x) else y, 
          zip(d1, d2))
print map(len, d1)
