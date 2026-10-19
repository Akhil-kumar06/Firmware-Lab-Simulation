#include "controller.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#define CHECK(x) do { if(!(x)) { fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x); exit(1); } } while(0)
int main(void) {
 Controller c; controller_init(&c); CHECK(c.state==IDLE);
 controller_step(&c,30,true,0,true); CHECK(c.state==RUNNING && c.fan==0);
 controller_step(&c,65,true,0,true); CHECK(c.state==WARNING && c.fan==1);
 controller_step(&c,62,true,0,true); CHECK(c.state==WARNING);
 controller_step(&c,60,true,0,true); CHECK(c.state==RUNNING);
 controller_step(&c,40,false,0,true); CHECK(c.fault==SENSOR_INVALID && c.fan==1);
 for(int i=0;i<9;i++) controller_step(&c,40,true,0,true);
 CHECK(c.state==FAULT);
 controller_step(&c,40,true,0,true); CHECK(c.state==RUNNING);
 controller_step(&c,40,true,500,true); CHECK(c.state==RUNNING);
 controller_step(&c,40,true,501,true); CHECK(c.fault==SENSOR_STALE);
 controller_step(&c,NAN,true,0,true); CHECK(c.fault==SENSOR_INVALID);
 controller_step(&c,INFINITY,true,0,true); CHECK(c.fault==SENSOR_INVALID);
 controller_step(&c,-41,true,0,true); CHECK(c.fault==SENSOR_INVALID);
 controller_step(&c,151,true,0,true); CHECK(c.fault==SENSOR_INVALID);
 controller_step(&c,80,true,0,true); CHECK(c.fault==OVERTEMP);
 for(int i=0;i<20;i++) controller_step(&c,65,true,0,true);
 CHECK(c.state==FAULT); /* Cannot recover while hot. */
 for(int i=0;i<9;i++) controller_step(&c,40,true,0,true);
 controller_step(&c,40,false,0,true); /* Interrupted recovery resets count. */
 controller_step(&c,40,true,0,true); CHECK(c.state==FAULT);
 for(int i=0;i<9;i++) controller_step(&c,40,true,0,false);
 CHECK(c.state==IDLE && c.fan==0);
 controller_step(&c,80,true,0,false); CHECK(c.state==FAULT && c.fan==1);
 puts("Controller checks passed: thresholds, hysteresis, faults, recovery, disable.");
 return 0;
}
