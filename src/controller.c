#include "controller.h"
#include <math.h>
void controller_init(Controller *c) { *c=(Controller){IDLE,OK,0,0}; }
void controller_step(Controller *c,float t,bool valid,uint32_t age,bool enabled) {
    Fault f=OK;
    if (!valid || !isfinite(t) || t < -40 || t > 150) f=SENSOR_INVALID;
    else if (age > 500) f=SENSOR_STALE;
    else if (t >= 80) f=OVERTEMP;
    if(f!=OK) { c->state=FAULT; c->fault=f; c->healthy=0; c->fan=1; return; }
    /* Recover only after 10 consecutive healthy samples below 65 C. */
    if(c->state==FAULT) {
        c->healthy = t<65 ? c->healthy+1 : 0;
        if(c->healthy<10) { c->fan=1; return; }
    }
    c->fault=OK; c->healthy=0;
    if(!enabled) { c->state=IDLE; c->fan=0; return; }
    /* Warning hysteresis prevents threshold chatter. */
    c->state=(t>=65 || (c->state==WARNING && t>60)) ? WARNING : RUNNING;
    c->fan=(t-35)/30;
    if(c->fan<0) c->fan=0;
    if(c->fan>1) c->fan=1;
}
const char *state_name(State s) {
    static const char *n[]={"IDLE","RUNNING","WARNING","FAULT"};
    return (s>=IDLE && s<=FAULT)?n[s]:"UNKNOWN";
}
const char *fault_name(Fault f) {
    static const char *n[]={"OK","SENSOR_INVALID","SENSOR_STALE","OVERTEMP"};
    return (f>=OK && f<=OVERTEMP)?n[f]:"UNKNOWN";
}
