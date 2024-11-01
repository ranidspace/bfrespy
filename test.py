from bfrespy.switch import ResFile
from bfrespy.switch.core import ResFileLoader

test = open('Brd_Sparrow01.bfres', 'rb')
ResFile(test.read())
print("done")