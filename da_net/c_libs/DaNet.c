// Created by Gubanov Alexander (aka Derzhiarbuz) at 29.10.2020
// Contacts: derzhiarbuz@yandex.ru

#include "DaNet.h"

#include <math.h>

NodePtr newNode()
{
    NodePtr ptr;
    ptr = (NodePtr)malloc(sizeof(Node));
    ptr->actual_degree = 0;
    ptr->id = 0;
    ptr->neigbors = NULL;
    ptr->userdata = NULL;
    ptr->userdataDestructor = NULL;
    ptr->nominal_degree = 0;
    return ptr;
}


void freeNode(NodePtr node)
{
    if(!node) return;
    if(node->neigbors) free(node->neigbors);
    if(node->userdata)
    {
        if(node->userdataDestructor)
            node->userdataDestructor(node->userdata);
        else
            free(node->userdata);
    }
    free(node);
}


int nodeCompare(const void *n1, const void *n2)
{
    NodePtr node1 = *((NodePtr*)n1);
    NodePtr node2 = *((NodePtr*)n2);
    return node1->id - node2->id;
}


//NodePtr* getInNeighbors(NodePtr node) {}
//int32_t getInNeighborsN(NodePtr node) {}
//NodePtr* getOutNeighbors(NodePtr node) {}
//int32_t getOutNeighborsN(NodePtr node) {}


NetworkPtr newNetwork()
{
    NetworkPtr net;
    net = (NetworkPtr)malloc(sizeof(Network));
    initNetwork(net);
    return net;
}


void initNetwork(NetworkPtr network)
{
    network->nodes = NULL;
    network->N = 0;
}


void clearNetwork(NetworkPtr network)
{
    if(!network) return;

    NodePtr curNode;
    if(network->nodes)
    {
        for(int32_t i=0; i<network->N; i++)
        {
            curNode = network->nodes[i];
            freeNode(curNode);
        }
        free(network->nodes);
        network->nodes = NULL;
        network->N = 0;
    }
    initNetwork(network);
}


void freeNetwork(NetworkPtr network)
{
    if(!network) return;
    clearNetwork(network);
    free(network);
}


void loadNetworkFromFile(NetworkPtr network, const char * fpath)
{
    FILE * f;
    int64_t size_in_bytes = 0;

    clearNetwork(network);

    if(network->nodes != NULL)
    {
        DADSLog("\nUnable to load new network: there is one already loaded. Try to call clear_network()");
    }

    f = fopen(fpath, "rb");
    if(!f)
    {
        DADSLog("\nError: Unable to open underlying network file %s", fpath);
        return;
    }

    DADSLog("\nReading network from %s", fpath);
    fread((void *)(&network->N), 4, 1, f);

    DADSLog("\nNumber of nodes: %d", network->N);

    network->nodes = malloc(network->N * sizeof(NodePtr));
    size_in_bytes += network->N * sizeof(NodePtr);

    NodePtr newNod;
    for(int32_t i=0; i<network->N; i++)
    {
        newNod = newNode();
        fread((void *)(&newNod->nominal_degree), 4, 1, f);
        fread((void *)(&newNod->actual_degree), 4, 1, f);
        //newNod->nominal_degree = newNod->actual_degree;
        fread((void *)(&newNod->id), 4, 1, f);
        newNod->userdata = malloc(newNod->actual_degree * 4);
        fread(newNod->userdata, 4, newNod->actual_degree, f);
        network->nodes[i] = newNod;
    }

    fclose(f);

    DADSLog("\nNetwork readed. Optimizing...");

    //sorting nodes by id to make dichotomy search
    qsort(network->nodes, network->N, sizeof(NodePtr), nodeCompare);

    int64_t new_size = 0;
    #pragma omp parallel for shared(network) schedule(guided) reduction(+ : new_size)// num_threads(4)
    for(int32_t i=0; i<network->N; i++)
    {
        NodePtr curNode;
        NodePtr neigNode;
        int32_t *neig_ids;

        curNode = network->nodes[i];
        curNode->neigbors = malloc(curNode->actual_degree * sizeof(NodePtr));
        neig_ids = (int32_t *)curNode->userdata;
        for(int32_t j=0; j<curNode->actual_degree; j++)
        {
            neigNode = nodeForId(network, neig_ids[j]);
            if(!neigNode)
            {
                DADSLog("\nWarning: Unable to find a node %d", neig_ids[j]);
                break;
            }
            curNode->neigbors[j] = neigNode;
            //printf("%d : %d     ", neig_ids[j], curNode->neigbors[j]->id);
        }
        free(curNode->userdata);
        curNode->userdata = NULL;
        new_size += curNode->actual_degree * sizeof(NodePtr) + sizeof(Node);
    }
    size_in_bytes += new_size;

    DADSLog("\nNetwork optimized. Size in bytes: %d", size_in_bytes);
}

typedef struct _pair {int32_t a; int32_t b;} Pair;
typedef struct _adj {int32_t N; int32_t *nn; int32_t *nodes; int32_t **neighbors} Adj;

int pairACompare(const void *c1, const void *c2)
{
    Pair *p1 = (Pair*)c1;
    Pair *p2 = (Pair*)c2;
    if (p1->a > p2->a) return 1;
    if (p1->a == p2->a) return 0;
    return -1;
}

int pairBCompare(const void *c1, const void *c2)
{
    Pair *p1 = (Pair*)c1;
    Pair *p2 = (Pair*)c2;
    if (p1->b > p2->b) return 1;
    if (p1->b == p2->b) return 0;
    return -1;
}

void edgeListToAdjacency(Pair* elist, int32_t N_rows, Adj* aj)
{
    int32_t a, prev_a, b;
    int i, j, k;
    //counting nodes
    prev_a = 0;
    aj->N = 0;
    for(k=0; k<N_rows; k++)
    {
        a = elist[k].a;
        if(prev_a != a)
        {
            prev_a = a;
            aj->N++;
        }
    }
    DADSLog("N nodes: %i\n", aj->N);

    i=-1;
    prev_a = 0;

    //counting neighbors and writing nodes
    aj->nn = (int32_t*)malloc(aj->N*sizeof(int32_t));
    aj->nodes = (int32_t*)malloc(aj->N*sizeof(int32_t));
    for(k=0; k<N_rows; k++)
    {
        a = elist[k].a;
        if(prev_a != a)
        {
            prev_a = a;
            i++;
            aj->nn[i] = 0;
            aj->nodes[i] = a;
        }
        aj->nn[i]++;
    }
    DADSLog("Neighbors counted\n");

    //reading neighbors
    i=-1;
    aj->neighbors = (int32_t**)malloc(aj->N*sizeof(int32_t*));
    for(k=0; k<N_rows; k++)
    {
        a = elist[k].a;
        b = elist[k].b;
        if(prev_a != a)
        {
            prev_a = a;
            i++;
            aj->neighbors[i] = (int32_t*)malloc(aj->nn[i]*sizeof(int32_t));
            j = 0;
        }
        aj->neighbors[i][j] = b;
        j++;
    }
    DADSLog("Nodes readed\n");
    return aj;
}


void saveAdjToFile(FILE *f, const Adj a)
{
    DADSLog("Writing to file\n");
    fwrite((void *)&(a.N), 4, 1, f);
    for(int i=0; i<a.N; i++)
    {
        fwrite((void *)(&a.nn[i]), 4, 1, f);
        fwrite((void *)(&a.nodes[i]), 4, 1, f);
        for(int j=0; j<a.nn[i]; j++)
        {
            fwrite((void *)(&a.neighbors[i][j]), 4, 1, f);
        }
    }
    DADSLog("Writed\n");
}


void readAdjFromFile(FILE *f, Adj *a)
{
    DADSLog("Reading from file\n");
    fread((void *)&(a->N), 4, 1, f);
    a->nn = (int32_t*)malloc(a->N*sizeof(int32_t));
    a->nodes = (int32_t*)malloc(a->N*sizeof(int32_t));
    a->neighbors = (int32_t**)malloc(a->N*sizeof(int32_t*));
    for(int i=0; i<a->N; i++)
    {
        fread((void *)(&a->nn[i]), 4, 1, f);
        fread((void *)(&a->nodes[i]), 4, 1, f);
        a->neighbors[i] = (int32_t*)malloc(a->nn[i]*sizeof(int32_t));
        for(int j=0; j<a->nn[i]; j++)
        {
            fread((void *)(&a->neighbors[i][j]), 4, 1, f);
        }
    }
    DADSLog("Readed\n");
}


void freeAdj(Adj a)
{
    int i;

    free(a.nn);
    free(a.nodes);
    for(i=0; i<a.N; i++)
    {
        free(a.neighbors[i]);
    }
    free(a.neighbors);
}


void edgeListToBinary(const char * list_path, const char * network_path)
{
    FILE * f, *tof, *to2f;
    int32_t a, prev_a, b;
    char c;
    int32_t N_rows;
    Pair *rows;
    int i, j, k;
    Adj a_from;
    Adj a_to;

    char *to_path;
    to_path = (char *)malloc((strlen(network_path)+10)*sizeof(char));
    strcpy(to_path, network_path);
    to_path[strlen(network_path)] = '1';
    to_path[strlen(network_path)+1] = 0;


 /*   f = fopen(list_path, "rt");
    if(!f)
    {
        DADSLog("\nError: Unable to open edge list file %s", list_path);
        return;
    }

    tof = fopen(network_path, "wb");
    if(!tof)
    {
        DADSLog("\nError: Unable to open file to write network %s", network_path);
        fclose(f);
        return;
    }

    to2f = fopen(to_path, "wb");
    if(!to2f)
    {
        DADSLog("\nError: Unable to open file to write temporary network %s", to_path);
        fclose(f);
        fclose(tof);
        return;
    }

    //reading rows
    N_rows = 0;
    while (!feof(f))
    {
        fscanf(f, "%i%c%i", &a, &c, &b);
        N_rows++;
    }
    DADSLog("N rows: %i\n", N_rows);
    fclose(f);

    rows = (Pair*)malloc(N_rows*sizeof(Pair));
    f = fopen(list_path, "rt");
    k = 0;
    while (!feof(f))
    {
        fscanf(f, "%i%c%i", &a, &c, &b);
        rows[k].a = a;
        rows[k].b = b;
        k++;
    }

    DADSLog("Sorting by from\n");
    qsort(rows, N_rows, sizeof(Pair), pairACompare);
    DADSLog("Adjacency\n");
    edgeListToAdjacency(rows, N_rows, &a_from);

    //writing
    saveAdjToFile(tof, a_from);
    fclose(tof);
    freeAdj(a_from);

    //flipping edges
    for(k=0; k<N_rows; k++)
    {
        a = rows[k].a;
        rows[k].a = rows[k].b;
        rows[k].b = a;
    }
    DADSLog("Sorting by to\n");
    qsort(rows, N_rows, sizeof(Pair), pairACompare);
    DADSLog("Adjacency\n");
    edgeListToAdjacency(rows, N_rows, &a_to);

    free(rows);

    //writing
    saveAdjToFile(to2f, a_to);
    fclose(to2f);
    freeAdj(a_to); */

    //reading
    tof = fopen(network_path, "rb");
    if(!tof)
    {
        DADSLog("\nError: Unable to open file to read network %s", network_path);
        return;
    }
    readAdjFromFile(tof, &a_to);
    fclose(tof);

    to2f = fopen(to_path, "rb");
    if(!tof)
    {
        DADSLog("\nError: Unable to open file to read network %s", to_path);
        return;
    }
    readAdjFromFile(to2f, &a_from);
    fclose(to2f);

    int32_t *node_found;
    int32_t idx;
    int32_t total_N = 0;
    int32_t new_nn;
    int32_t *new_neighbors;
    DADSLog("Symmetrizing...\n");
    //symmetrizing first adj
    for(k=0; k<a_to.N; k++)
    {
        node_found = bsearch(&a_to.nodes[k], a_from.nodes, a_from.N, sizeof(int32_t), int32Compare);
        //add edges to nodes
        if(node_found)
        {
            total_N++;
            idx = node_found - a_from.nodes;
            new_neighbors = (int32_t*)malloc((a_to.nn[k] + a_from.nn[idx])*sizeof(int32_t));
            for(new_nn=0; new_nn<a_to.nn[k]; new_nn++)
            {
                new_neighbors[new_nn] = a_to.neighbors[k][new_nn];
            }
            for(i=0; i<a_from.nn[idx]; i++)
            {
                if(!bsearch(&a_from.neighbors[idx][i], a_to.neighbors[k], a_to.nn[k], sizeof(int32_t), int32Compare))
                {
                    new_neighbors[new_nn] = a_from.neighbors[idx][i];
                    new_nn++;
                }
            }
            free(a_to.neighbors[k]);
            a_to.neighbors[k] = new_neighbors;
            a_to.nn[k] = new_nn;
            //if(a_to.nn[k] != a_from.nn[idx])
            //{
            //    printf("%i - %i : %i\n", *node_found, a_from.nn[idx], a_to.nn[k]);
            //    failed_N++;
            //}
        }
    }
    DADSLog("Symmetrized...\n");

    DADSLog("Searching for single nodes\n");
    int32_t N_dummys = 0;
    int32_t *dummys;
    dummys = (int32_t*)malloc(a_from.N*sizeof(int32_t));
    for(int i=0; i<a_from.N; i++)
    {
        if(!bsearch(&a_from.nodes[i], a_to.nodes, a_to.N, sizeof(int32_t), int32Compare))
        {
            if(a_from.nn[i]==1)
            {
                dummys[N_dummys] = a_from.nodes[i];
                N_dummys++;
            }
        }
    }
    DADSLog("Found\n");


    total_N = a_to.N + a_from.N - total_N - N_dummys;
    DADSLog("Total nodes: %i\n", total_N);

    to_path[strlen(network_path)] = '2';
    tof = fopen(to_path, "wb");

    //writing total symmetrized adj
    DADSLog("Writing combined to file\n");
    int32_t n_not_dum;

    fwrite((void *)&(total_N), 4, 1, tof);
    for(int i=0; i<a_to.N; i++)
    {
        //counting dummy nodes
        n_not_dum = 0;
        for(int j=0; j<a_to.nn[i]; j++)
        {
            if(!bsearch(&a_to.neighbors[i][j], dummys, N_dummys, sizeof(int32_t), int32Compare))
                n_not_dum++;
        }
        fwrite((void *)(&a_to.nn[i]), 4, 1, tof);
        fwrite((void *)(&n_not_dum), 4, 1, tof);
        fwrite((void *)(&a_to.nodes[i]), 4, 1, tof);
        for(int j=0; j<a_to.nn[i]; j++)
        {
            if(!bsearch(&a_to.neighbors[i][j], dummys, N_dummys, sizeof(int32_t), int32Compare))
                fwrite((void *)(&a_to.neighbors[i][j]), 4, 1, tof);
        }
    }
    for(int i=0; i<a_from.N; i++)
    {
        if(!bsearch(&a_from.nodes[i], a_to.nodes, a_to.N, sizeof(int32_t), int32Compare) && a_from.nn[i]>1)
        {
            n_not_dum = 0;
            for(int j=0; j<a_from.nn[i]; j++)
            {
                if(!bsearch(&a_from.neighbors[i][j], dummys, N_dummys, sizeof(int32_t), int32Compare))
                    n_not_dum++;
            }
            fwrite((void *)(&a_from.nn[i]), 4, 1, tof);
            fwrite((void *)(&n_not_dum), 4, 1, tof);
            fwrite((void *)(&a_from.nodes[i]), 4, 1, tof);
            for(int j=0; j<a_from.nn[i]; j++)
            {
                if(!bsearch(&a_from.neighbors[i][j], dummys, N_dummys, sizeof(int32_t), int32Compare))
                    fwrite((void *)(&a_from.neighbors[i][j]), 4, 1, tof);
            }
        }
    }
    fclose(tof);
    DADSLog("Writed\n");
    DADSLog("N dummys: %i\n", N_dummys);


    DADSLog("All done?\n");
    free(dummys);
    freeAdj(a_from);
    freeAdj(a_to);
    DADSLog("All done\n");
}


NodePtr nodeForId(NetworkPtr network, int32_t id)
{
    NodePtr tempNode = NULL;
    NodePtr *retNode;
    if(!tempNode) tempNode = newNode();
    tempNode -> id = id;
    retNode = bsearch(&tempNode, network->nodes, network->N, sizeof(NodePtr), nodeCompare);
    if(!retNode) return NULL;
    return *retNode;
}


ICasePtr newCase()
{
    ICasePtr newCase = malloc(sizeof(ICase));
    newCase->node = NULL;
    newCase->time = .0;
    newCase->index = 0;
    return newCase;
}


void freeCase(ICasePtr cas)
{
    if(cas) free(cas);
}


int ICaseCompare(const void *c1, const void *c2)
{
    ICasePtr case1 = *((ICasePtr*)c1);
    ICasePtr case2 = *((ICasePtr*)c2);
    if (case1->time > case2->time) return 1;
    if (case1->time == case2->time) return 0;
    return -1;
}


CascadePtr newCascade()
{
    CascadePtr cascade = malloc(sizeof(Cascade));
    cascade->cases = NULL;
    cascade->id = 0;
    cascade->network = NULL;
    cascade->nodes_to_check = NULL;
    cascade->N_cases = 0;
    cascade->N_nodes_to_check = 0;
    cascade->observation_time = .0;
    return(cascade);
}


void freeCascade(CascadePtr cascade)
{
    if(!cascade) return;
    if(cascade->cases)
    {
        for(int i=0; i<cascade->N_cases; i++)
        {
            freeCase(cascade->cases[i]);
        }
        free(cascade->cases);
    }
    free(cascade);
}


int int32Compare(const void *c1, const void *c2)
{
    int32_t case1 = *((int32_t*)c1);
    int32_t case2 = *((int32_t*)c2);
    return case1-case2;
}


int32_t hello_func(int32_t a)
{
    printf("This is number %d", a);
    return a * 2;
}


void DADSEchoOn()
{
    echo = 33;
}


void DADSEchoOff()
{
    echo = 0;
}


void DADSLog(char *text, ...)
{
    va_list args;

    va_start(args, text);
    if(echo == 33) vprintf(text, args);
    va_end(args);
}
