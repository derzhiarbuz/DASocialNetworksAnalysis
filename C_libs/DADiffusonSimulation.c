// Created by Gubanov Alexander (aka Derzhiarbuz) at 06.02.2020
// Contacts: derzhiarbuz@gmail.com

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
    return ptr;
}


void clearNodePtr(NodePtr ptr) {
    if(ptr->neigbors) free(ptr->neigbors);
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
    if(und_network.cases) free(und_network.cases);
    if(und_network.nodes_to_check) free(und_network.nodes_to_check);
    und_network.nodes = NULL;
    und_network.N = 0;
    und_network.cases = NULL;
    und_network.N_cases = 0;
    und_network.nodes_to_check = NULL;
    und_network.N_nodes_to_check = 0;
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


void DADSAddInfectionCase(int32_t node_id, double t) {
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
    int32_t i, j;
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

    qsort(und_network.cases, und_network.N_cases, sizeof(ICase), ICaseCompare);
    for(i=0; i<und_network.N_cases; i++)
        und_network.cases[i].index = i;
/*    for(i=0; i<und_network.N_cases; i++) {
        DADSLog("\n%d : ", und_network.cases[i].node->id);
        DADSLog("%f", und_network.cases[i].time);
    }*/
    if(und_network.nodes_to_check) free(und_network.nodes_to_check);
    und_network.nodes_to_check = NULL;
    und_network.N_nodes_to_check = 0;

    DADSLog("\nDefining nodes that are in contact with infected.");
    for(i=0; i<und_network.N_cases; i++) {
        node = und_network.cases[i].node;
        node->payload = &und_network.cases[i];
        if(node->state == Passive) und_network.N_nodes_to_check++;
        node->state = NS;
        for(j=0; j<node->actual_degree; j++) {
            if(node->neigbors[j]->state == Passive) und_network.N_nodes_to_check++;
            node->neigbors[j]->state = NS;
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


void DADSRemarkNodes() {
    int32_t i, j;
    NodePtr node;
    NodeState st;

    for(i=0; i<und_network.N_nodes_to_check; i++) {
        und_network.nodes_to_check[i]->state = Passive;
    }

    for(i=0; i<und_network.N_cases; i++) {
        node = und_network.cases[i].node;
        //DADSLog("\nCase id: %d", und_network.cases[i].node->id);
        //DADSLog("\nCase time: %f", und_network.cases[i].time);
        if(und_network.cases[i].time == 0) {
            st = S;
            node->state = I;
            //DADSLog("\nInfected Id: %d", node->id);
        }
        else {
            st = NS;
            if(node->state == Passive)
                node->state = NS;
        }
        for(j=0; j<node->actual_degree; j++) {
            if(node->neigbors[j]->state < st)
                node->neigbors[j]->state = st;
        }
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


double DADSLogLikelyhoodTKDR(double theta, double confirm, double decay, double relic) {
    int32_t i;
    for(i=0; i<und_network.N_cases; i++) {
        und_network.cases[i].node->theta = theta;
    }
    return DADSLogLikelyhoodKDR(confirm, decay, relic);
}


double DADSLogLikelyhoodKDR(double confirm, double decay, double relic) {
    int32_t i, j, k, n_i;
    double t = .0, dt, loglikelyhood, inf_rate, cd, relic1, relic2;
    double confirm_drop = 0.1;
    ICase cur_case, *neigh_case;
    NodePtr neighbor, cur_node;

    DADSRemarkNodes(); //dropping all I, S and NS states to initial (t=0)

/*    for(i=0; i<und_network.N; i++) {
        DADSLog("\n%d : ", und_network.nodes[i]->id);
        DADSLog(" %d", und_network.nodes[i]->state);
    }*/

    loglikelyhood = .0;
    for(i=0; i<und_network.N_cases; i++) {
        if(und_network.cases[i].time > 0.) break;
    }

    for(;i<und_network.N_cases; i++) {
        cur_case = und_network.cases[i];
        relic1 = .0;
        relic2 = .0;
        for(j=0; j<=i; j++) {
            if(decay > .0) {
                und_network.cases[j].value1 = 1./decay*(exp(decay*(und_network.cases[j].time - t)) - exp(decay*(und_network.cases[j].time - cur_case.time)));
                relic1 += relic*(und_network.cases[j].value1);
                und_network.cases[j].value1 *= und_network.cases[j].node->theta;
                und_network.cases[j].value2 = 1.*exp(decay*(und_network.cases[j].time - cur_case.time));
                relic2 += relic*(und_network.cases[j].value2);
                und_network.cases[j].value2 *= und_network.cases[j].node->theta;
            }
            else {
                und_network.cases[j].value1 = und_network.cases[j].node->theta*(cur_case.time - t);
                relic1 += relic*(cur_case.time - t);
                und_network.cases[j].value2 = und_network.cases[j].node->theta;
                relic2 += relic*1;
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
            }
            else if(cur_node->state == NS) {
                //loglikelyhood -= confirm_drop*relic*dt;
                //loglikelyhood -= relic*dt;
                //loglikelyhood -= relic;
                //loglikelyhood -= relic*i;
                loglikelyhood -= relic1;
            }
        }
        //loglikelyhood -= confirm_drop*relic*dt*(und_network.N - und_network.N_nodes_to_check);
        //loglikelyhood -= relic*dt*(und_network.N - und_network.N_nodes_to_check);
        //loglikelyhood -= relic*(und_network.N - und_network.N_nodes_to_check);
        //loglikelyhood -= relic*i*(und_network.N - und_network.N_nodes_to_check);
        loglikelyhood -= relic1*(und_network.N - und_network.N_nodes_to_check);

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
        //DADSLog("\n%f ", t);
        //DADSLog(" %f ", loglikelyhood);
    }
/*    DADSLog("\ntheta: %f", theta);
    DADSLog("\nconfirm: %f", confirm);
    DADSLog("\ndecay: %f", decay);
    DADSLog("\nrelic: %f", relic);
    DADSLog("\nLL: %f", loglikelyhood);*/
    return loglikelyhood;
}

//derivatives
double* DADSDLogLikelyhoodDtheta(double *thetas, double confirm, double decay, double relic) {
    int32_t i, j, k, n_i;
    double t = .0, dt, *dfdthetas, inf_rate, cd, L;
    double confirm_drop = 0.1;
    ICase cur_case, *neigh_case;
    NodePtr neighbor, cur_node;

    DADSRemarkNodes(); //dropping all I, S and NS states to initial (t=0)

    dfdthetas = malloc(und_network.N_cases * sizeof(double)); //partial derivatives array
    for(i=0; i<und_network.N_cases; i++) dfdthetas[i] = .0;

/*    for(i=0; i<und_network.N; i++) {
        DADSLog("\n%d : ", und_network.nodes[i]->id);
        DADSLog(" %d", und_network.nodes[i]->state);
    }*/

    for(i=0; i<und_network.N_cases; i++) {
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
    }
/*    DADSLog("\ntheta: %f", theta);
    DADSLog("\nconfirm: %f", confirm);
    DADSLog("\ndecay: %f", decay);
    DADSLog("\nrelic: %f", relic);
    DADSLog("\nLL: %f", loglikelyhood);*/
    return dfdthetas;
}

void DADSCalculateDerivatives(double theta, double confirm, double decay, double relic) {
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
    dlldthetas = DADSDLogLikelyhoodDtheta(thetas, confirm, decay, relic);

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
