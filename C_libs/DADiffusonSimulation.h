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
typedef struct Infect Infection;
typedef struct Derivs Derivatives;

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
    Infection *infections;
    int32_t N_infections;

    NodePtr *nodes_to_check; //array of nodes that have infected neighbors
    int32_t N_nodes_to_check;
    int32_t N_active_nodes;
};

struct ICas {
    NodePtr node;
    double time;
    int32_t index;
    double value1;
    double value2;
};

struct Infect {
    ICase *cases;
    int32_t N_cases;
    int32_t id;
};

int ICaseCompare(const void *, const void *);
int int32Compare(const void *c1, const void *c2);

struct Derivs {
    //gradient
    double dfdtheta;
    double dfddelta;
    double dfdrho;
    double *dfdthetas;
    double *dfdalphas;
    double *dfdrhos;
    //Hessian
    double **df2dthetasdalphas;
    double **df2dthetasdrhos;
    double *df2dthetasddelta;
    double **df2dalphasdrhos;
    double *df2dalphasddelta;
    double *df2drhosddelta;
};


Network und_network;
int32_t echo;
double *dlldthetas;
int32_t n_dlldthetas;
Derivatives ll_derivatives;


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
void DADSSetNumberOfInfections(int32_t N);
void DADSAddInfectionCaseForInfection(int32_t node_id, double t, int32_t infection_number);
void DADSAddInfectionCase(int32_t node_id, double t);
//model estimation
void DADSPrepareForEstimation();
void DADSRemarkNodes();
void DADSSetThetaForAllNodes(double theta);
void DADSSetThetaForNode(int32_t node_id, double theta);
double DADSConfirmDropForC(double c, double frac, double drop);

double DADSLogLikelyhoodTKDR(double theta, double kappa, double delta, double rho, double observe_time);
double DADSLogLikelyhoodByNodeTheta(double node_theta, int32_t node_id, double theta, double confirm, double decay, double relic, double observe_time);
double DADSLogLikelyhoodKDR(double kappa, double delta, double rho, double observe_time);
double DADSLogLikelyhoodTKDRByInfectionsEnsemble(double theta, double kappa, double delta, double rho, double observe_time);
//derivatives
double* DADSDLogLikelyhoodDtheta(double *thetas, double kappa, double delta, double rho, double observe_time);
void DADSCalculateDerivatives(double theta, double kappa, double delta, double rho, double observe_time);
double DADSDLogLikelyhoodDthetaForId(int32_t id);
//double DADSLogLikelyhoodTDRGradient();

#ifdef  __cplusplus
}
#endif

#endif  /* _DADIFFUSIONSIMULATION_H_ */
