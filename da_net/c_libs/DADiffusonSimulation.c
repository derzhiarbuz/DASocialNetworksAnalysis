// Created by Gubanov Alexander (aka Derzhiarbuz) at 06.02.2020
// Contacts: derzhiarbuz@yandex.ru

#include "DADiffusonSimulation.h"

#include <math.h>

NodePtr newNodePtr() {
    NodePtr ptr;
    ptr = (NodePtr)malloc(sizeof(Node));
    ptr->actual_degree = 0;
    ptr->id = 0;
    ptr->neigbors = NULL;
    ptr->payload = NULL;
    ptr->nominal_degree = 0;
    ptr->state = Passive;
    ptr->theta = .0;
    ptr->cases = NULL;
    return ptr;
}


void clearNodePtr(NodePtr ptr) {
    if(ptr->neigbors) free(ptr->neigbors);
    if(ptr->payload) free(ptr->payload);
    if(ptr->cases) free(ptr->cases);
    free(ptr);
}


int NodeCompare(const void *n1, const void *n2) {
    NodePtr node1 = *((NodePtr*)n1);
    NodePtr node2 = *((NodePtr*)n2);
    return node1->id - node2->id;
}


int ICaseCompare(const void *c1, const void *c2) {
    ICase case1 = *((ICase*)c1);
    ICase case2 = *((ICase*)c2);
    if (case1.time > case2.time) return 1;
    if (case1.time == case2.time) return 0;
    return -1;
}


int int32Compare(const void *c1, const void *c2) {
    int32_t case1 = *((int32_t*)c1);
    int32_t case2 = *((int32_t*)c2);
    return case1-case2;
}


int32_t hello_func(int32_t a) {
	printf("This is number %d", a);
	return a * 2;
}


void DADSEchoOn() {
    echo = 33;
}


void DADSEchoOff() {
    echo = 0;
}


void DADSLog(char *text, ...) {
    va_list args;

    va_start(args, text);
    if(echo == 33) vprintf(text, args);
    va_end(args);
}


void DADSInitNetwork() {
    static int inited = 0;
    if(inited == 0 || und_network.nodes == NULL) {
        inited = 1;
        und_network.nodes = NULL;
        und_network.N = 0;
        und_network.cases = NULL;
        und_network.N_cases = 0;
        und_network.nodes_to_check = NULL;
        und_network.N_nodes_to_check = 0;
        und_network.infections = NULL;
        und_network.N_infections = 0;
    }
}


void DADSClearNetwork() {
    DADSInitNetwork(); //make sure that it was initiation

    NodePtr curNode;
    if(und_network.nodes){
        for(int32_t i=0; i<und_network.N; i++) {
            curNode = und_network.nodes[i];
            clearNodePtr(curNode);
        }
        free(und_network.nodes);
    }
    if(und_network.infections) {
        for(int32_t i=0; i<und_network.N_infections; i++) {
            if(und_network.infections[i].cases)
                free(und_network.infections[i].cases);
        }
        free(und_network.infections);
    }
    else
        if(und_network.cases) free(und_network.cases);
    if(und_network.nodes_to_check) free(und_network.nodes_to_check);
    und_network.nodes = NULL;
    und_network.N = 0;
    und_network.cases = NULL;
    und_network.N_cases = 0;
    und_network.nodes_to_check = NULL;
    und_network.N_nodes_to_check = 0;
    und_network.infections = NULL;
    und_network.N_infections = 0;
}


NodePtr DADSNodeForId(int32_t id) {
    static NodePtr tempNode = NULL;
    static NodePtr *retNode;
    if(!tempNode) tempNode = newNodePtr();
    tempNode -> id = id;
    retNode = bsearch(&tempNode, und_network.nodes, und_network.N, sizeof(NodePtr), NodeCompare);
    if(!retNode) return NULL;
    return *retNode;
}

ICase DADSICaseForNodePtr(NodePtr node)  {
    static ICase retCase;

    return retCase;
}


void DADSLoadNetworkFromFile(const char * fpath) {
    FILE * f;
    int32_t i, j;
    int64_t size_in_bytes = 0;

    DADSClearNetwork();

    if(und_network.nodes != NULL) {
        DADSLog("\nUnable to load new network: there is one already loaded. Try to call clear_network()");
    }

    f = fopen(fpath, "rb");
    if(!f) {
        DADSLog("\nError: Unable to open underlying network file %s", fpath);
        return;
    }

    DADSLog("\nReading network from %s", fpath);
    fread((void *)(&und_network.N), 4, 1, f);

    DADSLog("\nNumber of nodes: %d", und_network.N);

    und_network.nodes = malloc(und_network.N * sizeof(NodePtr));
    size_in_bytes += und_network.N * sizeof(NodePtr);

    NodePtr newNode;
    for(i=0; i<und_network.N; i++) {
        newNode = newNodePtr();
        fread((void *)(&newNode->actual_degree), 4, 1, f);
        newNode->nominal_degree = newNode->actual_degree;
        fread((void *)(&newNode->id), 4, 1, f);
        newNode->payload = malloc(newNode->actual_degree * 4);
        fread(newNode->payload, 4, newNode->actual_degree, f);
        und_network.nodes[i] = newNode;
    }

    fclose(f);

    DADSLog("\nNetwork readed. Optimizing...");

    //sorting nodes by id to make dichotomy search
    qsort(und_network.nodes, und_network.N, sizeof(NodePtr), NodeCompare);

    NodePtr curNode;
    NodePtr neigNode;
    NodePtr tempNode = newNodePtr();
    int32_t *neig_ids;

    for(i=0; i<und_network.N; i++) {
        curNode = und_network.nodes[i];
        curNode->neigbors = malloc(curNode->actual_degree * sizeof(NodePtr));
        neig_ids = (int32_t *)curNode->payload;
        for(j=0; j<curNode->actual_degree; j++) {
            neigNode = DADSNodeForId(neig_ids[j]);
            if(!neigNode) {
                DADSLog("\nWarning: Unable to find a node %d", tempNode->id);
                break;
            }
            curNode->neigbors[j] = neigNode;
            //printf("%d : %d     ", neig_ids[j], curNode->neigbors[j]->id);
        }
        free(curNode->payload);
        curNode->payload = NULL;
        size_in_bytes += curNode->actual_degree * sizeof(NodePtr) + sizeof(Node);
    }

    clearNodePtr(tempNode);
    DADSLog("\nNetwork optimized. Size in bytes: %d", size_in_bytes);
}


void DADSSetMetaForNode(int32_t node_id, int32_t nominal_degree, int32_t deactivated) {
    NodePtr node = DADSNodeForId(node_id);
    if(!node) {
        DADSLog("\nWarning: Node %d not found", node_id);
        return;
    }
    node->nominal_degree = nominal_degree;
    if(deactivated)
        node->payload = (void*)deactivated;
    else
        node->payload = NULL;
}


void DADSPurifyNetwork() {
    //removing deactivated vertices
    int32_t i, j, k;
    NodePtr cur_node, neig_node, *temp;
    int64_t size_in_bytes = 0;

    //removing deactivated nodes links from neighbors
    DADSLog("\nRemoving deactivated nodes...");
    for(i=0; i<und_network.N; i++) {
        cur_node = und_network.nodes[i];
        if(cur_node->payload > 0) { //node is deactivated
            for(j=0; j<cur_node->actual_degree; j++) {
                neig_node = cur_node->neigbors[j];
                for(k=0; k<neig_node->actual_degree; k++) {
                    if(neig_node->neigbors[k]->id == cur_node->id) {
                        neig_node->neigbors[k] = neig_node->neigbors[neig_node->actual_degree-1];
                        neig_node->actual_degree--;
                        break;
                    }
                }
            }
        }
    }

    //removing deactivated nodes from network and reallocate arrays for other nodes
    i = 0;
    while(i<und_network.N) {
        cur_node = und_network.nodes[i];
        if(cur_node->payload > 0) {
            cur_node->payload = NULL;
            clearNodePtr(cur_node);
            und_network.nodes[i] = und_network.nodes[und_network.N-1];
            und_network.N--;
        }
        else {
            temp = cur_node->neigbors;
            if(cur_node->actual_degree <= 0) cur_node->neigbors = NULL;
            else {
                cur_node->neigbors = malloc(cur_node->actual_degree * sizeof(NodePtr));
                for(j=0; j<cur_node->actual_degree; j++)
                    cur_node->neigbors[j] = temp[j];
            }
            free(temp);
            i++;
            size_in_bytes += cur_node->actual_degree * sizeof(NodePtr);
        }
    }

    if(und_network.N <= 0) {
        DADSClearNetwork();
        return;
    }
    qsort(und_network.nodes, und_network.N, sizeof(NodePtr), NodeCompare); //rearranging nodes in network

    temp = und_network.nodes;
    und_network.nodes = malloc(und_network.N * sizeof(NodePtr));
    for(i=0; i<und_network.N; i++)
        und_network.nodes[i] = temp[i];
    free(temp);
    size_in_bytes += und_network.N * sizeof(Node) + und_network.N * sizeof(NodePtr);

    DADSLog("\nDeactivated nodes removed. Size in bytes: %d.", size_in_bytes);
    DADSLog(" Number of nodes: %d", und_network.N);

    //filling zero nominal degrees as medians
    int32_t *degrees = malloc(und_network.N * sizeof(int32_t));
    int32_t n_active = 0, median = 0, n_setted = 0;

    for(i=0; i<und_network.N; i++) {
        cur_node = und_network.nodes[i];
        if(cur_node->nominal_degree > 0) {
            degrees[n_active] = cur_node->nominal_degree;
            n_active++;
        }
    }
    qsort(degrees, n_active, sizeof(int32_t), int32Compare);
    if(n_active%2 == 0) {
        if(n_active)
            median = (degrees[n_active/2-1] + degrees[n_active/2])/2;
    }
    else
        median = degrees[n_active/2];
    DADSLog("\nMedian nominal degree: %d", median);

    for(i=0; i<und_network.N; i++) {
        cur_node = und_network.nodes[i];
        if(cur_node->nominal_degree <= 0) {
            cur_node->nominal_degree = median;
            n_setted++;
        }
    }
    DADSLog("\nMedian nominal degree setted for %d nodes.", n_setted);

    free(degrees);
}


void DADSSetNumberOfInfections(int32_t n) {
    if(und_network.infections) {
        for(int32_t i=0; i<und_network.N_infections; i++) {
            if(und_network.infections[i].cases)
                free(und_network.infections[i].cases);
            if(und_network.infections[i].nodes_to_check)
                free(und_network.infections[i].nodes_to_check);
        }
        free(und_network.infections);
    }
    und_network.infections = malloc(n * sizeof(Infection));
    und_network.N_infections = n;
    for(int32_t i=0; i<und_network.N_infections; i++) {
        und_network.infections[i].cases = NULL;
        und_network.infections[i].N_cases = 0;
        und_network.infections[i].id = 0;
        und_network.infections[i].nodes_to_check = NULL;
        und_network.infections[i].N_nodes_to_check = 0;
    }
}


void DADSAddInfectionCaseForInfection(int32_t node_id, double t, int32_t infection_number) {
    if(infection_number >= und_network.N_infections) return;
    //DADSLog("\nInfection number: %d", infection_number);
    //DADSLog("  case id: %d", node_id);
    //DADSLog("  time: %f", t);
    und_network.cases = und_network.infections[infection_number].cases;
    und_network.N_cases = und_network.infections[infection_number].N_cases;
    DADSAddInfectionCaseCurrent(node_id, t);
    und_network.infections[infection_number].cases = und_network.cases;
    und_network.infections[infection_number].N_cases = und_network.N_cases;
}


void DADSAddInfectionCase(int32_t node_id, double t) {
    if(!und_network.infections)
        DADSSetNumberOfInfections(1);
    DADSAddInfectionCaseForInfection(node_id, t, 0);
}


void DADSAddInfectionCaseCurrent(int32_t node_id, double t) {
    NodePtr node = DADSNodeForId(node_id);
    ICase *temp;
    int32_t i;

    if(!node) {
        DADSLog("\nWarning: Tried to add infection case, but node %d not found.", node_id);
        return;
    }

    temp = und_network.cases;
    und_network.N_cases++;
    und_network.cases = malloc(und_network.N_cases * sizeof(ICase));
    if(und_network.N_cases>1) {
        for(i=0; i<und_network.N_cases-1; i++) {
            und_network.cases[i] = temp[i];
        }
    }
    und_network.cases[und_network.N_cases-1].node = node;
    und_network.cases[und_network.N_cases-1].time = t;
    und_network.cases[und_network.N_cases-1].index = und_network.N_cases-1;
    und_network.cases[und_network.N_cases-1].value1 = 0.;
    und_network.cases[und_network.N_cases-1].value2 = 0.;

    if(temp) free(temp);
}


void DADSPrepareForEstimation() { //making some stuff to simplify estimation process
    int32_t i, j, ii;
    NodePtr node;
    NodeState st;

    DADSLog("\nPreparing for estimation.");
    if(!und_network.N) {
        DADSLog("\nWarning: The network is empty.");
        return;
    }
    if(!und_network.N_cases) {
        DADSLog("\nWarning: There is no infected.");
        return;
    }

    for(ii=0; ii<und_network.N_infections; ii++) {
        qsort(und_network.infections[ii].cases, und_network.infections[ii].N_cases, sizeof(ICase), ICaseCompare);
        for(i=0; i<und_network.infections[ii].N_cases; i++)
            und_network.infections[ii].cases[i].index = i;
    }

/*    for(i=0; i<und_network.N_cases; i++) {
        DADSLog("\n%d : ", und_network.cases[i].node->id);
        DADSLog("%f", und_network.cases[i].time);
    }*/
    if(und_network.nodes_to_check) free(und_network.nodes_to_check);
    und_network.nodes_to_check = NULL;
    und_network.N_nodes_to_check = 0;

    DADSLog("\nDefining nodes that are in contact with infected.");
    for(ii=0; ii<und_network.N_infections; ii++) {
        for(i=0; i<und_network.infections[ii].N_cases; i++) {
            node = und_network.infections[ii].cases[i].node;
            //node->payload = &und_network.infections[ii].cases[i];
            if(node->state == Passive) und_network.N_nodes_to_check++;
            node->state = NS;
            for(j=0; j<node->actual_degree; j++) {
                if(node->neigbors[j]->state == Passive) und_network.N_nodes_to_check++;
                node->neigbors[j]->state = NS;
            }
        }
    }

    if(!und_network.N_nodes_to_check) {
        DADSLog("\nWarning: No nodes in contact with infected.");
        return;
    }

    und_network.nodes_to_check = malloc(und_network.N_nodes_to_check * sizeof(NodePtr));
    j = 0;
    for(i=0; i<und_network.N; i++) {
        if(und_network.nodes[i]->state != Passive) {
            und_network.nodes_to_check[j] = und_network.nodes[i];
            j++;
        }
    }
    DADSLog("\nPrepared. Nodes to check: %d", und_network.N_nodes_to_check);

 /*   for(i=0; i<und_network.N; i++) {
        DADSLog("\n%d : ", und_network.nodes[i]->id);
        for(j=0; j<und_network.nodes[i]->actual_degree; j++) {
            DADSLog(" %d ", und_network.nodes[i]->neigbors[j]->id);
        }
    }*/
}


//making nodes_to_check array for infection
void DADSUpdate_infection(int32_t infection_number) {
    int32_t i, j;
    NodePtr node;
    NodeState st;
    Infect* infection;

    infection = &und_network.infections[infection_number];

    DADSLog("\nPreparing for estimation.");
    if(!und_network.N) {
        DADSLog("\nWarning: The network is empty.");
        return;
    }
    if(!infection->N_cases) {
        DADSLog("\nWarning: There is no infected for infection #%d", infection_number);
        return;
    }

    //sorting infection cases by time
    qsort(infection->cases, infection->N_cases, sizeof(ICase), ICaseCompare);
    for(i=0; i<infection->N_cases; i++)
        infection->cases[i].index = i;


    if(infection->nodes_to_check) free(infection->nodes_to_check);
    infection->nodes_to_check = NULL;
    infection->N_nodes_to_check = 0;

    DADSLog("\nDefining nodes that are in contact with infected.");
    for(i=0; i<infection->N_cases; i++) {
        node = infection->cases[i].node;
        if(node->state != infection_number) infection->N_nodes_to_check++;
        node->state = infection_number;
        for(j=0; j<node->actual_degree; j++) {
            if(node->neigbors[j]->state != infection_number) infection->N_nodes_to_check++;
            node->neigbors[j]->state = infection_number;
        }
    }

    if(!infection->N_nodes_to_check) {
        DADSLog("\nWarning: No nodes in contact with infected for infection #%d", infection_number);
        return;
    }

    infection->nodes_to_check = malloc(infection->N_nodes_to_check * sizeof(NodePtr));
    j = 0;
    for(i=0; i<und_network.N; i++) {
        if(und_network.nodes[i]->state == infection_number) {
            infection->nodes_to_check[j] = und_network.nodes[i];
            j++;
        }
    }
    DADSLog("\nPrepared for infection #%d. ", infection_number)
    DADSLog(" Nodes to check: %d", und_network.N_nodes_to_check);
}


//searching for all nodes should be checeked and making cases arrays for them
void DADSConnectNodesToCases() {
    int32_t i, j;
    NodePtr curNode;
    Infect* infection;

    #pragma omp parallel for shared(und_network) private(i, j, curNode) schedule(guided)
    for(i=0; i<und_network.N; i++) {
        curNode = und_network.nodes[i];
        if(curNode->cases == -1) {
            curNode->cases = malloc(und_network.N_infections * sizeof(ICase*));
            for(j=0; j<und_network.N_infections; j++) {
                curNode->cases[j] = NULL;
            }
        }
        else {
            if(curNode->cases) free(curNode->cases);
                curNode->cases = NULL;
        }
    }

    #pragma omp parallel for shared(und_network) private(i, j, infection, curNode) schedule(guided)
    for(i=0; i<und_network.N_infections; i++) {
        infection = &und_network.infections[infection_number];
        for(j=0; j<infection->N_cases; j++) {
            infection->cases[j].node->cases[i] = &infection->cases[j];
        }
    }
}


//making some stuff to simplify estimation process more suitable for parallel calculations
void DADSPrepareForEstimation_new() {
    int32_t i;

    for(i=0; i<und_network.N; i++)
        und_network.nodes[i]->state = -1;

    //this cannot be parralelled
    for(i=0; i<und_network.N_infections; i++)
        DADSUpdate_infection(i)

    //now searching for all nodes should be checeked and making cases arrays for them
    DADSConnectNodesToCases();
}


void DADSRemarkNodes() {
    int32_t i, j;
    NodePtr node;
    NodeState st;

    und_network.N_active_nodes = 0; //counting nodes that are not passive for current case

    for(i=0; i<und_network.N_nodes_to_check; i++) {
        und_network.nodes_to_check[i]->state = Passive;
    }

    for(i=0; i<und_network.N_cases; i++) {
        node = und_network.cases[i].node;
        node->payload = &und_network.cases[i];
        //DADSLog("\nCase id: %d", und_network.cases[i].node->id);
        //DADSLog("\nCase time: %f", und_network.cases[i].time);
        if(und_network.cases[i].time == 0) {
            st = S;
            node->state = I;
            und_network.N_active_nodes++;
            //DADSLog("\nInfected Id: %d", node->id);
        }
        else {
            st = NS;
            if(node->state == Passive) {
                node->state = NS;
                und_network.N_active_nodes++;
            }
        }
        for(j=0; j<node->actual_degree; j++) {
            if(node->neigbors[j]->state < st) {
                if(node->neigbors[j]->state == Passive) und_network.N_active_nodes++;
                node->neigbors[j]->state = st;
            }
        }
    }
}


void DADSSetThetaForAllNodes(double theta) {
    for(int32_t i=0; i<und_network.N_cases; i++) {
        und_network.cases[i].node->theta = theta;
    }
}


void DADSSetThetaForNode(int32_t node_id, double theta) {
    NodePtr node;
    node = DADSNodeForId(node_id);
    if(node) node->theta = theta;
}


int DADSHasConfirmDrop(double c, double frac) {
    if(c>=.0) {
        if(frac < c) return 1;
        return 0;
    }
    if(frac > 1. + c) return 1;
    return 0;
}


double DADSLogLikelyhoodTKDR(double theta, double confirm, double decay, double relic, double observe_time) {
    DADSSetThetaForAllNodes(theta);
    return DADSLogLikelyhoodKDR(confirm, decay, relic, observe_time);
}


double DADSLogLikelyhoodByNodeTheta(double node_theta, int32_t node_id, double theta, double confirm, double decay, double relic, double observe_time) {
    DADSSetThetaForAllNodes(theta);
    DADSSetThetaForNode(node_id, node_theta);
    return DADSLogLikelyhoodKDR(confirm, decay, relic, observe_time);
}


double DADSLogLikelyhoodKDR(double confirm, double decay, double relic, double observe_time) {
    int32_t i, j, k, n_i;
    double t = .0, dt, new_time, loglikelyhood, inf_rate, cd, relic1, relic2;
    double confirm_drop = 0.1;
    ICase cur_case, *neigh_case;
    NodePtr neighbor, cur_node;
    int observation_tail = 0;

    DADSRemarkNodes(); //dropping all I, S and NS states to initial (t=0)
    //DADSLog("\nOT: %f", observe_time);

    if(observe_time<1) {
        //if no observation time, set it to the last case time
        observe_time = und_network.cases[und_network.N_cases-1].time;
    }

    /*for(i=0; i<und_network.N; i++) {
        DADSLog("\n%d : ", und_network.nodes[i]->id);
        DADSLog(" %d", und_network.nodes[i]->state);
    }*/

    loglikelyhood = .0;
    for(i=0; i<und_network.N_cases; i++) {
        if(und_network.cases[i].time > 0.) break;
    }

    for(;i<und_network.N_cases + 1; i++) { //the last step is for observation finish time
        if(i < und_network.N_cases) //if it's a case, not the end of observation
            new_time = und_network.cases[i].time;
        else
            new_time = observe_time;
        relic1 = .0;
        relic2 = .0;
        for(j=0; j<i; j++) {
            if(decay > .0) {
                und_network.cases[j].value1 = 1./decay*(exp(decay*(und_network.cases[j].time - t)) - exp(decay*(und_network.cases[j].time - new_time)));
                //und_network.cases[j].value1 = 1./(1.-decay)*(pow((new_time - und_network.cases[j].time), 1.-decay) - pow((t - und_network.cases[j].time), 1. - decay));
                relic1 += relic*(und_network.cases[j].value1);
                und_network.cases[j].value1 *= und_network.cases[j].node->theta;
                und_network.cases[j].value2 = 1.*exp(decay*(und_network.cases[j].time - new_time));
                //und_network.cases[j].value2 = 1.*pow((new_time - und_network.cases[j].time), -decay);
                relic2 += relic*(und_network.cases[j].value2);
                und_network.cases[j].value2 *= und_network.cases[j].node->theta;
            }
            else {
                und_network.cases[j].value1 = und_network.cases[j].node->theta*(new_time - t);
                relic1 += relic*(new_time - t);
                und_network.cases[j].value2 = und_network.cases[j].node->theta;
                relic2 += relic*1;
            }
        }
        dt = new_time - t;
        t = new_time;
        //DADSLog("\n%f ", t);
        //the member of ll function defined by non-infection during current time interval
        double prevll = 0;
        int nrel = 0;
        for(j=0; j<und_network.N_nodes_to_check; j++) {
            cur_node = und_network.nodes_to_check[j];
            if(cur_node->state == S) { //if node is susceptible
                n_i = 0;
                inf_rate = .0;
                for(k=0; k<cur_node->actual_degree; k++) {
                    neighbor = cur_node->neigbors[k];
                    if(neighbor->state == I) { //neighbor is infected
                        n_i++;
                        neigh_case = (ICase *)neighbor->payload; //case for this neighbor
                        inf_rate += neigh_case->value1;
                    }
                }
                if(DADSHasConfirmDrop(confirm, (double)n_i/cur_node->nominal_degree))
                    cd = confirm_drop;
                else
                    cd = 1.;
                //loglikelyhood -= cd*(inf_rate + relic*dt);
                //loglikelyhood -= (inf_rate + relic*dt);
                //loglikelyhood -= (inf_rate + relic);
                //loglikelyhood -= (inf_rate + relic*i);
                loglikelyhood -= (inf_rate + relic1);
                //nrel++;
                //prevll -= (inf_rate + relic1);
                //DADSLog(" %d ", cur_node->id);
                //DADSLog(" %f ", relic1);
            }
            else if(cur_node->state == NS) {
                //loglikelyhood -= confirm_drop*relic*dt;
                //loglikelyhood -= relic*dt;
                //loglikelyhood -= relic;
                //loglikelyhood -= relic*i;
                loglikelyhood -= relic1;
                //nrel++;
                //prevll -= relic1;
            }
        }
        //loglikelyhood -= confirm_drop*relic*dt*(und_network.N - und_network.N_nodes_to_check);
        //loglikelyhood -= relic*dt*(und_network.N - und_network.N_nodes_to_check);
        //loglikelyhood -= relic*(und_network.N - und_network.N_nodes_to_check);
        //loglikelyhood -= relic*i*(und_network.N - und_network.N_nodes_to_check);
        loglikelyhood -= relic1*(und_network.N - und_network.N_active_nodes);
        //nrel+=und_network.N - und_network.N_active_nodes;
        //prevll -= relic1*(und_network.N - und_network.N_active_nodes);
        //DADSLog(" %f ", loglikelyhood);
        if(i < und_network.N_cases) { //if it's a case, not the end of observation
            cur_case = und_network.cases[i];
            cur_node = cur_case.node;
            n_i = 0;
            inf_rate = .0;
            //the member of ll function defined by infection at the end of current time interval
            for(k=0; k<cur_node->actual_degree; k++) {
                neighbor = cur_node->neigbors[k];
                if(neighbor->state == I) { //neighbor is infected
                    n_i++;
                    neigh_case = (ICase *)neighbor->payload; //case for this neighbor
                    inf_rate += neigh_case->value2;
                }
                else if(neighbor->state == NS) //if neighbor was not susceptible, now it is
                    neighbor->state = S;
            }
            if(DADSHasConfirmDrop(confirm, (double)n_i/cur_node->nominal_degree))
                cd = confirm_drop;
            else
                cd = 1.;
            //loglikelyhood += log(cd*inf_rate + relic);
            //loglikelyhood += log(inf_rate + relic);
            //loglikelyhood += log(inf_rate + relic/dt);
            //loglikelyhood += log(inf_rate + relic*i);
            loglikelyhood += log(inf_rate + relic2);

            //int kk = 0;
            //for(int pp=0; pp<und_network.N; pp++) {
            //    if(und_network.nodes[pp]->state == I) kk++;
            //}
            //DADSLog("\nCNInfTot %d", kk);
            cur_node->state = I; //the node is infected now
            //DADSLog("\n%d ", cur_node->id);
            //DADSLog(" %f ", t);
            //DADSLog(" %f ", prevll);
            //DADSLog(" %f ", log(inf_rate + relic2));
            //DADSLog(" %f ", loglikelyhood);
            //DADSLog(" nr%d ", nrel);
        }
        else {
            //DADSLog("\ntail %f ", t);
            //DADSLog(" %f ", prevll);
            //DADSLog(" nr%d ", nrel);
            //DADSLog(" r%f ", relic1);
        }
    }
/*    DADSLog("\ntheta: %f", theta);
    DADSLog("\nconfirm: %f", confirm);
    DADSLog("\ndecay: %f", decay);
    DADSLog("\nrelic: %f", relic);
    DADSLog("\nLL: %f", loglikelyhood);*/
    //DADSLog("\n%f", t);
    return loglikelyhood;
}


double DADSLogLikelyhoodKDR_par(double confirm, double decay, double relic, double observe_time, int32_t infection_number) {
    int32_t i;
    double loglikelyhood;
    double confirm_drop = 0.1;
    Infect* infection;

    infection = &und_network.infections[infection_number];

    if(observe_time<1) {
        //if no observation time, set it to the last case time
        observe_time = infection->cases[und_network.N_cases-1].time;
    }

    loglikelyhood = .0;
    for(i=0; i<infection->N_cases; i++) {
        if(infection->cases[i].time > 0.) break;
    }

    #pragma omp parallel \
        shared(und_network, observe_time, confirm, decay, relic, observe_time, infection, confirm_drop) \
        firstprivate(i) \
        reduction(+:loglikelyhood)
    {
        int32_t j, k, n_i;
        double t = .0, dt, new_time, inf_rate, cd, relic1, relic2;
        ICase cur_case, *neigh_case;
        NodePtr neighbor, cur_node;
        double value1[infection->N_cases];
        double value2[infection->N_cases];

        #pragma omp for schedule(guided)
        for(;i<infection->N_cases + 1; i++) { //the last step is for observation finish time

            //paralleled block
            if(i < infection->N_cases) //if it's a case, not the end of observation
                new_time = infection->cases[i].time;
            else
                new_time = observe_time;
            if(i > 0) //if it's a case, not the end of observation
                t = infection->cases[i-1].time;
            else
                t = 0;
            dt = new_time - t;
            relic1 = .0;
            relic2 = .0;

            for(j=0; j<i; j++) {
                if(decay > .0) {
                    value1[j] = 1./decay*(exp(decay*(infection->cases[j].time - t)) - exp(decay*(infection->cases[j].time - new_time)));
                    //value1[j] = 1./(1.-decay)*(pow((new_time - infection->cases[j].time), 1.-decay) - pow((t - infection->cases[j].time), 1. - decay));
                    relic1 += relic*(value1[j]);
                    value1[j] *= infection->cases[j].node->theta;
                    value2[j] = 1.*exp(decay*(infection->cases[j].time - new_time));
                    //value2[j] = 1.*pow((new_time - infection->cases[j].time), -decay);
                    relic2 += relic*(value2[j]);
                    value2[j] *= infection->cases[j].node->theta;
                }
                else {
                    value1[j] = infection->cases[j].node->theta*(new_time - t);
                    relic1 += relic*(new_time - t);
                    value2[j] = infection->cases[j].node->theta;
                    relic2 += relic*1;
                }
            }
            //DADSLog("\n%f ", t);
            //the member of ll function defined by non-infection during current time interval
            double prevll = 0;
            int nrel = 0;
            for(j=0; j<infection->N_nodes_to_check; j++) {
                cur_node = infection->nodes_to_check[j];
                if(cur_node->state == S) { //if node is susceptible
                    n_i = 0;
                    inf_rate = .0;
                    for(k=0; k<cur_node->actual_degree; k++) {
                        neighbor = cur_node->neigbors[k];
                        if(neighbor->state == I) { //neighbor is infected
                            n_i++;
                            neigh_case = (ICase *)neighbor->payload; //case for this neighbor
                            inf_rate += neigh_case->value1;
                        }
                    }
                    if(DADSHasConfirmDrop(confirm, (double)n_i/cur_node->nominal_degree))
                        cd = confirm_drop;
                    else
                        cd = 1.;
                    loglikelyhood -= (inf_rate + relic1);
                }
                else if(cur_node->state == NS) {
                    loglikelyhood -= relic1;
                }
            }
            loglikelyhood -= relic1*(und_network.N - infection->N_nodes_to_check);

            if(i < infection->N_cases) { //if it's a case, not the end of observation
                cur_case = infection->cases[i];
                cur_node = cur_case.node;
                n_i = 0;
                inf_rate = .0;
                //the member of ll function defined by infection at the end of current time interval
                for(k=0; k<cur_node->actual_degree; k++) {
                    neighbor = cur_node->neigbors[k];
                    if(neighbor->state == I) { //neighbor is infected
                        n_i++;
                        neigh_case = (ICase *)neighbor->payload; //case for this neighbor
                        inf_rate += neigh_case->value2;
                    }
                    else if(neighbor->state == NS) //if neighbor was not susceptible, now it is
                        neighbor->state = S;
                }
                if(DADSHasConfirmDrop(confirm, (double)n_i/cur_node->nominal_degree))
                    cd = confirm_drop;
                else
                    cd = 1.;
                loglikelyhood += log(inf_rate + relic2);
                cur_node->state = I;
            }
            else {
            }
        }
    }
    //end of parallel block. Result is reducted to likelyhood
    return loglikelyhood;
}


double DADSLogLikelyhoodTKDRByInfectionsEnsemble(double theta, double kappa, double delta, double rho, double observe_time) {
    double loglikelyhood = .0;
    double newll = .0;
    //DADSLog("\nEnsemble!");
    for(int32_t i=0; i<und_network.N_infections; i++) {
        und_network.cases = und_network.infections[i].cases;
        und_network.N_cases = und_network.infections[i].N_cases;
        newll = DADSLogLikelyhoodTKDR(theta, kappa, delta, rho, observe_time);
        loglikelyhood += newll;
        //DADSLog("\n%f", newll);
        //DADSLog("\n");
    }
    return loglikelyhood;
}


//derivatives
double* DADSDLogLikelyhoodDtheta(double *thetas, double confirm, double decay, double relic, double observe_time) {
    int32_t i, j, k, n_i;
    double t = .0, dt, *dfdthetas, inf_rate, cd, L, new_time;
    double confirm_drop = 0.1;
    ICase cur_case, *neigh_case;
    NodePtr neighbor, cur_node;

    DADSRemarkNodes(); //dropping all I, S and NS states to initial (t=0)

    if(observe_time<1) {
        //if no observation time, set it to the last case time
        observe_time = und_network.cases[und_network.N_cases-1].time;
    }

    dfdthetas = malloc(und_network.N_cases * sizeof(double)); //partial derivatives array
    for(i=0; i<und_network.N_cases; i++) dfdthetas[i] = .0;

/*    for(i=0; i<und_network.N; i++) {
        DADSLog("\n%d : ", und_network.nodes[i]->id);
        DADSLog(" %d", und_network.nodes[i]->state);
    }*/

    for(i=0; i<und_network.N_cases; i++) {
        if(und_network.cases[i].time > 0.) break;
    }

    for(;i<und_network.N_cases + 1; i++) { //the last step is for observation finish time
        if(i < und_network.N_cases) //if it's a case, not the end of observation
            new_time = und_network.cases[i].time;
        else
            new_time = observe_time;

        for(j=0; j<=i; j++) {
            if(decay > .0) {
                und_network.cases[j].value1 = 1./decay*(exp(decay*(und_network.cases[j].time - t)) - exp(decay*(und_network.cases[j].time - new_time)));
                und_network.cases[j].value2 = 1.*exp(decay*(und_network.cases[j].time - new_time));
            }
            else {
                und_network.cases[j].value1 = 1.*(new_time - t);
                und_network.cases[j].value2 = 1.;
            }
        }
        dt = new_time - t;
        t = new_time;

        //the member of ll function defined by non-infection during current time interval
        for(j=0; j<und_network.N_nodes_to_check; j++) {
            cur_node = und_network.nodes_to_check[j];
            if(cur_node->state == S) { //if node is susceptible
                n_i = 0;
                inf_rate = .0;
                for(k=0; k<cur_node->actual_degree; k++) {
                    neighbor = cur_node->neigbors[k];
                    if(neighbor->state == I) { //neighbor is infected
                        n_i++;
                        neigh_case = (ICase *)neighbor->payload; //case for this neighbor
                        dfdthetas[neigh_case->index] -= neigh_case->value1;
                    }
                }
            }
        }

        if(i < und_network.N_cases) { //if it's a case, not the end of observation
            cur_case = und_network.cases[i];
            cur_node = cur_case.node;
            n_i = 0;
            inf_rate = .0;
            L = .0;
            //making common L function denominator
            for(j=0; j<=i; j++) {
                L += relic*und_network.cases[j].value2; //exponential decaying relic
            }
            for(k=0; k<cur_node->actual_degree; k++) {
                neighbor = cur_node->neigbors[k];
                if(neighbor->state == I) { //neighbor is infected
                    neigh_case = (ICase *)neighbor->payload; //case for this neighbor
                    L += thetas[neigh_case->index] * neigh_case->value2;
                }
            }
            //the member of ll function defined by infection at the end of current time interval
            for(k=0; k<cur_node->actual_degree; k++) {
                neighbor = cur_node->neigbors[k];
                if(neighbor->state == I) { //neighbor is infected
                    n_i++;
                    neigh_case = (ICase *)neighbor->payload; //case for this neighbor
                    dfdthetas[neigh_case->index] += neigh_case->value2/L;
                }
                else if(neighbor->state == NS) //if neighbor was not susceptible, now it is
                    neighbor->state = S;
            }
            cur_node->state = I; //the node is infected now
        }
        //DADSLog("\n%f ", t);
        //DADSLog(" %f ", loglikelyhood);
    }
/*    DADSLog("\ntheta: %f", theta);
    DADSLog("\nconfirm: %f", confirm);
    DADSLog("\ndecay: %f", decay);
    DADSLog("\nrelic: %f", relic);
    DADSLog("\nLL: %f", loglikelyhood);*/
    return dfdthetas;
}

void DADSCalculateDerivatives(double theta, double confirm, double decay, double relic, double observe_time) {
    static int first_time = 1;
    double *thetas;

    if(first_time) {
        dlldthetas = NULL;
        n_dlldthetas = 0;
        first_time = 0;
    }

    if(dlldthetas) {
        free(dlldthetas);
        n_dlldthetas = 0;
    }
    if(!und_network.N_cases) return;
    thetas = malloc(und_network.N_cases * sizeof(double));
    n_dlldthetas = und_network.N_cases;
    for(int i=0; i<und_network.N_cases; i++) {
        thetas[i] = theta;
    }
    dlldthetas = DADSDLogLikelyhoodDtheta(thetas, confirm, decay, relic, observe_time);

    free(thetas);
}

double DADSDLogLikelyhoodDthetaForId(int32_t id) {
    if(!n_dlldthetas || n_dlldthetas != und_network.N_cases) return .0;
    for(int i=0; i<n_dlldthetas; i++) {
        if(und_network.cases[i].node->id == id) {
                return dlldthetas[i];
        }
    }
    return .0;
}

//gradient for four params
/*double DADSLogLikelyhoodTDRGradient() {
    ll_derivatives.dfdtheta = .0;
    ll_derivatives.dfddelta = .0;
    ll_derivatives.dfdrho = .0;

    int32_t i, j, k, n_i;
    double t = .0, dt, *dfdthetas, inf_rate, cd, L;
    double confirm_drop = 0.1;
    ICase cur_case, *neigh_case;
    NodePtr neighbor, cur_node;

    DADSRemarkNodes(); //dropping all I, S and NS states to initial (t=0)

    dfdthetas = malloc(und_network.N_cases * sizeof(double)); //partial derivatives array
    for(i=0; i<und_network.N_cases; i++) dfdthetas[i] = .0;*/

/*    for(i=0; i<und_network.N; i++) {
        DADSLog("\n%d : ", und_network.nodes[i]->id);
        DADSLog(" %d", und_network.nodes[i]->state);
    }*/

 /*   for(i=0; i<und_network.N_cases; i++) {
        if(und_network.cases[i].time > 0.) break;
    }

    for(;i<und_network.N_cases; i++) {
        cur_case = und_network.cases[i];
        for(j=0; j<=i; j++) {
            if(decay > .0) {
                und_network.cases[j].value1 = 1./decay*(exp(decay*(und_network.cases[j].time - t)) - exp(decay*(und_network.cases[j].time - cur_case.time)));
                und_network.cases[j].value2 = 1.*exp(decay*(und_network.cases[j].time - cur_case.time));
            }
            else {
                und_network.cases[j].value1 = 1.*(cur_case.time - t);
                und_network.cases[j].value2 = 1.;
            }
        }
        dt = cur_case.time - t;
        t = cur_case.time;

        //the member of ll function defined by non-infection during current time interval
        for(j=0; j<und_network.N_nodes_to_check; j++) {
            cur_node = und_network.nodes_to_check[j];
            if(cur_node->state == S) { //if node is susceptible
                n_i = 0;
                inf_rate = .0;
                for(k=0; k<cur_node->actual_degree; k++) {
                    neighbor = cur_node->neigbors[k];
                    if(neighbor->state == I) { //neighbor is infected
                        n_i++;
                        neigh_case = (ICase *)neighbor->payload; //case for this neighbor
                        dfdthetas[neigh_case->index] -= neigh_case->value1;
                    }
                }
            }
        }

        cur_node = cur_case.node;
        n_i = 0;
        inf_rate = .0;
        L = .0;
        //making common L function denominator
        for(j=0; j<=i; j++) {
            L += relic*und_network.cases[j].value2; //exponential decaying relic
        }
        for(k=0; k<cur_node->actual_degree; k++) {
            neighbor = cur_node->neigbors[k];
            if(neighbor->state == I) { //neighbor is infected
                neigh_case = (ICase *)neighbor->payload; //case for this neighbor
                L += thetas[neigh_case->index] * neigh_case->value2;
            }
        }
        //the member of ll function defined by infection at the end of current time interval
        for(k=0; k<cur_node->actual_degree; k++) {
            neighbor = cur_node->neigbors[k];
            if(neighbor->state == I) { //neighbor is infected
                n_i++;
                neigh_case = (ICase *)neighbor->payload; //case for this neighbor
                dfdthetas[neigh_case->index] += neigh_case->value2/L;
            }
            else if(neighbor->state == NS) //if neighbor was not susceptible, now it is
                neighbor->state = S;
        }
        cur_node->state = I; //the node is infected now
        //DADSLog("\n%f ", t);
        //DADSLog(" %f ", loglikelyhood);
    } */
/*    DADSLog("\ntheta: %f", theta);
    DADSLog("\nconfirm: %f", confirm);
    DADSLog("\ndecay: %f", decay);
    DADSLog("\nrelic: %f", relic);
    DADSLog("\nLL: %f", loglikelyhood);*/
   /* return dfdthetas;
}*/
