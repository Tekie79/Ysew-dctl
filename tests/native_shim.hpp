// CPU test adapter only. This is NOT Blackmagic's compiler, GPU SDK or Resolve host.
#pragma once
#include <cmath>
struct float3 { float x, y, z; };
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
#define UI_TYPE_DCTLUI_COMBO_BOX int
#define UI_TYPE_DCTLUI_CHECK_BOX int
#define UI_TYPE_DCTLUI_SLIDER_INT int
#define UI_TYPE_DCTLUI_SLIDER_FLOAT float
#define DEFINE_UI_PARAMS(name,label,type,initial,...) UI_TYPE_##type name = initial;
