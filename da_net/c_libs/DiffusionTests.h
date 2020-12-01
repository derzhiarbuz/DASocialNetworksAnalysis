#ifndef DIFFUSIONTESTS_H_INCLUDED
#define DIFFUSIONTESTS_H_INCLUDED

#ifdef  __cplusplus
extern "C" {
#endif

#include "Diffusion.h"

//theta = 0.02, delta = 0.02, rho = 0.001
extern double cascade_1[29][2];
//theta = 0.02, delta = 0.02, rho = 0.001
extern double cascade_2[25][2];
//theta = 0.02, delta = 0.02, rho = 0.001
extern double cascade_3[29][2];

extern DiffusionModelPtr diffusionModel;

void testLikelyhood();

#ifdef  __cplusplus
}
#endif

#endif // DIFFUSIONTESTS_H_INCLUDED
