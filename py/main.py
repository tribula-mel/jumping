#!/usr/bin/python3

import pygame

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

# chuck tile x offset to pygame
def tile_x_convert_to_pygame (offset):
   # 8 pixels per chuck x offset
   return DOTS_PER_PIXEL_X * 8 * scale * offset

# chuck tile y offset to pygame
def tile_y_convert_to_pygame (offset):
   # 8 pixels per chuck y offset
   # plus difference between top and bottom left
   # plus we need to make a room for the sprite
   return scale * y_res - (DOTS_PER_PIXEL_Y * 8 * scale * (offset + 1)) + 1

# chuck x offset to pygame
def x_convert_to_pygame (x):
   return DOTS_PER_PIXEL_X * scale * x

# chuck tile y offset to sdl
def y_convert_to_pygame (y):
   # plus difference between top and bottom left
   # plus we need to make a room for the sprite
   return (scale * y_res - (DOTS_PER_PIXEL_Y * scale * (y + 1)) + 1)

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

def draw_lives (screen):
   draw_element (screen, life, 0, 180, set_colour (0x03))

def draw_jack (screen):
   draw_element (screen, jack_0, 0, 0, set_colour (0x00))
   draw_element (screen, jack_1, 50, 0, set_colour (0x00))
   draw_element (screen, jack_2, 100, 0, set_colour (0x00))
   draw_element (screen, jack_3, 150, 0, set_colour (0x00))
   draw_element (screen, dyno_0, 0, 80, set_colour (0x00))
   draw_element (screen, dyno_1, 80, 80, set_colour (0x00))
   draw_element (screen, dyno_2, 160, 80, set_colour (0x03))
   draw_element (screen, hag_0, 20, 160, set_colour (0x00))
   draw_element (screen, hag_1, 100, 160, set_colour (0x00))
   draw_element (screen, ax_0, 0, 240, set_colour (0x00))
   draw_element (screen, ax_1, 80, 240, set_colour (0x00))
   draw_element (screen, ax_2, 160, 240, set_colour (0x03))
   draw_element (screen, ax_3, 240, 240, set_colour (0x03))
   draw_element (screen, snake_0, 0, 320, set_colour (0x00))
   draw_element (screen, snake_1, 80, 320, set_colour (0x00))
   draw_element (screen, snake_2, 160, 320, set_colour (0x03))
   draw_element (screen, snake_3, 240, 320, set_colour (0x03))
   draw_element (screen, plane_0, 0, 400, set_colour (0x00))
   draw_element (screen, plane_1, 80, 400, set_colour (0x00))
   draw_element (screen, plane_2, 160, 400, set_colour (0x03))
   draw_element (screen, plane_3, 240, 400, set_colour (0x03))
   draw_element (screen, spider_0, 320, 80, set_colour (0x00))
   draw_element (screen, spider_1, 400, 80, set_colour (0x00))
   draw_element (screen, spider_2, 480, 80, set_colour (0x03))
   draw_element (screen, spider_3, 560, 80, set_colour (0x03))
   draw_element (screen, train_0, 0, 480, set_colour (0x00))
   draw_element (screen, train_1, 80, 480, set_colour (0x00))
   draw_element (screen, train_2, 160, 480, set_colour (0x03))
   draw_element (screen, train_3, 240, 480, set_colour (0x03))
   draw_element (screen, ghost_0, 320, 0, set_colour (0x00))
   draw_element (screen, ghost_1, 400, 0, set_colour (0x00))
   draw_element (screen, ghost_2, 480, 0, set_colour (0x03))
   draw_element (screen, ghost_3, 560, 0, set_colour (0x03))
   draw_element (screen, gunner_0, 320, 240, set_colour (0x00))
   draw_element (screen, gunner_1, 400, 240, set_colour (0x00))
   draw_element (screen, gunner_2, 480, 240, set_colour (0x03))
   draw_element (screen, gunner_3, 560, 240, set_colour (0x03))
   draw_element (screen, bus_0, 320, 160, set_colour (0x03))
   draw_element (screen, bus_1, 400, 160, set_colour (0x03))
   draw_element (screen, bus_2, 480, 160, set_colour (0x03))
   draw_element (screen, bus_3, 560, 160, set_colour (0x03))

def title_loop (screen):
   screen.fill ((255, 255, 255))
   while do_events ([pygame.QUIT, pygame.KEYDOWN],
                    [pygame.K_ESCAPE, pygame.K_s]):
      draw_jack (screen)
      draw_lives (screen)
      pygame.display.flip ()
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
