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
        fread((void *)(&newNod->actual_degree), 4, 1, f);
        newNod->nominal_degree = newNod->actual_degree;
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
