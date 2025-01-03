import os

class FANCY_PRINT:
  def __init__(self):
    self.c1 = 0
    self.c2 = 0
    self.c3 = 0
    self.c4 = 0
  
  def update( self, chans ):
    if chans[1]:
      self.c1 = chans[1]
    elif chans[2]:
      self.c2 = chans[2]
    elif chans[3]:
      self.c3 = chans[3]
    elif chans[4]:
      self.c4 = chans[4]
    os.system("clear")
    print(f"1: {self.c1} \n 2: {self.c2} \n 3: {self.c3} \n 4: {self.c4} \n" )
  
    
  
  