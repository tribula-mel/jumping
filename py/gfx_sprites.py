from game_types import sprite_t

life = sprite_t (0x01, 0x08, 0x82,
      [
         0x18,
         0x3c,
         0x3c,
         0x18,
         0x7e,
         0x18,
         0x24,
         0x42
      ])

dyno = sprite_t (0x03, 0x10, 0x00,
      [
         0x00, 0x00, 0x00,
         0x00, 0x00, 0x00,
         0x00, 0x00, 0x00,
         0x03, 0x00, 0x00,
         0x05, 0x80, 0x00,
         0x07, 0xc0, 0x00,
         0x06, 0xc0, 0x00,
         0x00, 0xe0, 0x00,

         0x00, 0xf0, 0x00,
         0x01, 0xf8, 0x00,
         0x07, 0xf8, 0x30,
         0x08, 0x7c, 0x40,
         0x00, 0x7c, 0x40,
         0x00, 0xfe, 0x80,
         0x03, 0xcf, 0x80,
         0x07, 0x8f, 0x00,
      ])

jack_0 = sprite_t (0x02, 0x10, 0x00,
      [
         0x01, 0xc0,
         0x03, 0xe0,
         0x04, 0x90,
         0x07, 0x70,
         0x05, 0xd0,
         0x04, 0x10,
         0x03, 0xe0,
         0x01, 0xc0,
         0x03, 0xe0,
         0x04, 0x90,
         0x09, 0x48,
         0x11, 0x44,
         0x02, 0x20,
         0x02, 0x20,
         0x04, 0x10,
         0x0c, 0x18,
      ])

jack_1 = sprite_t (0x02, 0x10, 0x00,
      [
         0x01, 0xc0,
         0x03, 0xe0,
         0x04, 0xf0,
         0x0f, 0xf0,
         0x1f, 0x30,
         0x04, 0x70,
         0x03, 0xe0,
         0x01, 0xc0,
         0x03, 0xe0,
         0x04, 0x90,
         0x09, 0x50,
         0x11, 0x48,
         0x02, 0x20,
         0x02, 0x20,
         0x04, 0x10,
         0x0c, 0x30,
      ])

jack_2 = sprite_t (0x02, 0x10, 0x00,
      [
         0x01, 0xc0,
         0x03, 0xe0,
         0x04, 0x90,
         0x07, 0x70,
         0x05, 0xd0,
         0x04, 0x10,
         0x03, 0xe0,
         0x01, 0xc0,

         0x03, 0xe0,
         0x04, 0x90,
         0x09, 0x48,
         0x11, 0x44,
         0x02, 0x20,
         0x02, 0x20,
         0x04, 0x10,
         0x0c, 0x18,
      ])

jack_3 = sprite_t (0x02, 0x10, 0x00,
      [
         0x01, 0xc0,
         0x03, 0xe0,
         0x07, 0x90,
         0x07, 0xf8,
         0x06, 0x7c,
         0x07, 0x10,
         0x03, 0xe0,
         0x01, 0xc0,

         0x03, 0xe0,
         0x04, 0x90,
         0x05, 0x48,
         0x09, 0x44,
         0x02, 0x20,
         0x02, 0x20,
         0x04, 0x10,
         0x06, 0x18,
      ])
