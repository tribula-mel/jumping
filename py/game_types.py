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
