#!/usr/bin/python3

import pygame
import random

from game_types import colour_t
from game_types import hazard_t
from game_types import jack_t
from game_types import sounds_t
from gfx_sprites import *
from ballad import ballad_list

scale = 1

DOTS_PER_PIXEL_X = 1
DOTS_PER_PIXEL_Y = 1

# speccy's original screen is 256*192 (32x24 chars)
x_res = DOTS_PER_PIXEL_X * 256
y_res = DOTS_PER_PIXEL_Y * 192

clock = None
pause = False
font  = None
grid  = False
frame = 0
hhse  = 0
snds  = None

# do not cross the line :) , but embed gaps within
# there are eight lines with maximum of eight gaps
# two for starters; the eight lines are internally
#    presented as one line; since we are moving
#    a character this means 32*8 = 256 positions
#    within the line, which is 32*8*8 spectrum dots
#    long (2048)
# each gap is three speccy chars long
# holders for the gaps; each gap is presented with a single
#    integer (random starting value) within [0..2047] range
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

jjack = None
high_score = 0

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

def convert_to_pygame (lt):
   global scale
   x1, y1, x2, y2 = lt
   rx1 = DOTS_PER_PIXEL_X * scale * x1
   rx2 = DOTS_PER_PIXEL_X * scale * x2
   ry1 = DOTS_PER_PIXEL_Y * scale * y1
   ry2 = DOTS_PER_PIXEL_Y * scale * y2
   return [rx1, ry1, rx2, ry2]

def set_colour (colour):
   if colour == colour_t.yellow.value:
      return (0xd7, 0xd7, 0x00)
   elif colour == colour_t.magenta.value:
      return (0xd7, 0x00, 0xd7)
   elif colour == colour_t.cyan.value:
      return (0x00, 0xd7, 0xd7)
   elif colour == colour_t.green.value:
      return (0x00, 0xd7, 0x00)
   elif colour == colour_t.white.value:
      return (0xd7, 0xd7, 0xd7)
   elif colour == colour_t.red.value:
      return (0xd7, 0x00, 0x00)
   elif colour == colour_t.blue.value:
      return (0x00, 0x00, 0xd7)
   else:
      # black
      return (0x00, 0x00, 0x00)

def draw_element (screen, element, x, y, colour, dnuy = False):
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
               if dnuy == True and x > (x_res * scale - 1):
                  pygame.draw.rect(screen, colour,
                     [x%(x_res*scale), y, w, h])
               elif dnuy == False and x > (x_res * scale - 1):
                  pygame.draw.rect(screen, colour,
                     [x%(x_res*scale),
                      (y+y_convert_to_pygame (24))%(y_res*scale), w, h])
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
   global jjack
   y = y_convert_to_pygame (176)
   for i in range (0, jjack.lives):
      x = x_convert_to_pygame (8* i)
      draw_element (screen, life, x, y, set_colour (0x03))

def draw_jack_standing (screen):
   global frame
   global jjack
   global snds
   s_x, s_y = jjack.pos
   x = x_convert_to_pygame (s_x)
   y = y_convert_to_pygame (s_y)
   if (frame & 0x7f) < 32:
      draw_element (screen, jack_ff, x, y, set_colour (0x00))
      if (frame & 0x7f) == 0:
         snds.ff_head.play ()
   elif (frame & 0x7f) < 64:
      draw_element (screen, jack_lf, x, y, set_colour (0x00))
      if (frame & 0x7f) == 32:
         snds.lr_head.play ()
   elif (frame & 0x7f) < 96:
      draw_element (screen, jack_ff, x, y, set_colour (0x00))
      if (frame & 0x7f) == 64:
         snds.ff_head.play ()
   elif (frame & 0x7f) <= 127:
      draw_element (screen, jack_rf, x, y, set_colour (0x00))
      if (frame & 0x7f) == 96:
         snds.lr_head.play ()

def draw_jack_left (screen):
   global jjack
   global snds
   dnuy = False
   s_x, s_y = jjack.pos
   if (s_x - 8) < 0:
      jjack.state = 9
      dnuy = True
   if jjack.state == 9:
      if jjack.sprite_idx == 2:
         s_x = (s_x - 8) & 0xff
         jjack.pos = (s_x, s_y)
   s_x = (s_x - 8) & 0xff
   x = x_convert_to_pygame (s_x)
   y = y_convert_to_pygame (s_y)
   sprite = jack_se[jjack.state][jjack.sprite_idx]
   draw_element (screen, sprite, x, y, set_colour (0x00), dnuy)
   if jjack.sprite_idx == 0:
      snds.run.play ()
   jjack.sprite_idx += 1
   if jjack.sprite_idx >= len (jack_se[jjack.state]):
      jjack.state = 0
      jjack.sprite_idx = 0
      jjack.pos = (s_x, s_y)

def draw_jack_right (screen):
   global jjack
   global snds
   dnuy = False
   s_x, s_y = jjack.pos
   if (s_x + 16) > 255:
      jjack.state = 10
      dnuy = True
   if jjack.state == 10:
      if jjack.sprite_idx == 2:
         s_x += 8
         jjack.pos = (s_x, s_y)
   x = x_convert_to_pygame (s_x)
   y = y_convert_to_pygame (s_y)
   sprite = jack_se[jjack.state][jjack.sprite_idx]
   draw_element (screen, sprite, x, y, set_colour (0x00), dnuy)
   if jjack.sprite_idx == 0:
      snds.run.play ()
   jjack.sprite_idx += 1
   if jjack.sprite_idx >= len (jack_se[jjack.state]):
      jjack.state = 0
      jjack.sprite_idx = 0
      if (s_x + 8) > 231:
         s_x = 0
      else:
         s_x += 8
      jjack.pos = (s_x, s_y)

def draw_jack_crash (screen):
   global jjack
   global snds
   s_x, s_y = jjack.pos
   x = x_convert_to_pygame (s_x)
   y = y_convert_to_pygame (s_y - 8)
   sprite = jack_se[jjack.state][jjack.sprite_idx]
   draw_element (screen, sprite, x, y, set_colour (0x00))
   if jjack.sprite_idx == 0:
      snds.line_crash.play ()
   jjack.sprite_idx += 1
   if jjack.sprite_idx >= len (jack_se[jjack.state]):
      jjack.state = 4
      jjack.sprite_idx = 0
      if s_y == 176:
         jjack.lives -= 1

def draw_jack_stars (screen):
   global jjack
   global snds
   s_x, s_y = jjack.pos
   x = x_convert_to_pygame (s_x)
   y = y_convert_to_pygame (s_y)
   sprite = jack_se[jjack.state][jjack.sprite_idx]
   draw_element (screen, sprite, x, y, set_colour (0x00))
   if jjack.sprite_idx == 0:
      snds.stars.play ()
   jjack.sprite_idx += 1
   if jjack.sprite_idx >= len (jack_se[jjack.state]):
      jjack.state = 0
      jjack.sprite_idx = 0

def draw_jack_jump (screen):
   global jjack
   global snds
   s_x, s_y = jjack.pos
   x = x_convert_to_pygame (s_x)
   y = y_convert_to_pygame (s_y - 8)
   sprite = jack_se[jjack.state][jjack.sprite_idx]
   draw_element (screen, sprite, x, y, set_colour (0x00))
   if jjack.sprite_idx == 0:
      snds.jump_thro.play ()
   jjack.sprite_idx += 1
   if jjack.sprite_idx >= len (jack_se[jjack.state]):
      jjack.state = 7
      jjack.sprite_idx = 0
      jjack.score += 5 * (jjack.level + 1)
      if s_y == 8:
         jjack.next = True

def draw_jack_through (screen):
   global jjack
   s_x, s_y = jjack.pos
   x = x_convert_to_pygame (s_x)
   y = y_convert_to_pygame (s_y - 24)
   sprite = jack_se[jjack.state][jjack.sprite_idx]
   draw_element (screen, sprite, x, y, set_colour (0x00))
   jjack.sprite_idx += 1
   if jjack.sprite_idx >= len (jack_se[jjack.state]):
      jjack.state = 0
      jjack.sprite_idx = 0
      jjack.pos = (s_x, s_y - 24)
      add_gap ()

def draw_jack_ledge (screen):
   global jjack
   global snds
   s_x, s_y = jjack.pos
   x = x_convert_to_pygame (s_x)
   y = y_convert_to_pygame (s_y)
   sprite = jack_se[jjack.state][jjack.sprite_idx]
   draw_element (screen, sprite, x, y, set_colour (0x00))
   if jjack.sprite_idx == 0:
      snds.fall_thro.play ()
   jjack.sprite_idx += 1
   if jjack.sprite_idx >= len (jack_se[jjack.state]):
      jjack.state = 8
      jjack.sprite_idx = 0

def draw_jack_fall (screen):
   global jjack
   s_x, s_y = jjack.pos
   x = x_convert_to_pygame (s_x)
   y = y_convert_to_pygame (s_y + 8)
   sprite = jack_se[jjack.state][jjack.sprite_idx]
   draw_element (screen, sprite, x, y, set_colour (0x00))
   jjack.sprite_idx += 1
   if jjack.sprite_idx >= len (jack_se[jjack.state]):
      jjack.state = 4
      jjack.sprite_idx = 0
      jjack.pos = (s_x, s_y + 24)
      if s_y + 24 == 176:
         jjack.lives -= 1

def draw_jack (screen):
   global jjack
   if jjack.state == 0:
      draw_jack_standing (screen)
   elif jjack.state == 1 or jjack.state == 9:
      draw_jack_left (screen)
   elif jjack.state == 2 or jjack.state == 10:
      draw_jack_right (screen)
   elif jjack.state == 3:
      draw_jack_jump (screen)
   elif jjack.state == 4:
      draw_jack_stars (screen)
   elif jjack.state == 5:
      draw_jack_crash (screen)
   elif jjack.state == 6:
      draw_jack_ledge (screen)
   elif jjack.state == 7:
      draw_jack_through (screen)
   elif jjack.state == 8:
      draw_jack_fall (screen)

def up_left_up_gap ():
   global jjack
   global left_up_gap
   jx, jy = jjack.pos
   for i in range (0, len (left_up_gap)):
      l1, l2, l3 = left_up_gap[i]
      jl = 256 * int (jy / 24) + jx
      if l1 - 3 <= jl and jl < l3 - 3:
         return True
   return False

def up_right_down_gap ():
   global jjack
   global right_down_gap
   jx, jy = jjack.pos
   for i in range (0, len (right_down_gap)):
      l1, l2, l3 = right_down_gap[i]
      jl = 256 * int (jy / 24) + jx
      if l1 - 3 <= jl and jl < l3 - 3:
         return True
   return False

def attempt_up_jack ():
   ls = up_left_up_gap ()
   rs = up_right_down_gap ()
   if ls == False and rs == False:
         # jump crash
         jjack.state = 5
   else:
         # jump state
         jjack.state = 3

def down_left_up_gap ():
   global jjack
   global left_up_gap
   jx, jy = jjack.pos
   for i in range (0, len (left_up_gap)):
      l1, l2, l3 = left_up_gap[i]
      jl = 256 * (int (jy / 24) + 1) + jx
      if l1 <= jl and jl <= l3:
         return True
   return False

def down_right_down_gap ():
   global jjack
   global right_down_gap
   jx, jy = jjack.pos
   for i in range (0, len (right_down_gap)):
      l1, l2, l3 = right_down_gap[i]
      jl = 256 * (int (jy / 24) + 1) + jx
      if l1 <= jl and jl <= l3:
         return True
   return False

def attempt_down_jack ():
   ls = down_left_up_gap ()
   rs = down_right_down_gap ()
   # we can reach the fall state from standing or from
   #    stars state
   if jjack.state == 0 or jjack.state == 1 or jjack.state == 2 or jjack.state == 4:
      if ls == True or rs == True:
         # fall state
         jjack.state = 6

def draw_grid (screen):
   global grid
   if grid == False:
      return
   green = (0x00, 0xd7, 0x00)
   black = (0x00, 0x00, 0x00)
   # draw vertical lines first
   sx_s = 7
   sy_s = 0
   sy_e = 191
   for i in range (0, 32):
      x = x_convert_to_pygame (sx_s)
      y = x_convert_to_pygame (sy_e)
      if i % 3 == 0:
         pygame.draw.line (screen, green, (x, sy_s), (x, y))
      else:
         pygame.draw.line (screen, black, (x, sy_s), (x, y))
      sx_s += 8
   # draw horizontal lines
   sy_s = 7
   sx_s = 0
   sx_e = 255
   for i in range (0, 24):
      y = x_convert_to_pygame (sy_s)
      x = x_convert_to_pygame (sx_e)
      if i % 3 == 0:
         pygame.draw.line (screen, green, (sx_s, y), (x, y))
      else:
         pygame.draw.line (screen, black, (sx_s, y), (x, y))
      sy_s += 8

def collision_check ():
   global hazard_list
   global jjack
   hl = len (hazard_list)
   if hl == 0:
      return
   jx, jy = jjack.pos
   for i in range (0, hl):
      if hazard_list[i].delay != 0:
         continue
      hx, hy = hazard_list[i].pos
      if jy == hy:
         if jx <= hx and (jx + 16) > hx:
            # stars state
            snds.squash.play ()
            jjack.state = 4
            return

def the_end_loop (screen):
   global clock
   global jjack
   global high_score
   global frame
   cy = set_colour (colour_t.yellow.value)
   cg = set_colour (colour_t.green.value)
   cw = set_colour (colour_t.white.value)
   cb = set_colour (colour_t.black.value)
   cp = set_colour (colour_t.blue.value)
   cc = set_colour (colour_t.cyan.value)
   cl = set_colour (colour_t.magenta.value)
   jj = font.render ('JUMPING JACK', True, cb)
   ts = 'FINAL SCORE  ' + prep_string (jjack.score)
   ts2 = ' WITH '
   if jjack.level < 10:
      ts2 += ' '
   ts2 += str (jjack.level) + '  HAZARD'
   if jjack.level != 1:
      ts2 += 'S'
   if jjack.score > high_score:
      high_score = jjack.score
      hs = True
   else:
      hs = False
   te = 'Press ENTER to replay'
   rs = font.render (ts, True, cb)
   rs2 = font.render (ts2, True, cb)
   re = font.render (te, True, cp)
   rhsl = font.render ('NEW HIGH', True, cl)
   rhsw = font.render ('NEW HIGH', True, cw)
   while True:
      running = do_events ([pygame.K_ESCAPE, pygame.K_RETURN])
      if (running == False):
         break
      screen.fill (cy)
      pygame.draw.rect(screen, cg, convert_to_pygame ([64, 16, 128, 24]))
      screen.blit (jj, (x_convert_to_pygame (80), y_convert_to_pygame (24)))
      pygame.draw.rect(screen, cc, convert_to_pygame ([40, 72, 176, 40]))
      screen.blit (rs, (x_convert_to_pygame (56), y_convert_to_pygame (80)))
      screen.blit (rs2, (x_convert_to_pygame (56), y_convert_to_pygame (96)))
      if hs == True:
         if (frame & 0x8) == 0:
            pygame.draw.rect(screen, cl, convert_to_pygame ([80, 128, 96, 24]))
            screen.blit (rhsw, (x_convert_to_pygame (96), y_convert_to_pygame (136)))
         else:
            pygame.draw.rect(screen, cw, convert_to_pygame ([80, 128, 96, 24]))
            screen.blit (rhsl, (x_convert_to_pygame (96), y_convert_to_pygame (136)))
      screen.blit (re, (x_convert_to_pygame (40), y_convert_to_pygame (176)))
      pygame.display.flip ()
      frame += 1
      clock.tick (35) # limits FPS

def finish_game (screen):
   global jjack
   if jjack.lives == 0:
      snds.game_end.play ()
      clear_gaps ()
      clear_hazards ()
      return True
   return False

def next_level (screen):
   global jjack
   if jjack.next == True:
      snds.new_level.play ()
      jjack.next = False
      jjack.level += 1
      jjack.state = 0
      jjack.pos = (80, 176)
      ballad_loop (screen)
      clear_gaps ()
      init_gaps ()
      create_hazards (jjack.level)

def ticker ():
   global hazard_list
   global frame
   for i in range (0, len (hazard_list)):
      h = hazard_list[i]
      if h.delay != 0:
         h.delay -= 1
   frame += 1

def game_loop (screen):
   global pause
   global jjack
   global frame
   init_gaps ()
   jjack = jack_t (0, (80, 176))
   while do_events ([pygame.K_ESCAPE,
                     pygame.K_p, pygame.K_a,
                     pygame.K_d, pygame.K_w,
                     pygame.K_i]):
      screen.fill ((0xd7, 0xd7, 0xd7))
      draw_line (screen)
      draw_lives (screen)
      move_gaps ()
      if frame & 0x1 == 0:
         move_hazards ()
      draw_gaps (screen)
      draw_hazards (screen)
      draw_score (screen)
      attempt_down_jack ()
      draw_jack (screen)
      collision_check ()
      if True == finish_game (screen):
         return
      draw_grid (screen)
      pygame.display.flip ()
      ticker ()
      clock.tick (35) # limits FPS
      next_level (screen)

def do_events (keys):
   global pause
   global jjack
   global grid
   for event in pygame.event.get ():
      if event.type == pygame.QUIT:
         exit ()
      elif event.type == pygame.KEYDOWN:
         if event.key in keys:
            if event.key == pygame.K_ESCAPE:
               exit ()
            if event.key == pygame.K_p:
               if pause == False:
                  pause = True
               else:
                  pause = False
               while pause:
                  running = do_events ([pygame.K_p])
                  if running == False:
                     return
            if event.key == pygame.K_a:
               if jjack.state == 0:
                  # left state
                  jjack.state = 1
            if event.key == pygame.K_d:
               if jjack.state == 0:
                  # right state
                  jjack.state = 2
            if event.key == pygame.K_w:
               if jjack.state == 0:
                  attempt_up_jack ()
            if event.key == pygame.K_i:
               if grid == True:
                  grid = False
               else:
                  grid = True
            if event.key == pygame.K_RETURN:
               return False
   return True

def ballad_loop (screen):
   global clock
   global jjack
   global ballad_list
   global frame
   rd = False
   rd2 = False
   el = False
   cy = set_colour (colour_t.yellow.value)
   cg = set_colour (colour_t.green.value)
   cw = set_colour (colour_t.white.value)
   cb = set_colour (colour_t.black.value)
   cp = set_colour (colour_t.blue.value)
   if jjack.level == 6 or jjack.level == 11 or jjack.level == 16:
      el = True
      cl = set_colour (colour_t.magenta.value)
      nlw = font.render ('EXTRA LIFE', True, cw)
      nll = font.render ('EXTRA LIFE', True, cl)
   jj = font.render ('JUMPING JACK', True, cb)
   tl = 'NEXT LEVEL - '
   if jjack.level < 10:
      tl += ' '
   tl += str (jjack.level) + '  HAZARD'
   if jjack.level > 1:
      tl += 'S'
   nl = font.render (tl, True, cp)
   st1 = ballad_list [jjack.level - 1][0]
   if len (ballad_list[jjack.level - 1]) == 2:
      st2 = ballad_list [jjack.level - 1][1]
   else:
      st2 = None
   pst1 = ''
   pst2 = ''
   i = 0
   j = 0
   sf = frame
   while True:
      running = do_events ([pygame.K_ESCAPE])
      if (running == False):
         break
      screen.fill (cy)
      pygame.draw.rect(screen, cg, convert_to_pygame ([64, 16, 128, 24]))
      screen.blit (jj, (x_convert_to_pygame (80), y_convert_to_pygame (24)))
      pygame.draw.rect(screen, cw, convert_to_pygame ([16, 64, 224, 24]))
      screen.blit (nl, (x_convert_to_pygame (32), y_convert_to_pygame (72)))
      if i < len (st1):
         pst1 += st1[i]
         r1 = font.render (pst1, True, cp)
         i += 1
      elif rd == False:
         rd = True
      if st2 != None and rd == True:
         if j < len (st2):
            pst2 += st2[j]
            r2 = font.render (pst2, True, cp)
            j += 1
         elif rd2 == False:
            rd2 = True
         screen.blit (r2, (x_convert_to_pygame (0), y_convert_to_pygame (144)))
      screen.blit (r1, (x_convert_to_pygame (0), y_convert_to_pygame (128)))
      if el == True and rd2 == True:
         if (frame & 0x8) == 0:
            pygame.draw.rect(screen, cl, convert_to_pygame ([72, 168, 112, 24]))
            screen.blit (nlw, (x_convert_to_pygame (88), y_convert_to_pygame (176)))
         else:
            pygame.draw.rect(screen, cw, convert_to_pygame ([72, 168, 112, 24]))
            screen.blit (nll, (x_convert_to_pygame (88), y_convert_to_pygame (176)))
      pygame.display.flip ()
      clock.tick (35) # limits FPS
      frame += 1
      # 9 seconds loop
      if (frame - sf) >= (9 * 35):
         break

def init_gaps ():
   global left_up_gap
   global right_down_gap
   # mask is common for both movements; we want the initial position
   #    to be aligned on the character level
   mask = -1
   mask ^= 0x7
   # both gaps are starting from the same position
   # the gaps will be moving from [0..2023], in eight dots steps,
   #    last three positions being needed for the full gap length
   # line is 2048 [0..2047] dots long (32 chars * 8 dots/char * 8 lines)
   # both gaps have origin in the left corner
   init = random.randint (0, 2023)
   init &= mask
   left_up_gap.append ([init, init+8, init+16])
   right_down_gap.append ([init, init+8, init+16])

def clear_gaps ():
   global left_up_gap
   global right_down_gap
   left_up_gap.clear ()
   right_down_gap.clear ()

def clear_hazards ():
   global hazard_list
   hazard_list.clear ()

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
   global frame
   #if frame & 0x3 != 0:
   #   return
   for i in range (0, len (left_up_gap)):
      x, y, z = left_up_gap[i]
      x = (x - 2) & 0x7ff
      y = (y - 2) & 0x7ff
      z = (z - 2) & 0x7ff
      left_up_gap[i] = [x, y, z]
   for i in range (0, len (right_down_gap)):
      x, y, z = right_down_gap[i]
      x = (x + 2) % 2048
      y = (y + 2) % 2048
      z = (z + 2) % 2048
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
      #l1, l2, l3 = right_down_gap[i]
      #xl2 = l2 % 256
      #xl3 = l3 % 256
      #print ('gap x2/x3', xl2, xl3)

def create_hazards (num):
   global hazard_list
   hazard_list.clear ()
   if num < 20:
      for i in range (0, num):
         # get hazard sprite (random)
         i = get_index ()
         # get hazard colour (random)
         c = get_colour ()
         p = get_position ()
         h = hazard_t (i - 1, c, p)
         hazard_list.append (h)

def draw_hazards (screen):
   global hazard_list
   # these are sprites
   global hazards
   for i in range (0, len (hazard_list)):
      h = hazard_list[i]
      if h.delay != 0:
         continue
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
      if h.delay != 0:
         continue
      h.sprite_idx = (h.sprite_idx + 1) % n_sprites
      if h.sprite_idx == 2 or h.sprite_idx == 0:
         x, y = h.pos
         x -= 8
         if x < 0:
            x &= 0xff
            y -= 24
            if y < 8:
               x = 232
               y = 152
               # re-entrance on the bottom right corner is going to be
               #    delayed for 16 frames
               h.delay = 128
         h.pos = (x, y)

def prep_string (num):
   st = ''
   dividend = 10000
   for i in range (0, 4):
      st += str (int (num / dividend))
      num = num % dividend
      dividend = int (dividend / 10)
   st += str (num)
   return st

def draw_score (screen):
   global font
   global jjack
   global high_score
   st = 'HI'
   c = set_colour (colour_t.magenta.value)
   st += prep_string (high_score)
   st += ' SC'
   st += prep_string (jjack.score)
   tf = font.render (st, True, c)
   screen.blit (tf, (x_convert_to_pygame (136), y_convert_to_pygame (176)))

def init_sounds ():
   global snds
   snds = sounds_t ()
   snds.fall_thro = pygame.mixer.Sound ('fall_thro.ogg')
   snds.ff_head = pygame.mixer.Sound ('ff_head.ogg')
   snds.game_end = pygame.mixer.Sound ('game_end.ogg')
   snds.jump_thro = pygame.mixer.Sound ('jump_thro.ogg')
   snds.line_crash = pygame.mixer.Sound ('line_crash.ogg')
   snds.lr_head = pygame.mixer.Sound ('lr_head.ogg')
   snds.new_level = pygame.mixer.Sound ('new_level.ogg')
   snds.run = pygame.mixer.Sound ('run.ogg')
   snds.squash = pygame.mixer.Sound ('squash.ogg')
   snds.stars = pygame.mixer.Sound ('stars.ogg')

def main ():
   global clock
   global font
   global x_res
   global y_res
   global scale
   # pygame setup
   pygame.init ()
   # get display information
   info = pygame.display.Info()
   width = info.current_w
   height = info.current_h
   scale = int (height / 192)
   if int (width / scale) >= 256:
      scale -= 2
   else:
      scale = 1
   print (scale)
   pygame.mixer.init()
   pygame.key.set_repeat(100, 100)
   screen = pygame.display.set_mode ((x_res * scale, y_res * scale))
   pygame.display.set_caption("Jumping Jack")
   clock = pygame.time.Clock ()
   font = pygame.font.Font ('ZxSpectrum7-nROZ0.ttf', 10 * scale)
   init_sounds ()
   init_hazards ()
   while True:
      game_loop (screen)
      the_end_loop (screen)
   pygame.quit ()

if __name__ == '__main__':
   main ()
