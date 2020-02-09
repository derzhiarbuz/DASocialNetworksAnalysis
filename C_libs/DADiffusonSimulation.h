#ifndef _DADIFFUSIONSIMULATION_H_
#define _DADIFFUSIONSIMULATION_H_

#ifdef  __cplusplus
extern "C" {
#endif

#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <malloc.h>

typedef struct Nod Node;
typedef Node* NodePtr;
struct Nod {
    int32_t id;
    NodePtr *neigbors;
    int32_t actual_degree;
    int32_t nominal_degree;
    void* payload;
};

NodePtr newNodePtr();
void clearNodePtr(NodePtr ptr);
int NodeCompare(const void *, const void *);


typedef struct Netw Network;
struct Netw {
    NodePtr *nodes;
    int32_t N;
};

Network und_network;
int32_t echo;


int32_t hello_func(int32_t a);
void DADSEchoOn();
void DADSEchoOff();
void DADSLog(char *text, ...);

//state machine
//**************************************************
//state variables
//**************************************************



//**************************************************
//functions
//**************************************************
//utilities
void DADSInitNetwork();
void DADSCleatNetwork();
NodePtr DADSNodeForId(int32_t id);
//loading
void DADSLoadNetworkFromFile(const char * fname);
void DADSSetMetaForNode(int32_t node_id, int32_t nominal_degree, int32_t diactivated);
void DADSPurifyNetwork(); //removing disabled vertices, filling missed values with medians
void DADSAddInfectionCase(int32_t node_id, double t);
//model estimation
void DADSPrepareForEstimation();
double DADSLogLikelyhoodTKDR(double theta, double kappa, double delta, double rho);

#ifdef  __cplusplus
}
#endif

#endif  /* _DADIFFUSIONSIMULATION_H_ */
