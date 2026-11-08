"""Optional asset generator; the PNG files are already included in the project.
Run `python assets/make_pixel_art.py` only if you want to recreate them.
Pillow is needed for regeneration, NOT for running the game.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import random

ROOT = Path(__file__).resolve().parent / 'pixel'
ROOT.mkdir(parents=True, exist_ok=True)
SIZE = 32

def save(im, name):
    im.save(ROOT / f'{name}.png')

def rect(d, box, color):
    d.rectangle(box, fill=color)

# Ve tuong gach
rng = random.Random(12)
im = Image.new('RGBA', (SIZE, SIZE), (9, 7, 7, 255)); d = ImageDraw.Draw(im)
for row in range(4):
    top = row * 8 + 1
    shift = -8 if row % 2 else 0
    for left in range(shift, 33, 16):
        l, r = max(0, left + 1), min(31, left + 14)
        if r < l: continue
        rect(d, (l, top, r, top + 5), (139 + rng.randrange(15), 54 + rng.randrange(16), 25, 255))
        rect(d, (l, top, r, top), (223, 109, 42, 255))
        rect(d, (l, top + 5, r, top + 5), (84, 30, 18, 255))
        for _ in range(2):
            xx = rng.randint(l, r)
            yy = rng.randint(top+1, top+4)
            rect(d, (xx, yy, min(r,xx+2), yy), rng.choice([(204,83,34,255),(101,34,19,255)]))
save(im, 'brick')

# Ve tuong thep
im = Image.new('RGBA', (SIZE, SIZE), (14, 16, 19, 255)); d=ImageDraw.Draw(im)
for oy in (1, 17):
    for ox in (1, 17):
        rect(d, (ox,oy,ox+13,oy+13), (81,89,96,255))
        rect(d, (ox,oy,ox+12,oy+2), (237,243,243,255))
        rect(d, (ox,oy,ox+2,oy+12), (228,233,232,255))
        rect(d, (ox+3,oy+3,ox+11,oy+11), (168,179,183,255))
        rect(d, (ox+10,oy+4,ox+11,oy+11), (125,135,139,255))
        rect(d, (ox+3,oy+10,ox+11,oy+11), (108,119,126,255))
        rect(d, (ox+12,oy+2,ox+13,oy+13), (43,50,55,255))
        rect(d, (ox+2,oy+12,ox+13,oy+13), (38,45,50,255))
        rect(d, (ox+4,oy+4,ox+5,oy+5), (241,244,239,255))
save(im, 'steel')

# Ve bui cay
for variant in range(4):
    rng = random.Random(191 + variant)
    im = Image.new('RGBA', (SIZE, SIZE), (1, 17, 3, 255)); d=ImageDraw.Draw(im)
    for _ in range(235):
        x,y = rng.randrange(0,32),rng.randrange(0,32)
        sz = rng.choice([2,2,3,3,4])
        c = rng.choice([(18,84,8,255),(24,112,12,255),(39,140,8,255),
                        (61,174,12,255),(92,202,22,255),(120,224,24,255),(11,54,8,255)])
        rect(d, (x,y,min(31,x+sz),min(31,y+sz)),c)
    for _ in range(26):
        x,y=rng.randrange(32),rng.randrange(32)
        rect(d,(x,y,min(31,x+1),min(31,y+2)),(5,36,6,255))
    save(im, f'forest_{variant}')

# Ve Tank 4 huong
def tank(name, colors):
    shadow, track, hull, light, turret, barrel = colors
    im=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0)); d=ImageDraw.Draw(im)
    # Nong sung
    rect(d,(14,1,17,14),shadow)
    rect(d,(15,1,16,13),barrel)
    rect(d,(13,0,18,2),light)
    # Banh xich
    for x in (5,23):
        rect(d,(x,5,x+4,27),shadow)
        rect(d,(x+1,6,x+3,26),track)
        for y in range(7,27,5):
            rect(d,(x,y,x+4,y+1),light)
    # Than va thap phao
    rect(d,(10,6,22,27),shadow)
    rect(d,(11,8,21,26),hull)
    rect(d,(12,9,20,10),light)
    rect(d,(12,24,20,25),track)
    rect(d,(11,12,22,22),shadow)
    rect(d,(13,13,20,20),turret)
    rect(d,(15,14,18,17),light)
    rect(d,(14,19,19,20),track)
    for direction, angle in [('up',0),('left',90),('down',180),('right',270)]:
        save(im.rotate(angle,expand=False,resample=Image.Resampling.NEAREST), f'tank_{name}_{direction}')

tank('blue', ((12,31,43,255),(32,87,108,255),(59,171,199,255),(190,238,242,255),(31,108,143,255),(232,250,252,255)))
tank('gold', ((65,36,8,255),(128,80,15,255),(229,163,28,255),(255,235,131,255),(168,101,17,255),(255,243,179,255)))

# Ve Base
for name,edge in [('blue',(76,189,221,255)),('gold',(243,195,76,255))]:
    im=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0)); d=ImageDraw.Draw(im)
    rect(d,(3,3,28,28),(25,30,31,255))
    rect(d,(4,4,27,5),edge); rect(d,(4,26,27,27),edge)
    rect(d,(4,4,5,27),edge); rect(d,(26,4,27,27),edge)
    # Canh va than
    silver=(180,192,197,255); bright=(230,237,235,255); dark=(68,83,90,255)
    rect(d,(8,10,23,12),silver)
    rect(d,(6,12,12,14),silver); rect(d,(19,12,25,14),silver)
    rect(d,(8,15,13,18),dark); rect(d,(18,15,23,18),dark)
    rect(d,(11,13,20,16),bright)
    rect(d,(14,15,17,23),silver)
    rect(d,(12,20,19,21),bright)
    rect(d,(13,24,18,25),dark)
    rect(d,(15,9,16,12),edge)
    save(im, f'base_{name}')

# Hieu ung ban
im=Image.new('RGBA',(32,32),(0,0,0,0)); d=ImageDraw.Draw(im)
rect(d,(14,2,17,29),(255,222,74,255));rect(d,(2,14,29,17),(255,222,74,255))
rect(d,(7,7,24,24),(255,133,41,255))
rect(d,(11,11,20,20),(255,249,184,255))
rect(d,(14,14,17,17),(255,255,255,255))
save(im,'flash')
print('Pixel art assets generated:', len(list(ROOT.glob('*.png'))))
