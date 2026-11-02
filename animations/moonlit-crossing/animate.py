#!/usr/bin/env python3
"""Moonlit Crossing — original procedural 12-second animated film.
Requires: pillow, numpy, imageio-ffmpeg. No external images or music.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import math, random, wave, subprocess
from pathlib import Path
import imageio_ffmpeg

W,H,FPS,SEC=960,540,24,12
OUT=Path(__file__).resolve().parent
rng=random.Random(2411)
stars=[(rng.randrange(8,W-8),rng.randrange(8,265),rng.uniform(0.7,2.0),rng.uniform(0,6.28)) for _ in range(155)]
fireflies=[(rng.randrange(W),rng.randrange(400,H),rng.uniform(0.9,3),rng.uniform(0,7)) for _ in range(38)]
water_lines=[(rng.randrange(-5,W),rng.randrange(399,H),rng.randrange(12,72),rng.random()*6.28) for _ in range(170)]
try:
    titlefont=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',32)
    smallfont=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
except OSError:
    titlefont=ImageFont.load_default()
    smallfont=ImageFont.load_default()

y=np.linspace(0,1,H)[:,None,None]
top=np.array([8,13,35])[None,None,:]
bottom=np.array([42,52,78])[None,None,:]
base=np.clip(top*(1-y)+bottom*y,0,255).astype('uint8')
base=np.repeat(base,W,axis=1)
sky=Image.fromarray(base,'RGB')
def easing(v):
    v=max(0,min(1,v)); return v*v*(3-2*v)
def glow(draw,x,y,r,rgba):
    # concentric transparent circles with a bright inner core
    for radius,alpha in [(r*4,rgba[3]//12),(r*2.5,rgba[3]//6),(r*1.6,rgba[3]//3),(r,rgba[3])]:
        draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(*rgba[:3],alpha))

def frame(idx):
    t=idx/FPS
    im=sky.copy().convert("RGBA")
    d=ImageDraw.Draw(im,"RGBA")
    # soft distant vertical aurora
    for n in range(7):
        x=105+n*115+17*math.sin(t*.13+n)
        d.polygon([(x-80,0),(x+35,0),(x+120,310),(x+25,310)],fill=(57,114,135,8))
    # stars shimmer, no raster/image assets
    for x,sy,r,phase in stars:
        v=.55+.45*math.sin(t*1.6+phase)**2
        b=int(95+160*v)
        d.ellipse((x-r/2,sy-r/2,x+r/2,sy+r/2),fill=(180,213,244,b))
    # large moon, halo
    mx,my=760,113
    glow(d,mx,my,39,(185,221,255,105))
    d.ellipse((mx-32,my-32,mx+32,my+32),fill=(238,241,226,255))
    d.ellipse((mx-19,my-14,mx-8,my-4),fill=(191,203,203,64))
    d.ellipse((mx+9,my+5,mx+20,my+15),fill=(191,203,203,40))
    # drifting layered clouds
    for j,(cx,cy,scale) in enumerate([(-130,90,1.05),(300,150,.9),(695,68,.7)]):
        xx=(cx+t*(10+j*2))%1230-150
        for dx,dy,rr in [(-44,7,26),(0,-7,34),(36,5,25),(70,14,18)]:
            d.ellipse((xx+(dx-rr)*scale,cy+(dy-rr*.5)*scale,xx+(dx+rr)*scale,cy+(dy+rr*.6)*scale), fill=(50,65,95,82))
    # mountain silhouettes
    d.polygon([(0,314),(0,265),(125,300),(240,222),(352,299),(470,245),(585,294),(709,218),(845,295),(960,264),(960,365)],fill=(22,35,62,255))
    d.polygon([(0,341),(0,302),(132,350),(258,270),(360,337),(515,290),(630,344),(795,282),(960,337),(960,410)],fill=(17,30,51,255))
    # small snowcaps, pale in moonlight
    for peak in [(240,222),(709,218),(258,270),(795,282)]:
        x0,y0=peak
        d.polygon([(x0-16,y0+17),(x0,y0),(x0+21,y0+23),(x0+7,y0+18),(x0-2,y0+12)],fill=(113,134,158,94))
    # waters, dark blue depths
    d.rectangle((0,395,W,H),fill=(12,29,54,255))
    for k in range(28):
        yy=400+k*5
        d.line([(0,yy),(W,yy)],fill=(27,61,83,max(15,43-k)),width=1)
    # distant moon reflection, dancing broken light
    for k in range(33):
        yy=405+k*4.4
        width=8+(k*1.75)
        jitter=24*math.sin(k*1.9+t*2.2)
        cx=760+jitter
        d.line((cx-width/2,yy,cx+width/2,yy),fill=(205,224,198,max(9,82-int(k*1.7))),width=2)
    # bridge supporting pillars and rails
    for px in range(20,W,135):
        d.polygon([(px-11,374),(px+10,374),(px+4,H),(px-4,H)],fill=(14,23,39,255))
        d.line((px-40,393,px+70,466),fill=(17,28,43,225),width=3)
        d.line((px+64,393,px-35,466),fill=(17,28,43,225),width=3)
    d.rectangle((0,368,W,379),fill=(15,23,36,255))
    d.line((0,364,W,364),fill=(70,83,94,255),width=3)
    d.line((0,379,W,379),fill=(8,18,33,255),width=5)
    # rippling water highlights
    for k,(xx,yy,ww,ph) in enumerate(water_lines):
        ofs=19*math.sin(t*1.25+ph)
        alpha=max(14,55-int((yy-399)*.18))
        d.line((xx+ofs,yy,xx+ww+ofs,yy),fill=(67,126,144,alpha),width=1)
    # train passes from left to right, first locomotive then carriages
    progress=easing(t/SEC)
    tx=-710+progress*2410
    ty=304+1.3*math.sin(t*13)
    # train nose headlamp glow
    glow(d,tx+508,ty+38,15,(255,197,99,84))
    # carriages, each with roof and glowing windows
    for i in range(3):
        x=tx+i*158
        d.rounded_rectangle((x,ty+5,x+153,ty+62),radius=7,fill=(37,66,81,255),outline=(94,124,134,255),width=2)
        d.rounded_rectangle((x+8,ty,x+147,ty+13),radius=5,fill=(70,94,105,255))
        for col in range(4):
            wx=x+14+col*34
            d.rounded_rectangle((wx,ty+21,wx+23,ty+44),radius=3,fill=(255,199,111,255),outline=(252,228,169,255),width=1)
            d.line((wx+12,ty+21,wx+12,ty+44),fill=(138,93,74,180),width=2)
        d.line((x+5,ty+51,x+149,ty+51),fill=(198,157,104,180),width=3)
        for wheel in (x+31,x+125):
            d.ellipse((wheel-10,ty+54,wheel+10,ty+73),fill=(13,21,32,255),outline=(92,106,115,255),width=2)
            d.ellipse((wheel-3,ty+61,wheel+3,ty+67),fill=(105,119,123,255))
    # streamlined engine
    x=tx+468
    d.polygon([(x,ty+13),(x+52,ty+13),(x+76,ty+35),(x+76,ty+57),(x,ty+57)],fill=(62,96,105,255))
    d.polygon([(x+48,ty+18),(x+60,ty+25),(x+25,ty+25),(x+25,ty+18)],fill=(253,190,105,255))
    d.line((x,ty+48,x+75,ty+48),fill=(236,181,101,255),width=3)
    d.ellipse((x+68,ty+31,x+78,ty+42),fill=(255,237,180,255))
    for wheel in [x+19,x+58]:
        d.ellipse((wheel-10,ty+54,wheel+10,ty+73),fill=(12,20,29,255),outline=(96,110,118,255),width=2)
    # foreground trees frame the picture
    for root,flip in [(44,1),(915,-1)]:
        d.polygon([(root-9,H),(root-5,367),(root+6,350),(root+13,H)],fill=(6,20,28,255))
        for level in range(5):
            yy=380+level*27
            hh=92-level*11
            d.polygon([(root,yy-hh),(root-56+level*4,yy+24),(root+56-level*4,yy+24)],fill=(8+level,30+level*2,33+level,254))
    # translucent fireflies in front
    for fx,fy,r,phase in fireflies:
        x=fx+9*math.sin(.8*t+phase)
        y=fy+8*math.sin(.53*t+phase*2)
        glow(d,x,y,r,(201,228,133,int(74+50*math.sin(t*2+phase)**2)))
    # discreet titles fade in/out
    a=int(228*easing(t/.9)*(1-easing((t-3.8)/1.1)))
    if a:
        d.text((48,53),"MOONLIT CROSSING",font=titlefont,fill=(244,238,214,a),stroke_width=0)
        d.text((50,101),"An original animated journey",font=smallfont,fill=(183,207,216,a))
    # cinematic letterbox
    d.rectangle((0,0,W,17),fill=(2,6,14,255))
    d.rectangle((0,H-17,W,H),fill=(2,6,14,255))
    # gentle fade in and out
    opacity=int(255*max(1-easing(t/.8),easing((t-11.35)/.65)))
    if opacity>0:
        d.rectangle((0,0,W,H),fill=(3,7,15,opacity))
    return im.convert('RGB')

def make_audio(dest):
    sr=22050
    tt=np.arange(sr*SEC,dtype=np.float64)/sr
    audio=np.zeros(tt.size,dtype=np.float64)
    # entirely original ambient progression A minor -> F major -> C major
    chords=[(0,4,[220,261.6256,329.6276]),(4,8,[174.614,220,261.6256]),(8,12,[261.6256,329.6276,391.9954])]
    for start,end,notes in chords:
        env=np.clip((tt-start)/1.5,0,1)*np.clip((end-tt)/1.7,0,1)
        for j,f in enumerate(notes):
            audio+=env*(.065/(j+1))*(np.sin(2*np.pi*f*tt)+.17*np.sin(2*np.pi*f*1.003*tt))
    # train pulse and soft rolling rumble under the soundtrack
    cadence=.006*np.sin(2*np.pi*(3.2+tt*.09)*tt)
    envelope=np.clip((tt-2.2)/1.6,0,1)*np.clip((11.7-tt)/1.8,0,1)
    audio+=cadence*envelope
    audio*=np.clip(tt/.7,0,1)*np.clip((SEC-tt)/.8,0,1)
    audio=np.int16(np.clip(audio,-.95,.95)*32767)
    with wave.open(str(dest),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(audio.tobytes())

def main():
    out=OUT/'moonlit_crossing.mp4'
    silent=OUT/'_temp_silent.mp4'
    wav=OUT/'_temp_audio.wav'
    print(f'Rendering {SEC}s at {W}x{H} and {FPS}fps',flush=True)
    wr=imageio_ffmpeg.write_frames(str(silent),(W,H),fps=FPS,codec='libx264',quality=7,
        output_params=['-movflags','+faststart'],ffmpeg_log_level='error')
    wr.send(None)
    for i in range(FPS*SEC):
        wr.send(np.asarray(frame(i),dtype='uint8').tobytes())
        if i%72==0:print(f'frame {i}/{FPS*SEC}',flush=True)
    wr.close()
    print('Generating original soundtrack',flush=True)
    make_audio(wav)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y',
        '-i',str(silent),'-i',str(wav),'-c:v','copy','-c:a','aac','-b:a','128k',
        '-shortest','-movflags','+faststart',str(out)],check=True)
    frame(144).save(OUT/'moonlit_crossing_poster.png')
    silent.unlink(missing_ok=True);wav.unlink(missing_ok=True)
    print(f'DONE {out} ({out.stat().st_size/1024/1024:.2f} MiB)',flush=True)

if __name__=='__main__':
    main()

