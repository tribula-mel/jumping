#!/usr/bin/python3

import pygame
import random

from game_types import colour_t
from game_types import hazard_t
from gfx_sprites import *

scale = 3

DOTS_PER_PIXEL_X = 1
DOTS_PER_PIXEL_Y = 1

# speccy's original screen is 256*192 (32x24 chars)
x_res = DOTS_PER_PIXEL_X * 256
y_res = DOTS_PER_PIXEL_Y * 192

clock = None
pause = False
font  = None

# do not cross the line :) , but embed gaps within
# there are eight lines with maximum of eight gaps
# two for starters; the eight lines are internaly
#    presented as one line; since we are moving half
#    a character this means 32*2*8 = 512 positions
#    within the line, which is 32*8*8 spectrum dots
#    long (2048)
# each gap is three speccy chars long
# holders for the gaps; each gap is presented with a single
#    integer (random starting value) within [0..511] range
left_up_gap = []
right_down_gap = []

# index for hazard_sprites list [1..10]
next_hazard = 0
# index for hazard_colour list [1..8]
next_colour = 0
# possible positions [1..31]
#    divided in 8 chars chunks
next_position = 0
# hazard list; first level has no hazards, level 21 has 20 hazards
hazard_list = []

# linear pseudo random generator in range [1..f]
def lfsr (inp):
   newbit = (((inp >> 3) ^ (inp >> 2)) & 1)
   return ((inp << 1) | newbit) & 0x0f

# linear pseudo random generator in range [1..1f]
def lfsr_1f (inp):
   newbit = (((inp >> 4) ^ (inp >> 2)) & 1)
   return ((inp << 1) | newbit) & 0x1f

def init_hazards ():
   global next_hazard
   global next_colour
   global next_position
   next_hazard = random.randint (1, 10)
   next_colour = random.randint (1, 6)
   next_position = random.randint (1, 31)

def get_index ():
   global next_hazard
   next_hazard = lfsr (next_hazard)
   while next_hazard > 10:
      next_hazard = lfsr (next_hazard)
   return next_hazard

# any colour you like
def get_colour ():
   global next_colour
   next_colour = lfsr (next_colour)
   while next_colour > 6:
      next_colour = lfsr (next_colour)
   return next_colour

# returns random (x, y) tupple in speccy graphical system
def get_position ():
   global next_position
   next_position = lfsr_1f (next_position)
   if next_position > 28:
      (x, y) = get_position ()
      return (x, y)
   # speccy has 32x24 big console
   # a hazard is moving on a line 32x7 chars long
   #    one char at a time to the left
   # each hazard gets 8 chars space
   #    and a bit of randomness
   cal = next_position - 1
   x = 8 * ( ( (8*cal) & 0x1f) + random.randint (0, 5) )
   y = 24 * (int (cal / 4)) + 8
   return (x, y)

# jumping jack x offset to pygame
def x_convert_to_pygame (x):
   global scale
   return DOTS_PER_PIXEL_X * scale * x

# jumping jack y offset to pygame
def y_convert_to_pygame (y):
   global scale
   return DOTS_PER_PIXEL_Y * scale * y

def set_colour (colour):
   if colour == colour_t.yellow.value:
      return (0xff, 0xff, 0x80)
   elif colour == colour_t.magenta.value:
      return (0xff, 0x00, 0xff)
   elif colour == colour_t.cyan.value:
      return (0x00, 0xff, 0xff)
   elif colour == colour_t.green.value:
      return (0x00, 0x80, 0x00)
   elif colour == colour_t.white.value:
      return (0xff, 0xff, 0xff)
   elif colour == colour_t.red.value:
      return (0xff, 0x00, 0x00)
   elif colour == colour_t.blue.value:
      return (0x80, 0x80, 0xff)
   else:
      # black
      return (0x00, 0x00, 0x00)

def draw_element (screen, element, x, y, colour):
   global x_res
   global scale
   index = 0
   x_backup = x
   mask = 0x80
   for i in range (0, element.height):
      for j in range (0, element.width):
         for k in range (0, 8):
            if element.sprite[index] & mask:
               w = DOTS_PER_PIXEL_X * scale
               h = DOTS_PER_PIXEL_Y * scale
               # True part of the if is jumping jack specific
               if x > (x_res * scale - 1):
                  pygame.draw.rect(screen, colour,
                     [x%(x_res*scale), y+y_convert_to_pygame (24), w, h])
               else:
                  pygame.draw.rect(screen, colour, [x, y, w, h])
            x += DOTS_PER_PIXEL_X * scale
            mask = mask >> 1
         mask = 0x80
         index += 1
      x = x_backup
      y += DOTS_PER_PIXEL_Y * scale

def draw_line (screen):
   # there are 8 lines, each 256 dots long
   # since 8 dots are drawn in one go, we have
   #    32 line brick elements per line
   for i in range (0, 8):
      y = y_convert_to_pygame (24 * i)
      for j in range (0, 32):
         x = x_convert_to_pygame (8 * j)
         draw_element (screen, line_brick, x, y, set_colour (0x02))

def draw_lives (screen):
   y = y_convert_to_pygame (176)
   for i in range (0, 6):
      x = x_convert_to_pygame (8* i)
      draw_element (screen, life, x, y, set_colour (0x03))

frames = 0
def draw_jack (screen):
   global frames
   x = x_convert_to_pygame (80)
   y = y_convert_to_pygame (176)
   if frames >= 120:
      frames = 0
   if frames < 30:
      draw_element (screen, jack_ff, x, y, set_colour (0x00))
   elif frames < 60:
      draw_element (screen, jack_lf, x, y, set_colour (0x00))
   elif frames < 90:
      draw_element (screen, jack_ff, x, y, set_colour (0x00))
   elif frames < 120:
      draw_element (screen, jack_rf, x, y, set_colour (0x00))
   frames += 1

def title_loop (screen):
   global pause
   init_gaps ()
   init_hazards ()
   while do_events ([pygame.QUIT, pygame.KEYDOWN],
         [pygame.K_ESCAPE, pygame.K_s, pygame.K_g, pygame.K_p, pygame.K_h]):
      screen.fill ((255, 255, 255))
      draw_line (screen)
      draw_lives (screen)
      draw_gaps (screen)
      draw_hazards (screen)
      draw_score (screen)
      draw_jack (screen)
      pygame.display.flip ()
      move_gaps ()
      move_hazards ()
      clock.tick (30) # limits FPS

def do_events (events, keys):
   global pause
   for event in pygame.event.get ():
      for et in events:
         if event.type == pygame.QUIT and et == pygame.QUIT:
            exit ()
         elif event.type == pygame.KEYDOWN and et == pygame.KEYDOWN:
            for ke in keys:
               if event.key == pygame.K_ESCAPE and ke == pygame.K_ESCAPE:
                  exit ()
               if event.key == pygame.K_t and ke == pygame.K_t:
                  print ('t')
               if event.key == pygame.K_n and ke == pygame.K_n:
                  print ('n')
               if event.key == pygame.K_s and ke == pygame.K_s:
                  return False
               if event.key == pygame.K_g and ke == pygame.K_g:
                  add_gap ()
               if event.key == pygame.K_p and ke == pygame.K_p:
                  if pause == False:
                     pause = True
                  else:
                     pause = False
                  while pause:
                     running = do_events ([pygame.QUIT, pygame.KEYDOWN],
                                          [pygame.K_p])
                     if running == False:
                        return
               if event.key == pygame.K_h and ke == pygame.K_h:
                  add_hazard ()
   return True

def game_keys ():
   keys = pygame.key.get_pressed ()
   if keys[pygame.K_RIGHT]:
      print ('right')
   if keys[pygame.K_LEFT]:
      print ('left')
   if keys[pygame.K_UP]:
      print ('up')
   if keys[pygame.K_DOWN]:
      print ('down')
   if keys[pygame.K_LCTRL]:
      print ('left ctrl')

def game_loop (screen):
   global clock
   while True:
      game_keys ()
      running = do_events ([pygame.QUIT, pygame.KEYDOWN],
                           [pygame.K_ESCAPE, pygame.K_t, pygame.K_n])
      if (running == False):
         break
      screen.fill ((0,0,0))
      pygame.display.flip ()
      clock.tick (35) # limits FPS

def init_gaps ():
   global left_up_gap
   global right_down_gap
   # mask is common for both movements; we want the initial position
   #    to be alligned on the character level
   mask = -1
   mask ^= 0x7
   # both gaps are starting from the same position
   # the gaps will be moving from [0..2023], in four dots steps,
   #    last three positions being needed for the full gap length
   # line is 2048 [0..2047] dots long (32 chars * 8 dots/char * 8 lines)
   # both gaps have origin in the left corner
   init = random.randint (0, 2023)
   init &= mask
   left_up_gap.append ([init, init+8, init+16])
   right_down_gap.append ([init, init+8, init+16])

def add_gap ():
   global left_up_gap
   global right_down_gap
   mask = -1
   mask ^= 0x7
   init = random.randint (0, 2023)
   init &= mask
   if (len (right_down_gap) < 4):
      right_down_gap.append ([init, init+8, init+16])
   elif (len (left_up_gap) < 4):
      left_up_gap.append ([init, init+8, init+16])

def gap_pos_to_speccy_x_y (position):
   # each line has 256 positions, four dots per position
   x = position % 256
   y = int (position / 256) * 24
   return (x, y)

def move_gaps ():
   global left_up_gap
   global right_down_gap
   for i in range (0, len (left_up_gap)):
      x, y, z = left_up_gap[i]
      x = (x - 8) & 0x7ff
      y = (y - 8) & 0x7ff
      z = (z - 8) & 0x7ff
      left_up_gap[i] = [x, y, z]
   for i in range (0, len (right_down_gap)):
      x, y, z = right_down_gap[i]
      x = (x + 8) % 2048
      y = (y + 8) % 2048
      z = (z + 8) % 2048
      right_down_gap[i] = [x, y, z]

def draw_gaps (screen):
   global left_up_gap
   global right_down_gap
   for i in range (0, len (left_up_gap)):
      pos_1, pos_2, pos_3 = left_up_gap[i]
      # every gap is three speccy characters wide
      x, y = gap_pos_to_speccy_x_y (pos_1)
      pygame_x = x_convert_to_pygame (x)
      pygame_y = y_convert_to_pygame (y)
      draw_element (screen, line_brick, pygame_x, pygame_y, set_colour (0x07))
      x, y = gap_pos_to_speccy_x_y (pos_2)
      pygame_x = x_convert_to_pygame (x)
      pygame_y = y_convert_to_pygame (y)
      draw_element (screen, line_brick, pygame_x, pygame_y, set_colour (0x07))
      x, y = gap_pos_to_speccy_x_y (pos_3)
      pygame_x = x_convert_to_pygame (x)
      pygame_y = y_convert_to_pygame (y)
      draw_element (screen, line_brick, pygame_x, pygame_y, set_colour (0x07))
   for i in range (0, len (right_down_gap)):
      pos_1, pos_2, pos_3 = right_down_gap[i]
      # every gap is three speccy characters wide
      x, y = gap_pos_to_speccy_x_y (pos_1)
      pygame_x = x_convert_to_pygame (x)
      pygame_y = y_convert_to_pygame (y)
      draw_element (screen, line_brick, pygame_x, pygame_y, set_colour (0x07))
      x, y = gap_pos_to_speccy_x_y (pos_2)
      pygame_x = x_convert_to_pygame (x)
      pygame_y = y_convert_to_pygame (y)
      draw_element (screen, line_brick, pygame_x, pygame_y, set_colour (0x07))
      x, y = gap_pos_to_speccy_x_y (pos_3)
      pygame_x = x_convert_to_pygame (x)
      pygame_y = y_convert_to_pygame (y)
      draw_element (screen, line_brick, pygame_x, pygame_y, set_colour (0x07))

def add_hazard ():
   global hazard_list
   if len (hazard_list) < 20:
      # get hazard sprite (random)
      i = get_index ()
      # get hazard colour (random)
      c = get_colour ()
      p = get_position ()
      h = hazard_t (i - 1, c, p)
      # print ('hazard index ', i - 1)
      # print ('hazard colour ', c)
      # print ('hazard position ', p)
      hazard_list.append (h)

def draw_hazards (screen):
   global hazard_list
   # these are sprites
   global hazards
   for i in range (0, len (hazard_list)):
      h = hazard_list[i]
      sprite = hazards[h.index][h.sprite_idx]
      x, y = h.pos
      pygame_x = x_convert_to_pygame (x)
      pygame_y = y_convert_to_pygame (y)
      draw_element (screen, sprite, pygame_x, pygame_y, set_colour (h.colour))

def move_hazards ():
   global hazard_list
   # these are sprites
   global hazards
   for i in range (0, len (hazard_list)):
      h = hazard_list[i]
      n_sprites = len (hazards[h.index])
      h.sprite_idx = (h.sprite_idx + 1) % n_sprites
      x, y = h.pos
      x -= 8
      if x < 0:
         x = 247
         y -= 24
         if y < 8:
            x = 247
            y = 152
      h.pos = (x, y)

def draw_score (screen):
   global font
   c = set_colour (colour_t.magenta.value)
   tf = font.render ('HI00000 SC00075', True, c)
   screen.blit (tf, (x_convert_to_pygame (136), y_convert_to_pygame (176)))

def main ():
   global clock
   global font
   global x_res
   global y_res
   global scale
   # pygame setup
   pygame.init ()
   # pygame.mixer.init()
   screen = pygame.display.set_mode ((x_res * scale, y_res * scale))
   clock = pygame.time.Clock ()
   font = pygame.font.Font ('ZxSpectrum7-nROZ0.ttf', 10 * scale)
   while True:
      title_loop (screen)
      game_loop (screen)
   pygame.quit ()

if __name__ == '__main__':
   main ()
