#include "DADiffusonSimulation.h"

NodePtr newNodePtr() {
    NodePtr ptr;
    ptr = (NodePtr)malloc(sizeof(Node));
    ptr->actual_degree = 0;
    ptr->id = 0;
    ptr->neigbors = NULL;
    ptr->payload = NULL;
    ptr->nominal_degree = 0;
    return ptr;
}


void clearNodePtr(NodePtr ptr) {
    if(ptr->neigbors) free(ptr->neigbors);
    if(ptr->payload) free(ptr->payload);
    free(ptr);
}


int NodeCompare(const void *n1, const void *n2) {
    NodePtr node1 = *((NodePtr*)n1);
    NodePtr node2 = *((NodePtr*)n2);
    return node1->id - node2->id;
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
    }
}


void DADSCleatNetwork() {
    DADSInitNetwork(); //make sure that it was initiation
    if(!und_network.nodes) {
        und_network.N = 0;
        return;
    }

    NodePtr curNode;
    for(int32_t i=0; i<und_network.N; i++) {
        curNode = und_network.nodes[i];
        clearNodePtr(curNode);
    }
    free(und_network.nodes);
    und_network.nodes = NULL;
    und_network.N = 0;
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


void DADSLoadNetworkFromFile(const char * fpath) {
    FILE * f;
    int32_t i, j;

    DADSCleatNetwork();

    if(und_network.nodes != NULL) {
        DADSLog("\nUnable to load new network: there is one already loaded. Try to call clear_network()");
    }

    f = fopen(fpath, "rb");
    if(!f) {
        DADSLog("\nUnable to open underlying network file %s", fpath);
        return;
    }

    DADSLog("\nReading network from %s", fpath);
    fread((void *)(&und_network.N), 4, 1, f);

    DADSLog("\nNumber of nodes: %d", und_network.N);

    und_network.nodes = malloc(und_network.N * sizeof(NodePtr));

    NodePtr newNode;
    for(i=0; i<und_network.N; i++) {
        newNode = newNodePtr();
        fread((void *)(&newNode->actual_degree), 4, 1, f);
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
    int64_t size_in_bytes = 0;
    int32_t *neig_ids;

    for(i=0; i<und_network.N; i++) {
        curNode = und_network.nodes[i];
        curNode->neigbors = malloc(curNode->actual_degree * sizeof(NodePtr));
        neig_ids = (int32_t *)curNode->payload;
        for(j=0; j<curNode->actual_degree; j++) {
            neigNode = DADSNodeForId(neig_ids[j]);
            if(!neigNode) {
                DADSLog("\nUnable to find a node %d", tempNode->id);
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


void DADSSetMetaForNode(int32_t node_id, int32_t nominal_degree, int32_t diactivated) {
    NodePtr node = DADSNodeForId(node_id);
    if(!node) {
        DADSLog("\nNode %d not found", node_id);
        return;
    }
    node->nominal_degree = nominal_degree;
    if(diactivated)
        node->payload = (void*)diactivated;
    else
        node->payload = NULL;
}


void DADSPurifyNetwork() {
    //removing deactivated vertices

    //filling zero degrees as medians
}
