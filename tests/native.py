"""Compile the shipped shader with CPU float32 intrinsics. Not a Resolve emulator."""
from __future__ import annotations
import ctypes as C
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from build import SOURCE, controls, validate

MATH_EXPORTS = r'''
extern "C" float scalar(int op,float x,float a,float b,float c) {
    if(op==0) return ys_di_decode(x);
    if(op==1) return ys_di_encode(x);
    if(op==2) return ys_stops(x,a);
    if(op==3) return ys_tone(x,a);
    if(op==4) return ys_hue_weight(x,a,b,c);
    if(op==5) return ys_band(x,a,b,c);
    if(op==6) return ys_Y(ys_curve(ys_gray(x),a,b,c));
    if(op==7) return ys_quantize(x,(int)a);
    if(op==8) return ys_digit((int)x,(int)a,(int)b);
    if(op==9) return ys_picker_hue(make_float3(x,a,b),c);
    if(op==10) return ys_logc4_decode(x);
    if(op==11) return ys_slog3_decode(x);
    if(op==12) return ys_log3g10_decode(x);
    if(op==13) return ys_logc4_encode(x);
    if(op==14) return ys_slog3_encode(x);
    if(op==15) return ys_log3g10_encode(x);
    return -999.0f;
}
extern "C" void vector(int op,float r,float g,float b,float a,float c,float d,float* out) {
    float3 v=make_float3(r,g,b);
    if(op==0) v=ys_dwg_xyz(v); else if(op==1) v=ys_xyz_dwg(v);
    else if(op==2) v=ys_to709(v); else if(op==3) v=ys_from709(v);
    else if(op==4) v=ys_curve(v,a,c,d);
    else if(op==5) v=ys_gamut(v,ys_gamut_factor(v,a));
    else if(op==6) v=ys_hsv(v); else if(op==7) v=ys_hue_color(a);
    else if(op==8) v=ys_awg4_xyz(v); else if(op==9) v=ys_sgamut3cine_xyz(v);
    else if(op==10) v=ys_sgamut3_xyz(v); else if(op==11) v=ys_rwg_xyz(v);
    else if(op==12) v=ys_cat02_wb(v,a,c); else if(op==13) v=ys_input(v,(int)a);
    else if(op==14) v=ys_cct_xy(a);
    out[0]=v.x; out[1]=v.y; out[2]=v.z;
}
'''

class Shader:
    def __init__(self, source: Path = SOURCE, *, helpers: bool = True):
        text = source.read_text()
        validate(text)
        self.temp = tempfile.TemporaryDirectory(prefix='ysew-native-')
        self.ui = controls(text)
        self.ids = {row[0]: n for n, row in enumerate(self.ui)}
        self.types = {row[0]: row[2] for row in self.ui}
        compiler = os.environ.get('CXX') or shutil.which('clang++') or shutil.which('g++')
        if not compiler:
            raise RuntimeError('Install Clang/GCC or set CXX; tests must not silently skip.')
        reset = '\n'.join(f'{name}={default};' for name, _, _, default in self.ui)
        setters, pickers = [], []
        for i, (name, _, kind, _) in enumerate(self.ui):
            if kind == 'DCTLUI_COLOR_PICKER':
                pickers.append(f'case {i}: {name}=UIPicker{{r,g,b}}; break;')
            else:
                native_type = 'float' if kind == 'DCTLUI_SLIDER_FLOAT' else 'int'
                setters.append(f'case {i}: {name}=({native_type})value; break;')
        more = MATH_EXPORTS if helpers else ''
        if helpers:
            # Reuse the transform's actual parameter wiring rather than mirroring it.
            wiring = text.split('    YSGuideParams gp;', 1)[1].split('    return ys_graphic', 1)[0]
            more += '''extern "C" void guide_sample(float gray,float* out) {
                float skin_center=skin_pick_on ? ys_picker_hue(make_float3(skin_pick.r,skin_pick.g,skin_pick.b),skin_hue) : skin_hue;
                YSGuideParams gp;
            ''' + wiring + '''
                float3 v=ys_guide_curve(gray,gp); out[0]=v.x; out[1]=v.y; out[2]=v.z;
            }
            '''
        cpp = Path(self.temp.name)/'shader.cpp'
        cpp.write_text(f'''#include "{(ROOT/'tests/native_shim.hpp').as_posix()}"
#include "{source.as_posix()}"
extern "C" void reset_controls() {{ {reset} }}
extern "C" void set_control(int id,float value) {{ (void)value; switch(id) {{ {''.join(setters)} }} }}
extern "C" void set_picker(int id,float r,float g,float b) {{ (void)r; (void)g; (void)b; switch(id) {{ {''.join(pickers)} }} }}
extern "C" void pixel(float r,float g,float b,int w,int h,int x,int y,float* out) {{
    YSTexture tr{{nullptr,w,h,r}},tg{{nullptr,w,h,g}},tb{{nullptr,w,h,b}};
    float3 v=transform(w,h,x,y,tr,tg,tb); out[0]=v.x; out[1]=v.y; out[2]=v.z;
}}
extern "C" void render(int w,int h,float* out) {{
    std::vector<float> rr(w*h),gg(w*h),bb(w*h);
    for(int y=0;y<h;++y) for(int x=0;x<w;++x) {{
        float gray=0.18f*std::exp2(((float)x/(float)(w-1)*2.0f-1.0f)*6.0f);
        int i=y*w+x; rr[i]=gray; gg[i]=gray; bb[i]=gray;
    }}
    YSTexture tr{{rr.data(),w,h,0}},tg{{gg.data(),w,h,0}},tb{{bb.data(),w,h,0}};
    for(int y=0;y<h;++y) for(int x=0;x<w;++x) {{
        float3 v=transform(w,h,x,y,tr,tg,tb);
        int i=3*(y*w+x); out[i]=v.x; out[i+1]=v.y; out[i+2]=v.z;
    }}
}}
extern "C" void render_image(int w,int h,const float* rgb,float* out) {{
    std::vector<float> rr(w*h),gg(w*h),bb(w*h);
    for(int i=0;i<w*h;++i) {{ rr[i]=rgb[3*i]; gg[i]=rgb[3*i+1]; bb[i]=rgb[3*i+2]; }}
    YSTexture tr{{rr.data(),w,h,0}},tg{{gg.data(),w,h,0}},tb{{bb.data(),w,h,0}};
    for(int y=0;y<h;++y) for(int x=0;x<w;++x) {{
        float3 v=transform(w,h,x,y,tr,tg,tb);
        int i=3*(y*w+x); out[i]=v.x; out[i+1]=v.y; out[i+2]=v.z;
    }}
}}
{more}
''')
        library = Path(self.temp.name)/('shader.dylib' if sys.platform == 'darwin' else 'shader.so')
        completed = subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-shared','-fPIC',str(cpp),'-o',str(library)],
                                   text=True,capture_output=True,timeout=45)
        if completed.returncode:
            raise RuntimeError('CPU compilation failed:\n'+completed.stdout+completed.stderr)
        self.lib = C.CDLL(str(library))
        self.lib.reset_controls.argtypes = []
        self.lib.reset_controls.restype = None
        self.lib.set_control.argtypes = [C.c_int,C.c_float]
        self.lib.set_control.restype = None
        self.lib.set_picker.argtypes = [C.c_int]+[C.c_float]*3
        self.lib.set_picker.restype = None
        self.lib.pixel.argtypes = [C.c_float]*3+[C.c_int]*4+[C.POINTER(C.c_float)]
        self.lib.pixel.restype = None
        self.lib.render.argtypes = [C.c_int,C.c_int,C.POINTER(C.c_float)]
        self.lib.render.restype = None
        self.lib.render_image.argtypes = [C.c_int,C.c_int,C.POINTER(C.c_float),C.POINTER(C.c_float)]
        self.lib.render_image.restype = None
        if helpers:
            self.lib.scalar.argtypes = [C.c_int]+[C.c_float]*4
            self.lib.scalar.restype = C.c_float
            self.lib.vector.argtypes = [C.c_int]+[C.c_float]*6+[C.POINTER(C.c_float)]
            self.lib.vector.restype = None
            self.lib.guide_sample.argtypes = [C.c_float,C.POINTER(C.c_float)]
            self.lib.guide_sample.restype = None

    def reset(self):
        self.lib.reset_controls()

    def set(self, **kwargs):
        for name, value in kwargs.items():
            if self.types[name] == 'DCTLUI_COLOR_PICKER':
                if not isinstance(value,(tuple,list)) or len(value) != 3:
                    raise ValueError('Picker requires exactly three RGB numbers')
                self.lib.set_picker(self.ids[name],*value)
            else:
                self.lib.set_control(self.ids[name],value)

    def pixel(self,rgb,w=1920,h=1080,x=960,y=540):
        out=(C.c_float*3)(); self.lib.pixel(*rgb,w,h,x,y,out); return tuple(out)

    def scalar(self,op,x,a=0,b=0,c=0):
        return self.lib.scalar(op,x,a,b,c)

    def vector(self,op,rgb,a=0,b=0,c=0):
        out=(C.c_float*3)(); self.lib.vector(op,*rgb,a,b,c,out); return tuple(out)

    def guide(self,gray):
        out=(C.c_float*3)(); self.lib.guide_sample(gray,out); return tuple(out)

    def render(self,w,h):
        if w<2 or h<1:
            raise ValueError('Invalid render dimensions')
        out=(C.c_float*(w*h*3))(); self.lib.render(w,h,out); return out

    def render_image(self,pixels,w,h):
        if len(pixels)!=w*h*3:
            raise ValueError('Expected interleaved RGB image data')
        inp=(C.c_float*(w*h*3))(*pixels); out=(C.c_float*(w*h*3))()
        self.lib.render_image(w,h,inp,out); return tuple(out)
