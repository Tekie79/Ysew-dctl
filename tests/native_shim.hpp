// CPU adapter only: never a substitute for Resolve's UI parser or GPU compiler.
#pragma once
#include <cmath>
struct float3 { float x, y, z; };
struct UIPicker { float r, g, b; };
inline float3 make_float3(float x, float y, float z) { return {x,y,z}; }
#define __DEVICE__ inline
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
#define UI_DCTLUI_COMBO_BOX(name,label,initial,...) int name = initial;
#define UI_DCTLUI_CHECK_BOX(name,label,initial,...) int name = initial;
#define UI_DCTLUI_COLOR_PICKER(name,label,r,g,b) UIPicker name = {r,g,b};
#define DEFINE_UI_PARAMS(name,label,type,...) UI_##type(name,label,__VA_ARGS__)
#define DEFINE_UI_TOOLTIP(label,text)
