// CPU adapter only: never a substitute for Resolve's UI parser or GPU compiler.
#pragma once
#include <cmath>
#include <vector>
#include <cstdint>
struct float3 { float x, y, z; };
struct UIPicker { float r, g, b; };
using uint = unsigned int;
static uint ys_frame_index = 0u;
inline float ys_rand(uint s) {
    uint x=s+0x9E3779B9u;
    x ^= x >> 16; x *= 0x7FEB352Du; x ^= x >> 15; x *= 0x846CA68Bu; x ^= x >> 16;
    return (float)(x & 0x00FFFFFFu) / 16777216.0f;
}
struct YSTexture { const float* data; int width; int height; float constant_value; };
inline float3 make_float3(float x, float y, float z) { return {x,y,z}; }
inline float ys_tex2d(YSTexture tex,int x,int y) {
    if (!tex.data) return tex.constant_value;
    int xx=x<0?0:(x>=tex.width?tex.width-1:x);
    int yy=y<0?0:(y>=tex.height?tex.height-1:y);
    return tex.data[yy*tex.width+xx];
}
#define __DEVICE__ inline
#define __TEXTURE__ YSTexture
#define TIMELINE_FRAME_INDEX ys_frame_index
#define RAND(seed) ys_rand((uint)(seed))
#define _tex2D(tex,x,y) ys_tex2d(tex,x,y)
#define _fminf std::fmin
#define _fmaxf std::fmax
#define _fabs std::fabs
#define _exp2f std::exp2
#define _expf std::exp
#define _log2f std::log2
#define _powf std::pow
#define _sqrtf std::sqrt
#define _floorf std::floor
#define _atan2f std::atan2
#define UI_DCTLUI_SLIDER_FLOAT(name,label,initial,...) float name = initial;
#define UI_DCTLUI_SLIDER_INT(name,label,initial,...) int name = initial;
#define UI_DCTLUI_VALUE_BOX(name,label,initial) float name = initial;
#define UI_DCTLUI_COMBO_BOX(name,label,initial,...) int name = initial;
#define UI_DCTLUI_CHECK_BOX(name,label,initial,...) int name = initial;
#define UI_DCTLUI_COLOR_PICKER(name,label,r,g,b) UIPicker name = {r,g,b};
#define DEFINE_UI_PARAMS(name,label,type,...) UI_##type(name,label,__VA_ARGS__)
#define DEFINE_UI_TOOLTIP(label,text)
