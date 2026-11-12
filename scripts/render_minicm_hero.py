#!/usr/bin/env python3
"""Build the MiniCM profile's one-piece Xperia photo hero from attributed Wikimedia Commons photos."""
from pathlib import Path
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"profile/assets/minicm-photo-hero.png"
W,H=1600,874
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def font(path,size): return ImageFont.truetype(path,size)
B=lambda s:font(BOLD,s)
M=lambda s:font(MONO,s)
R=lambda s:font(FONT,s)

devices=[
 ("Xperia X8","shakira · E15i","Sony_Ericsson_Xperia_X8_-_Front.jpg"),
 ("Xperia X10 Mini","robyn · E10i","Sony_Ericsson_Xperia_X10_mini_-_Front.jpg"),
 ("Xperia X10 Mini Pro","mimmi · U20i","Sony_Ericsson_Xperia_X10_mini_pro_-_Front_(Open).jpg"),
]
session=requests.Session()
session.headers.update({"User-Agent":"MiniCM-HistoricalArchive/1.0 (source attribution at github.com/MiniCM-Project/.github)"})
def fetch_photo(name):
    url="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+requests.utils.quote(name,safe="")
    response=session.get(url,timeout=55)
    response.raise_for_status()
    if not response.headers.get("content-type","").startswith("image/"):
        raise RuntimeError("Not an image: "+str(response.url)+" "+response.headers.get("content-type",""))
    img=Image.open(BytesIO(response.content))
    img.load()
    return ImageOps.exif_transpose(img).convert("RGB")

img=Image.new("RGB",(W,H))
pixels=img.load()
for y in range(H):
    for x in range(W):
        # subtle muted teal gradient
        glow=max(0.0,1-(abs(x-1320)/1250)**1.3-(abs(y-115)/860)**1.4)
        pixels[x,y]=(round(5+12*glow+y/H*2),round(24+28*glow+y/H*3),round(31+26*glow+y/H*4))
d=ImageDraw.Draw(img)
for x in range(39,W,29):d.line((x,16,x,H-15),fill=(11,48,53),width=1)
for y in range(34,H,29):d.line((17,y,W-18,y),fill=(12,49,53),width=1)
d.rounded_rectangle((15,15,W-16,H-16),radius=29,outline=(59,193,165),width=2)
d.text((62,60),"MINICM / XPERIA LEGACY  ·  2010–2013",fill=(100,234,193),font=M(21))
d.text((60,111),"Mini",fill=(247,255,250),font=B(142))
d.text((367,111),"CM",fill=(99,227,176),font=B(142))
d.text((65,271),"THE LITTLE XPERIAS THAT COULD.",fill=(235,255,247),font=B(37))
d.text((65,332),"Unofficial CyanogenMod and nAa Kernel development for the original",fill=(156,203,194),font=R(21))
d.text((65,359),"Sony Ericsson Xperia family.",fill=(156,203,194),font=R(21))
top=409; card_w=471; gap=29; card_h=348
for i,(title,code,filename) in enumerate(devices):
    x=64+i*(card_w+gap)
    y=top
    d.rounded_rectangle((x,y,x+card_w,y+card_h),radius=18,fill=(10,40,47),outline=(53,129,117),width=2)
    d.rounded_rectangle((x+2,y+2,x+card_w-2,y+254),radius=16,fill=(243,246,247))
    d.rectangle((x+2,y+235,x+card_w-2,y+254),fill=(243,246,247))
    source=fetch_photo(filename)
    fit=ImageOps.contain(source,(card_w-70,250),Image.Resampling.LANCZOS)
    xp=x+(card_w-fit.width)//2
    yp=y+5+(247-fit.height)//2
    img.paste(fit,(xp,yp))
    d.rectangle((x+2,y+254,x+card_w-2,y+card_h-2),fill=(9,38,45))
    d.text((x+24,y+268),title,fill=(244,255,251),font=B(28))
    d.text((x+24,y+310),code,fill=(113,236,205),font=M(21))
d.line((65,787,1534,787),fill=(58,132,117),width=2)
d.text((65,808),"MINICM6 · MINICM7 · MINICM9 · MINICM10",fill=(130,205,192),font=M(18))
d.text((1138,808),"nobodyAtall (nAa) · XDA",fill=(130,205,192),font=M(18))
OUT.parent.mkdir(parents=True,exist_ok=True)
img.save(OUT,optimize=True)
print("Created",OUT,OUT.stat().st_size,"bytes")
