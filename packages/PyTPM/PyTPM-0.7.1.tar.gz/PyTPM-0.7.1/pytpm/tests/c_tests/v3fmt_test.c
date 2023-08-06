#include "tpm/vec.h"
#include <stdio.h>


int main() {
  V3 v3;
  #define L 2
  double v[L][3] = {
    {1.0, 2.0, 3.0},
    { 10.0, 0.2, -0.234}
  };

  v3 = v3init(SPHERICAL);

  for(int i=0; i < L; i++){
    v3SetR(v3, v[i][0]);
    v3SetAlpha(v3, v[i][1]);
    v3SetDelta(v3, v[i][2]);

    printf("%0.8f %0.8f %0.8f\n\n\n", v3GetR(v3), v3GetAlpha(v3), 
           v3GetDelta(v3));
    printf("%s\n", v3fmt(v3));

  }
  
  v3 = v3init(CARTESIAN);

  v3SetX(v3, 112.4);
  v3SetY(v3, 2234.0);
  v3SetZ(v3, 322.0);

  printf("%0.8f %0.8f %0.8f\n\n\n", v3GetX(v3), v3GetY(v3), 
         v3GetZ(v3));
  printf("%s\n", v3fmt(v3));

  return 0;
}
