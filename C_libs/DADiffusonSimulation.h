// Created by Gubanov Alexander (aka Derzhiarbuz) at 06.02.2020
// Contacts: derzhiarbuz@gmail.com

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

typedef enum {Passive, NS, S, I} NodeState;

typedef struct ICas ICase;

typedef struct Nod Node;
typedef Node* NodePtr;
struct Nod {
    int32_t id;
    NodePtr *neigbors;
    int32_t actual_degree;
    int32_t nominal_degree;
    void* payload;
    NodeState state;
    double theta;
};

NodePtr newNodePtr();
void clearNodePtr(NodePtr ptr);
int NodeCompare(const void *, const void *);

typedef struct Netw Network;
struct Netw {
    NodePtr *nodes;
    int32_t N;
    ICase *cases;
    int32_t N_cases;

    NodePtr *nodes_to_check; //array of nodes that have infected neighbors
    int32_t N_nodes_to_check;
};

struct ICas {
    NodePtr node;
    double time;
    int32_t index;
    double value1;
    double value2;
};

int ICaseCompare(const void *, const void *);
int int32Compare(const void *c1, const void *c2);


Network und_network;
int32_t echo;
double *dlldthetas;
int32_t n_dlldthetas;


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
void DADSClearNetwork();
NodePtr DADSNodeForId(int32_t id);
ICase DADSICaseForNodePtr(NodePtr node);
//loading
void DADSLoadNetworkFromFile(const char * fname);
void DADSSetMetaForNode(int32_t node_id, int32_t nominal_degree, int32_t deactivated);
void DADSPurifyNetwork(); //removing disabled vertices, filling missed values with medians
void DADSAddInfectionCase(int32_t node_id, double t);
//model estimation
void DADSPrepareForEstimation();
void DADSRemarkNodes();
void DADSSetThetaForNode(int32_t node_id, double theta);
double DADSConfirmDropForC(double c, double frac, double drop);
double DADSLogLikelyhoodTKDR(double theta, double kappa, double delta, double rho);
double DADSLogLikelyhoodKDR(double kappa, double delta, double rho);
//derivatives
double* DADSDLogLikelyhoodDtheta(double *thetas, double kappa, double delta, double rho);
void DADSCalculateDerivatives(double theta, double kappa, double delta, double rho);
double DADSDLogLikelyhoodDthetaForId(int32_t id);

#ifdef  __cplusplus
}
#endif

#endif  /* _DADIFFUSIONSIMULATION_H_ */
