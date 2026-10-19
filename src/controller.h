#ifndef CONTROLLER_H
#define CONTROLLER_H
#include <stdbool.h>
#include <stdint.h>
typedef enum { IDLE, RUNNING, WARNING, FAULT } State;
typedef enum { OK, SENSOR_INVALID, SENSOR_STALE, OVERTEMP } Fault;
typedef struct { State state; Fault fault; float fan; unsigned healthy; } Controller;
void controller_init(Controller *c);
/* Call every 100 ms. Timestamp subtraction supports uint32_t wraparound. */
void controller_step(Controller *c, float temp, bool valid, uint32_t age_ms, bool enabled);
const char *state_name(State s);
const char *fault_name(Fault f);
#endif
