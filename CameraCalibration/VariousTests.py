import glob
import os
import random

generalPath = 'CalibrationImagesSet'+ '/*.' +'jpg'
print(os.getcwd())
print(generalPath)
y = glob.glob(generalPath)
x =  random.choice(y)
print(x)