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
      self.index      = index
      self.colour     = colour
      # index into the particular hazard sprite set
      self.sprite_idx = -1
      # speccy graphical coordinates
      self.pos        = pos
      # entrance delay
      self.delay      = 0

class jack_t:
   def __init__ (self, state, pos, delay):
      # index into the jack_se list
      #    0 = standing, 1 = moving left, 2 = moving right
      #    3 = jump, 4 = stars, 5 = crash, 6 = fall
      #    7 = second part of the jump,
      #    8 = second part of the fall
      #    9 = moving thro left edge
      #   10 = moving thro right edge
      self.state        = state
      # index into the particular jack sprite set
      self.sprite_idx   = 0
      # speccy graphical coordinates
      self.pos          = pos
      self.lives        = 6
      self.score        = 0
      self.level        = 0
      self.next         = False
      self.timeout      = 0
      self.delay        = delay

class sounds_t:
   def __init__ (self):
      self.fall_thro = None
      self.ff_head = None
      self.game_end = None
      self.jump_thro = None
      self.line_crash = None
      self.lr_head = None
      self.new_level = None
      self.run = None
      self.squash = None
      self.stars = None
