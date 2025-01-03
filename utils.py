import os

class FANCY_PRINT:
  def __init__(self):
    self.c1 = 0
    self.c2 = 0
    self.c3 = 0
    self.c4 = 0
  
  def update( self, chans ):
    if 1 in chans:
      self.c1 = chans[1]
    if 2 in chans:
      self.c2 = chans[2]
    if 3 in chans:
      self.c3 = chans[3]
    if 4 in chans:
      self.c4 = chans[4]
    
    # print it
    os.system("clear")
    print(f"1: {self.c1} \n 2: {self.c2} \n 3: {self.c3} \n 4: {self.c4} \n" )
  
    
  
  