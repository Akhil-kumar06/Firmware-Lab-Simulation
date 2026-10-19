#include "controller.h"
#include <stdio.h>
#include <string.h>
/* Pipe commands: normal, disconnect, stale, heat, off, on, quit.
   Each input line advances exactly 100 ms of simulated time. */
int main(void) {
    Controller c; controller_init(&c);
    char command[64]; float plant=30, sample=30;
    unsigned tick=0,last_sample=0; int mode=0; bool enabled=true;
    while(fgets(command,sizeof command,stdin)) {
        command[strcspn(command,"\r\n")]=0;
        if(!strcmp(command,"quit")) break;
        if(!strcmp(command,"normal")) mode=0;
        else if(!strcmp(command,"disconnect")) mode=1;
        else if(!strcmp(command,"stale")) mode=2;
        else if(!strcmp(command,"heat")) mode=3;
        else if(!strcmp(command,"off")) enabled=false;
        else if(!strcmp(command,"on")) enabled=true;
        tick+=100;
        /* Educational first-order thermal model, not physical calibration. */
        float heat=(mode==3)?35.0f:3.0f;
        plant+=0.1f*(heat-0.10f*(plant-25)-12*c.fan);
        if(mode!=2) { sample=plant; last_sample=tick; }
        controller_step(&c,sample,mode!=1,tick-last_sample,enabled);
        printf("{\"ms\":%u,\"temperature\":%.2f,\"fan\":%.3f,\"state\":\"%s\",\"fault\":\"%s\",\"age_ms\":%u}\n",
            tick,sample,c.fan,state_name(c.state),fault_name(c.fault),tick-last_sample);
        fflush(stdout);
    }
    return 0;
}
