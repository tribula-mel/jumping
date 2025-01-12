#!/usr/bin/python3

import pygame
import random

from game_types import sprite_t
from game_types import colour_t
from gfx_sprites import *

scale = 3

DOTS_PER_PIXEL_X = 1
DOTS_PER_PIXEL_Y = 1

# original game on cpc464 ran in mode 0
x_res = DOTS_PER_PIXEL_X * 256
y_res = DOTS_PER_PIXEL_Y * 192

clock = None

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

# jumping jack tile x offset to pygame
def tile_x_convert_to_pygame (offset):
   # 8 pixels per jumping jack x offset
   return DOTS_PER_PIXEL_X * 8 * scale * offset

# jumping jack tile y offset to pygame
def tile_y_convert_to_pygame (offset):
   # 8 pixels per jumping jack y offset
   # plus difference between top and bottom left
   # plus we need to make a room for the sprite
   return scale * y_res - (DOTS_PER_PIXEL_Y * 8 * scale * (offset + 1)) + 1

# jumping jack x offset to pygame
def x_convert_to_pygame (x):
   return DOTS_PER_PIXEL_X * scale * x

# jumping jack tile y offset to sdl
def y_convert_to_pygame (y):
   # plus difference between top and bottom left
   # plus we need to make a room for the sprite
   #return (scale * y_res - (DOTS_PER_PIXEL_Y * scale * (y + 1)) + 1)
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
   index = 0
   x_backup = x
   mask = 0x80
   for i in range (0, element.height):
      for j in range (0, element.width):
         for k in range (0, 8):
            if element.sprite[index] & mask:
               w = DOTS_PER_PIXEL_X * scale
               h = DOTS_PER_PIXEL_Y * scale
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

   x = x_convert_to_pygame (96)
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
   # draw_element (screen, jack_lf, 50, 0, set_colour (0x00))
   # draw_element (screen, jack_rf, 100, 0, set_colour (0x00))
   # draw_element (screen, dyno_0, 0, 80, set_colour (0x00))
   # draw_element (screen, dyno_1, 80, 80, set_colour (0x00))
   # draw_element (screen, dyno_2, 160, 80, set_colour (0x03))
   # draw_element (screen, hag_0, 20, 160, set_colour (0x00))
   # draw_element (screen, hag_1, 100, 160, set_colour (0x00))
   # draw_element (screen, ax_0, 0, 240, set_colour (0x00))
   # draw_element (screen, ax_1, 80, 240, set_colour (0x00))
   # draw_element (screen, ax_2, 160, 240, set_colour (0x03))
   # draw_element (screen, ax_3, 240, 240, set_colour (0x03))
   # draw_element (screen, snake_0, 0, 320, set_colour (0x00))
   # draw_element (screen, snake_1, 80, 320, set_colour (0x00))
   # draw_element (screen, snake_2, 160, 320, set_colour (0x03))
   # draw_element (screen, snake_3, 240, 320, set_colour (0x03))
   # draw_element (screen, plane_0, 0, 400, set_colour (0x00))
   # draw_element (screen, plane_1, 80, 400, set_colour (0x00))
   # draw_element (screen, plane_2, 160, 400, set_colour (0x03))
   # draw_element (screen, plane_3, 240, 400, set_colour (0x03))
   # draw_element (screen, spider_0, 320, 80, set_colour (0x00))
   # draw_element (screen, spider_1, 400, 80, set_colour (0x00))
   # draw_element (screen, spider_2, 480, 80, set_colour (0x03))
   # draw_element (screen, spider_3, 560, 80, set_colour (0x03))
   # draw_element (screen, train_0, 0, 480, set_colour (0x00))
   # draw_element (screen, train_1, 80, 480, set_colour (0x00))
   # draw_element (screen, train_2, 160, 480, set_colour (0x03))
   # draw_element (screen, train_3, 240, 480, set_colour (0x03))
   # draw_element (screen, ghost_0, 320, 0, set_colour (0x00))
   # draw_element (screen, ghost_1, 400, 0, set_colour (0x00))
   # draw_element (screen, ghost_2, 480, 0, set_colour (0x03))
   # draw_element (screen, ghost_3, 560, 0, set_colour (0x03))
   # draw_element (screen, gunner_0, 320, 240, set_colour (0x00))
   # draw_element (screen, gunner_1, 400, 240, set_colour (0x00))
   # draw_element (screen, gunner_2, 480, 240, set_colour (0x03))
   # draw_element (screen, gunner_3, 560, 240, set_colour (0x03))
   # draw_element (screen, bus_0, 320, 160, set_colour (0x03))
   # draw_element (screen, bus_1, 400, 160, set_colour (0x03))
   # draw_element (screen, bus_2, 480, 160, set_colour (0x03))
   # draw_element (screen, bus_3, 560, 160, set_colour (0x03))
   # draw_element (screen, jack_lrls, 320, 320, set_colour (0x00))
   # draw_element (screen, jack_lrlp, 400, 320, set_colour (0x00))
   # draw_element (screen, jack_lrlc, 480, 320, set_colour (0x00))
   # draw_element (screen, jack_lrlws, 560, 320, set_colour (0x00))
   # draw_element (screen, jack_rrls, 320, 400, set_colour (0x00))
   # draw_element (screen, jack_rrlp, 400, 400, set_colour (0x00))
   # draw_element (screen, jack_rrlc, 480, 400, set_colour (0x00))
   # draw_element (screen, jack_rrlws, 560, 400, set_colour (0x00))
   # draw_element (screen, jack_f0, 320, 480, set_colour (0x00))
   # draw_element (screen, jack_f1, 400, 480, set_colour (0x00))
   # draw_element (screen, jack_f2, 480, 480, set_colour (0x00))
   # draw_element (screen, jack_f3, 560, 480, set_colour (0x00))
   # draw_element (screen, jack_f4, 640, 480, set_colour (0x00))
   # draw_element (screen, line_brick, 640, 560, set_colour (0x02))

def title_loop (screen):
   init_gaps ()
   while do_events ([pygame.QUIT, pygame.KEYDOWN],
                    [pygame.K_ESCAPE, pygame.K_s]):
      screen.fill ((255, 255, 255))
      draw_line (screen)
      draw_lives (screen)
      draw_gaps (screen)
      draw_jack (screen)
      pygame.display.flip ()
      move_gaps ()
      clock.tick (30) # limits FPS

def do_events (events, keys):
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

def main ():
   global clock
   global font
   # pygame setup
   pygame.init ()
   # pygame.mixer.init()
   screen = pygame.display.set_mode ((x_res * scale, y_res * scale))
   clock = pygame.time.Clock ()
   while True:
      title_loop (screen)
      game_loop (screen)
   pygame.quit ()

if __name__ == '__main__':
   main ()
