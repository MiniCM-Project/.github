#!/usr/bin/env python3
"""Render four seamless, lightweight GIF headings in the MiniCM visual language."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

ROOT=Path(__file__).resolve().parents[1]/"profile/assets/sections"
ROOT.mkdir(parents=True,exist_ok=True)
W,H=1100,170
FONTS="/usr/share/fonts/truetype/dejavu"
def ft(sz,bold=False,mono=False):
    return ImageFont.truetype(FONTS+("/DejaVuSansMono.ttf" if mono else "/DejaVuSans-Bold.ttf" if bold else "/DejaVuSans.ttf"),sz)
WHITE=(233,255,251); MINT=(78,241,195); CYAN=(105,223,202); GRID=(19,72,77)
rows=[
("01_roms_v2.gif","01",["THE ROMS"],"MINICM6 / MINICM7 / MINICM9 / MINICM10","roms"),
("02_kernel_v2.gif","02",["nAa KERNEL"],"LINUX KERNEL / XPERIA HARDWARE / RECOVERY","kernel"),
("03_xda_v2.gif","03",["XDA RELEASES","& ACHIEVEMENTS"],"ORIGINAL THREADS / DEVELOPMENT MILESTONES","xda"),
("04_community_v2.gif","04",["THE COMMUNITY"],"OPEN SOURCE / TESTERS / CONTRIBUTORS","community"),
]
def blend(c1,c2,t):
    return tuple(int(a+(b-a)*t) for a,b in zip(c1,c2))
def rounded(d,coords,r,outline,width=2,fill=None):
    d.rounded_rectangle(coords,radius=r,outline=outline,width=width,fill=fill)
def icon(d,kind):
    ink=MINT
    if kind=="roms":
        for y in (52,79,106):
            rounded(d,(144,y,205,y+20),5,ink,3)
            d.ellipse((154,y+8,159,y+13),fill=ink)
            d.line((171,y+10,195,y+10),fill=ink,width=2)
    elif kind=="kernel":
        rounded(d,(148,61,203,113),6,ink,3)
        d.text((157,67),"nAa",font=ft(18,True),fill=WHITE)
        for x in (157,171,185,199):
            d.line((x,53,x,60),fill=ink,width=3)
            d.line((x,114,x,122),fill=ink,width=3)
        for y in (70,85,100):
            d.line((139,y,147,y),fill=ink,width=3)
            d.line((204,y,213,y),fill=ink,width=3)
    elif kind=="xda":
        d.rounded_rectangle((160,57,189,94),radius=4,outline=ink,width=3)
        d.line((155,59,145,59,148,83,160,89),fill=ink,width=3)
        d.line((192,59,204,59,200,82,189,89),fill=ink,width=3)
        d.line((175,95,175,113),fill=ink,width=3)
        d.line((159,114,190,114),fill=ink,width=4)
    elif kind=="community":
        for x,y,r in [(159,70,11),(192,70,11),(176,59,13)]:
            d.ellipse((x-r,y-r,x+r,y+r),outline=ink,width=3)
        for xy in [(142,86,166,114),(187,86,213,114),(153,80,200,120)]:
            rounded(d,xy,11,ink,2)
def frame(heading,num,lines,subtitle,kind,i,n):
    phase=math.tau*i/n
    base=Image.new("RGB",(W,H),(6,36,42))
    d=ImageDraw.Draw(base)
    for x in range(0,W,28):d.line((x,0,x,H),fill=(13,57,62),width=1)
    for y in range(0,H,28):d.line((0,y,W,y),fill=(13,57,62),width=1)
    rounded(d,(2,2,W-3,H-3),16,(38,128,113),2)
    rounded(d,(27,30,103,139),11,(51,198,162),2)
    rounded(d,(125,30,223,139),13,(38,140,123),2)
    d.text((40,57),num,font=ft(43,mono=True),fill=(115,250,218))
    icon(d,kind)
    if len(lines)==2:
        d.text((251,25),lines[0],font=ft(38,True),fill=WHITE)
        d.text((251,71),lines[1],font=ft(38,True),fill=WHITE)
        d.text((253,141),subtitle,font=ft(12,mono=True),fill=(110,221,204))
    else:
        d.text((251,42),lines[0],font=ft(49 if len(lines[0])<15 else 42,True),fill=WHITE)
        d.text((253,112),subtitle,font=ft(14,mono=True),fill=(110,221,204))
    # circuit traces, original layout, with periodic glow that closes seamlessly
    d.line((900,45,1032,45,1060,73),fill=(44,140,132),width=3)
    d.line((1030,145,1060,115,1060,79),fill=(44,140,132),width=3)
    d.line((950,100,1017,100),fill=(25,110,111),width=2)
    d.arc((1001,57,1082,152),-46,42,fill=MINT,width=2)
    d.ellipse((895,40,905,50),fill=MINT)
    d.ellipse((1055,110,1065,120),outline=MINT,width=2)
    # The light stays in place and breathes smoothly. Identical phase at wrap.
    strength=.5-.5*math.cos(phase)
    glow=Image.new("RGBA",(W,H),(0,0,0,0));g=ImageDraw.Draw(glow)
    alpha=int(25+110*strength)
    g.ellipse((883,28,919,63),fill=(37,255,210,alpha))
    g.ellipse((1043,98,1077,132),fill=(37,255,210,alpha))
    glow=glow.filter(ImageFilter.GaussianBlur(12))
    base=Image.alpha_composite(base.convert("RGBA"),glow)
    # Clearly visible continuously cycling light sweep. Its position returns
    # smoothly to the start without a jump, and all text remains stationary.
    sweep_t=.5-.5*math.cos(phase)
    sweep_x=260+750*sweep_t
    sweep=Image.new("RGBA",(W,H),(0,0,0,0))
    beam=ImageDraw.Draw(sweep)
    # Soft vertical light traveling across the subtitle and title area.
    beam.rounded_rectangle((int(sweep_x-45),18,int(sweep_x+45),151),
                           radius=26,fill=(58,255,190,48))
    beam.line((int(sweep_x),26,int(sweep_x),145),fill=(108,255,205,100),width=5)
    sweep=sweep.filter(ImageFilter.GaussianBlur(19))
    base=Image.alpha_composite(base,sweep)
    d=ImageDraw.Draw(base)
    # Bright moving traces with a wide visible trail on the top and bottom
    # strokes; at the turning points, movement slows naturally.
    y_top=3
    left=max(5,int(sweep_x-54));right=min(W-5,int(sweep_x+54))
    d.line((left,y_top,right,y_top),fill=(101,255,203,255),width=3)
    d.line((left,H-4,right,H-4),fill=(67,228,183,255),width=3)
    # Larger pulsing circuit segment rather than near-invisible dots.
    electric=(math.sin(phase-math.pi/2)+1)/2
    bright=(int(65+125*electric),int(172+78*electric),int(158+68*electric),255)
    d.line((902,45,1032,45,1060,74),fill=bright,width=5)
    d.line((1030,145,1060,115),fill=bright,width=5)
    d.ellipse((896,41,904,49),fill=blend((34,160,143),MINT,strength))
    d.ellipse((1057,112,1063,118),fill=blend((40,150,138),MINT,strength))
    return base.convert("RGB")
for name,num,lines,sub,kind in rows:
    count=40
    frames=[frame(name,num,lines,sub,kind,i,count) for i in range(count)]
    frames[0].save(ROOT/name,save_all=True,append_images=frames[1:],duration=75,loop=0,optimize=True,disposal=2)
    print(name,(ROOT/name).stat().st_size)
