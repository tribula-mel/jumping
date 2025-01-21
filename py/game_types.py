from enum import Enum

class colour_t (Enum):
   blue    = 0x01
   red     = 0x02
   magenta = 0x03
   green   = 0x04
   cyan    = 0x05
   yellow  = 0x06
   white   = 0x07
   black   = 0x08

class sprite_t:
   def __init__ (self, width, height, colour, sprite):
      self.width  = width
      self.height = height
      self.colour = colour
      self.sprite = sprite

class hazard_t:
   def __init__ (self, index, colour, pos):
      # index into the hazards list
      self.index  = index
      self.colour = colour
      # index into the particular hazard sprite set
      self.sprite_idx = 0
      # speccy graphical coordinates
      self.pos    = pos
