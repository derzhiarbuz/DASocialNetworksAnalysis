// Created by Gubanov Alexander (aka Derzhiarbuz) at 02.11.2020
// Contacts: derzhiarbuz@yandex.ru

#ifndef NN
#define NN 30000000
#endif // N

#include <math.h>
#include <omp.h>
#include <stdio.h>
#include "Diffusion.h"


void createNumbersInDiffusionNodeData(DiffusionNodeDataPtr dnd, int32_t n_cases)
{
    dnd->case_numbers = (int32_t*)malloc(sizeof(int32_t)*n_cases);
    for(int32_t i=0; i<n_cases; i++)
        dnd->case_numbers[i] = -1;
}


DiffusionNodeDataPtr newDiffusionNodeData(int32_t n_cases)
{
    DiffusionNodeDataPtr newDND;
    newDND = (DiffusionNodeDataPtr)malloc(sizeof(DiffusionNodeData));
    newDND->alpha = 1.0;
    if(n_cases>0)
    {
        createNumbersInDiffusionNodeData(newDND, n_cases);
    }
    else
    {
        newDND->case_numbers = NULL;
    }
    return newDND;
}


void freeDiffusionNodeData(DiffusionNodeDataPtr dnd)
{
    if(dnd->case_numbers) free(dnd->case_numbers);
    free(dnd);
}


DiffusionModelPtr newDiffusionModelEmpty()
{
    DiffusionModelPtr newDM;
    newDM = (DiffusionModelPtr)malloc(sizeof(DiffusionModel));
    newDM->network = NULL;
    newDM->cascades = NULL;
    newDM->N_cascades = 0;
    newDM->thetas = NULL;
    newDM->rhos = NULL;
    newDM->delta = 0;
    newDM->kappas = NULL;
    newDM->has_alphas = 0;
    newDM->has_delta = 0;
    newDM->has_rhos = 0;
    newDM->has_thetas = 0;
    newDM->has_kappa = 0;
    newDM->prepared = 0;
    return newDM;
}


DiffusionModelPtr newDiffusionModel(const char* network_file_path, int16_t n_cascades)
{
    DiffusionModelPtr newDM = newDiffusionModelEmpty();
    newDM->network = newNetwork();
    loadNetworkFromFile(newDM->network, network_file_path);

    newDM->cascades = malloc(sizeof(CascadePtr)*n_cascades);
    newDM->thetas = malloc(sizeof(double)*n_cascades);
    newDM->rhos = malloc(sizeof(double)*n_cascades);
    newDM->kappas = malloc(sizeof(double)*n_cascades);
    newDM->N_cascades = n_cascades;
    for(int i=0; i<n_cascades; i++)
    {
        newDM->cascades[i] = newCascade();
        newDM->cascades[i]->id = i;
        newDM->cascades[i]->network = newDM->network;
        newDM->thetas[i] = .0;
        newDM->rhos[i] = .0;
        newDM->kappas[i] = .0;
    }
    return newDM;
}


void clearDiffusionModel(DiffusionModelPtr model)
{
    if(model->network)
    {
        freeNetwork(model->network);
        model->network = NULL;
    }
    if(model->cascades)
    {
        for(int32_t i=0; i<model->N_cascades; i++)
        {
            freeCascade(model->cascades[i]);
        }
        free(model->cascades);
        model->cascades = NULL;
    }
    if(model->thetas) free(model->thetas);
    model->thetas = NULL;
    if(model->rhos) free(model->rhos);
    model->rhos = NULL;
    if(model->kappas) free(model->kappas);
    model->kappas = NULL;
    model->prepared = 0;
}


void freeDiffusionModel(DiffusionModelPtr model)
{
    clearDiffusionModel(model);
    free(model);
}


int dmCaseNumberForNode(NodePtr node, int32_t cascade_n) {
    DiffusionNodeDataPtr node_data = (DiffusionNodeDataPtr)node->userdata;
    if(!node_data) return -1;
    if(!node_data->case_numbers) return -1;
    return node_data->case_numbers[cascade_n];
}


int dmIsNodeInfected(NodePtr node, int32_t cascade_n, int32_t case_n) {
    int case_number = dmCaseNumberForNode(node, cascade_n);
    if(case_number < 0) return 0;
    if(case_number < case_n) return 1;
    return 0;
}


void dmSetAlphaForNode(NodePtr node, double alpha)
{
    DiffusionNodeDataPtr node_data = (DiffusionNodeDataPtr)node->userdata;
    if(!node_data) return;
    node_data->alpha = alpha;
}


double dmAlphaForNode(NodePtr node)
{
    DiffusionNodeDataPtr node_data = (DiffusionNodeDataPtr)node->userdata;
    if(!node_data) return 1.;
    return node_data->alpha;
}


void dmSetNCasesForCascade(DiffusionModelPtr model, int32_t cascade_n, int32_t n_cases)
{
    CascadePtr cascade = model->cascades[cascade_n];
    if(cascade->cases)
    {
        for(int i=0; i<cascade->N_cases; i++)
            freeCase(cascade->cases[i]);
        free(cascade->cases);
    }
    cascade->cases_length = n_cases;
    cascade->cases = malloc(sizeof(ICasePtr)*n_cases);
    for(int i=0; i<cascade->cases_length; i++)
        cascade->cases[i] = NULL;
    model->prepared = 0;
}


void dmSetObservationTimeForCascade(DiffusionModelPtr model, int32_t cascade_n, double observation_time)
{
    CascadePtr cascade = model->cascades[cascade_n];
    cascade->observation_time = observation_time;
}


void dmAddCase(DiffusionModelPtr model, int32_t cascade_n, int32_t node_id, double case_time)
{
    CascadePtr cascade = model->cascades[cascade_n];
    int i;
    for(i=0; i<cascade->cases_length; i++)
    {
        if(cascade->cases[i] == NULL)
        {
            NodePtr node = nodeForId(model->network, node_id);
            if(!node)
            {
                DADSLog("\nTrying to add case for node id %d which does not exist", node_id);
                //exit(666);
                return;
            }
            ICasePtr cas = newCase();
            cas->index = i;
            cas->node = node;
            cas->time = case_time;
            cascade->cases[i] = cas;
//            #pragma omp atomic
            if(node)
            {
                if(node->userdata == NULL)
                {
                    node->userdata = newDiffusionNodeData(model->N_cascades);
                }
                DiffusionNodeDataPtr dnd = (DiffusionNodeDataPtr)node->userdata;
//            #pragma omp atomic
                if(dnd->case_numbers == NULL)
                    createNumbersInDiffusionNodeData(dnd, model->N_cascades);
                dnd->case_numbers[cascade_n] = i;
            }

            break;
        }
    }
    if(i >= cascade->cases_length)
        DADSLog("\nTrying to add case for node id %d, but there is no place for it", node_id);
    else
        cascade->N_cases = i+1;
    model->prepared = 0;
}


void dmPrepareForEstimation(DiffusionModelPtr model)
{
    #pragma omp parallel for shared(model) schedule(guided)
    for(int i=0; i<model->network->N; i++)
    {
        NodePtr node = model->network->nodes[i];
        DiffusionNodeDataPtr dnd;
        if(node->userdata == NULL)
        {
            for(int32_t j=0; j<node->actual_degree; j++)
            {
                NodePtr neighbor = node->neigbors[j];
                dnd = (DiffusionNodeDataPtr)neighbor->userdata;
                if(dnd)
                {
                    if(dnd->case_numbers)
                    {
                        node->userdata = newDiffusionNodeData(0); //creating userdata with empty cases array
                        break;
                    }
                }
            }
        }
    }

    #pragma omp parallel for shared(model) schedule(guided)
    for(int i=0; i<model->N_cascades; i++)
    {
        CascadePtr cascade = model->cascades[i];
        //sorting cases by time
        qsort(cascade->cases, cascade->N_cases, sizeof(ICasePtr), ICaseCompare);
        #pragma omp parallel for shared(cascade) schedule(guided)
        for(int j=0; j<cascade->N_cases; j++)
        {
            ICasePtr cas = cascade->cases[j];
            cas->index = j;
            //printf("\n%d ", ((DiffusionNodeDataPtr)cas->node));
            ((DiffusionNodeDataPtr)cas->node->userdata)->case_numbers[i] = j;
        }
        /*for(int j=0; j<cascade->N_cases; j++)
        {
            ICasePtr cas = cascade->cases[j];
            printf("\n%d  %d  %d  %f", j, cas->index, cas->node->id, cas->time);
        }*/
        int32_t nnodes = 0;

        #pragma omp parallel for shared(cascade) schedule(guided) reduction(+ : nnodes)
        for(int j=0; j<model->network->N; j++)
        {
            NodePtr node = model->network->nodes[j];
            NodePtr neighbor;
            DiffusionNodeDataPtr dnd;
            dnd = (DiffusionNodeDataPtr)node->userdata;
            if(dnd && dnd->case_numbers && dnd->case_numbers[i] > -1)
            {
                nnodes++;
            }
            else
                for(int k=0; k<node->actual_degree; k++)
                {
                    neighbor = node->neigbors[k];
                    dnd = (DiffusionNodeDataPtr)neighbor->userdata;
                    if(dnd && dnd->case_numbers && dnd->case_numbers[i] > -1)
                    {
                        nnodes++;
                        break;
                    }
                }
        }

        if(cascade->nodes_to_check) free(cascade->nodes_to_check);
        cascade->nodes_to_check = malloc(sizeof(NodePtr)*nnodes);
        cascade->N_nodes_to_check = nnodes;
        int last_index = 0;

        for(int j=0; j<model->network->N; j++)
        {
            NodePtr node = model->network->nodes[j];
            NodePtr neighbor;
            DiffusionNodeDataPtr dnd;
            dnd = (DiffusionNodeDataPtr)node->userdata;
            if(dnd && dnd->case_numbers && dnd->case_numbers[i] > -1)
            {
                {
                    cascade->nodes_to_check[last_index] = node;
                    last_index++;
                }
            }
            else
                for(int k=0; k<node->actual_degree; k++)
                {
                    neighbor = node->neigbors[k];
                    dnd = (DiffusionNodeDataPtr)neighbor->userdata;
                    if(dnd && dnd->case_numbers && dnd->case_numbers[i] > -1)
                    {
                        {
                            cascade->nodes_to_check[last_index] = node;
                            last_index++;
                        }
                        break;
                    }
                }
        }

    }
    model->prepared = 1;
}


double dmLoglikelyhoodForCase(DiffusionModelPtr model, int32_t cascade_n, int32_t case_n)
{
    if(case_n <= 0) return .0;

    double *values1;
    double *values2;
    values1 = (double *)malloc(sizeof(double)*(case_n));
    values2 = (double *)malloc(sizeof(double)*(case_n));
    int32_t i;

    CascadePtr cascade = model->cascades[cascade_n];
    if(case_n >= cascade->N_cases && cascade->cases[cascade->N_cases-1]->time >= cascade->observation_time)
        return .0;
    //if case_n is greater than last case number, than it means the moment of the end of observation
    double new_time = (case_n < cascade->N_cases) ? cascade->cases[case_n]->time : cascade->observation_time;
    double prev_time = cascade->cases[case_n-1]->time;
    double theta = model->thetas[cascade_n];
    double delta = model->delta;
    double rho = model->rhos[cascade_n];
    double kappa = model->rhos[cascade_n];
    double relic1 = .0, relic2 = .0;
    double loglikelyhood = .0;

    //calculate infection influence for nodes infected at time new_time
    #pragma omp parallel for \
    shared(values1, values2, model, case_n, cascade, new_time, prev_time, theta, delta, rho) \
    private(i) \
    schedule(guided) \
    reduction(+ : relic1, relic2)
    for(i=0; i<case_n; i++)
    {
        ICasePtr icase = cascade->cases[i];
        DiffusionNodeDataPtr node_data = (DiffusionNodeDataPtr)icase->node->userdata;
        if(model->delta > .0)
        {
            values1[i] = 1./delta*(exp(delta*(icase->time - prev_time))
                                           - exp(delta*(icase->time - new_time)));
            relic1 += rho*(values1[i]);
            values1[i] *= theta * node_data->alpha;

            values2[i] = 1.*exp(delta*(icase->time - new_time));
            relic2 += rho*(values2[i]);
            values2[i] *= theta * node_data->alpha;
        }
        else
        {
            values1[i] = theta * node_data->alpha * (new_time - prev_time);
            relic1 += rho*(new_time - prev_time);
            values2[i] = theta * node_data->alpha;
            relic2 += rho;
        }
    }

    //this wired logarithm should reduce the effect of large size of network on rho
    //relic1 /= log(model->network->N);
    //relic2 /= log(model->network->N);
    //relic1 /= log(cascade->N_nodes_to_check);
    //relic2 /= log(cascade->N_nodes_to_check);

    //accumulation the part of sum for probability to be not infected
    #pragma omp parallel for \
    shared(values1, relic1, case_n, cascade, cascade_n) \
    private(i) \
    schedule(guided) \
    reduction(+ : loglikelyhood)
    for(i=0; i<cascade->N_nodes_to_check; i++)
    {
        NodePtr cur_node = cascade->nodes_to_check[i];
        NodePtr neighbor;
        double inf_rate;
        int n_inf_neighbors;

        if(!dmIsNodeInfected(cur_node, cascade_n, case_n))
        { //if node is susceptible
            inf_rate = .0;
            n_inf_neighbors = 0;
            for(int32_t j=0; j<cur_node->actual_degree; j++)
            {
                neighbor = cur_node->neigbors[j];
                if(dmIsNodeInfected(neighbor, cascade_n, case_n))
                { //neighbor is infected
                    inf_rate += values1[dmCaseNumberForNode(neighbor, cascade_n)];
                    n_inf_neighbors++;
                }
            }
            loglikelyhood += -(inf_rate * pow(n_inf_neighbors, kappa) + relic1);
        }
    }

    //the member of ll function for all others in the network that are not infected through unobserved ties
    loglikelyhood -= relic1*(model->network->N - cascade->N_nodes_to_check);

    //the member of ll function defined by infection at the end of current time interval
    if(case_n < cascade->N_cases) { //if it's a case, not the end of observation
        NodePtr cur_node = cascade->cases[case_n]->node;
        NodePtr neighbor;
        double inf_rate = .0;
        int n_inf_neighbors = 0;
        for(int32_t j=0; j<cur_node->actual_degree; j++) {
            neighbor = cur_node->neigbors[j];
            if(dmIsNodeInfected(neighbor, cascade_n, case_n)) { //neighbor is infected
                inf_rate += values2[dmCaseNumberForNode(neighbor, cascade_n)];
                n_inf_neighbors++;
            }
        }
        loglikelyhood += log(inf_rate * pow(n_inf_neighbors, kappa) + relic2);
    }

    free(values1);
    free(values2);

    return loglikelyhood;
}


double dmLoglikelyhoodCasewise(DiffusionModelPtr model)
{
    if(!model) return -1.0;
    if(!model->prepared) dmPrepareForEstimation(model);
    double loglikelyhood = .0;
    //return .0;

    //#pragma omp parallel for shared(model) schedule(static) reduction(+ : loglikelyhood)
    for(int32_t i=0; i<model->N_cascades; i++)
    {
        CascadePtr cascade = model->cascades[i];
        double loglikelyhood_local = .0;
        #pragma omp parallel for shared(model) schedule(static) reduction(+ : loglikelyhood_local)
        for(int32_t j=0; j<=cascade->N_cases; j++) //j is <= because the last iteration means the moment of the end of observation
        {
            loglikelyhood_local += dmLoglikelyhoodForCase(model, i, j);
        }
        loglikelyhood += loglikelyhood_local;
    }

    return loglikelyhood;
}


double dmLoglikelyhoodNodewise(DiffusionModelPtr model)
{
    return dmLoglikelyhoodCasewise(model);
}


double dmLoglikelyhoodICMForCascade(DiffusionModelPtr model, int32_t cascade_n)
{
    CascadePtr cascade = model->cascades[cascade_n];
    double theta = model->thetas[cascade_n];
    double rho = model->rhos[cascade_n];
    //double logtheta = log(1-theta);
    double logrho = log(1-rho);
    double loglikelyhood = .0;
    #pragma omp parallel for shared(model) schedule(static) reduction(+ : loglikelyhood)
    for(int32_t i=0; i<cascade->N_nodes_to_check; i++)
    {
        double temp;
        NodePtr cur_node = cascade->nodes_to_check[i];
        NodePtr neighbor;

        int n_inf_neighbors = 0;
        int case_number = dmCaseNumberForNode(cur_node, cascade_n);
        if(case_number>0 && cascade->cases[case_number]->time>.0) //if node was infected and it was not initially infected
        {
            temp = 1.;
            for(int32_t j=0; j<cur_node->actual_degree; j++)
            {
                neighbor = cur_node->neigbors[j];
                if(dmCaseNumberForNode(neighbor, cascade_n) >= 0) //if neighbor is in infection cases
                {
                    if(cascade->cases[dmCaseNumberForNode(neighbor, cascade_n)]->time < cascade->cases[case_number]->time) //if it infected earlier
                    {
                        n_inf_neighbors++;
                        temp*=(1-theta*dmAlphaForNode(neighbor));
                    }
                }
            }
            loglikelyhood += log(1. - temp*pow(1-rho, case_number));
        }
        else if (case_number<0) //node was not infected
        {
            temp = 1.;
            for(int32_t j=0; j<cur_node->actual_degree; j++)
            {
                neighbor = cur_node->neigbors[j];
                if(dmIsNodeInfected(neighbor, cascade_n, cascade->N_cases)) //if neighbor is in infection cases
                {
                    n_inf_neighbors++;
                    temp *= (1-theta*dmAlphaForNode(neighbor));
                }
            }
            loglikelyhood += log(temp);
        }
        //probability that nodes was not infected through unobserved ties
    }
    loglikelyhood += cascade->N_cases*logrho*(model->network->N - cascade->N_cases);
    return loglikelyhood;
}

double dmLoglikelyhoodICM(DiffusionModelPtr model)
{
    if(!model) return -1.0;
    if(!model->prepared) dmPrepareForEstimation(model);
    double loglikelyhood = .0;

    for(int32_t i=0; i<model->N_cascades; i++)
    {
        loglikelyhood += dmLoglikelyhoodICMForCascade(model, i);
    }

    return loglikelyhood;
}


//============================================================================
//LIBRARY FUNCTIONS
//============================================================================

DiffusionModelPtr diffusionModels[100];
int model_created = 0;

int32_t dmLibNewDiffusionModel(const char* network_file_path, int32_t n_cascades)
{
    int i;
    if(!model_created)
    {
        for(i=0; i<100; i++) diffusionModels[i] = NULL;
        model_created = 1;
    }
    for(i=0; i<100 && diffusionModels[i]!=NULL; i++);
    if(i>=100) return -1;

    DiffusionModelPtr model = newDiffusionModel(network_file_path, n_cascades);
    diffusionModels[i] = model;
    return i;
}


void dmLibDeleteDiffusionModel(int32_t model_id)
{
    if(diffusionModels[model_id])
    {
        freeDiffusionModel(diffusionModels[model_id]);
        diffusionModels[model_id] = NULL;
    }
}


void dmLibSetNCasesForCascade(int32_t model_id, int32_t cascade_n, int32_t n_cases)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
        dmSetNCasesForCascade(model, cascade_n, n_cases);
}


void dmLibSetObservationTimeForCascade(int32_t model_id, int32_t cascade_n, double observation_time)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
        dmSetObservationTimeForCascade(model, cascade_n, observation_time);
}


void dmLibAddCase(int32_t model_id, int32_t cascade_n, int32_t node_id, double case_time)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
        dmAddCase(model, cascade_n, node_id, case_time);
}


void dmLibSetThetas(int32_t model_id, double theta)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model && model->thetas)
        for(int i=0; i<model->N_cascades; i++)
            model->thetas[i] = theta;
}


void dmLibSetRhos(int32_t model_id, double rho)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model && model->rhos)
        for(int i=0; i<model->N_cascades; i++)
            model->rhos[i] = rho;
}


void dmLibSetKappas(int32_t model_id, double kappa)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model && model->kappas)
        for(int i=0; i<model->N_cascades; i++)
            model->kappas[i] = kappa;
}


void dmLibSetDelta(int32_t model_id, double delta)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
        model->delta = delta;
}


void dmLibSetThetaForCascade(int32_t model_id, int32_t cascade_n, double theta)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model && model->thetas)
        model->thetas[cascade_n] = theta;
}


void dmLibSetRhoForCascade(int32_t model_id, int32_t cascade_n, double rho)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model && model->rhos)
        model->rhos[cascade_n] = rho;
}


void dmLibSetKappaForCascade(int32_t model_id, int32_t cascade_n, double kappa)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model && model->kappas)
        model->kappas[cascade_n] = kappa;
}


void dmLibSetAlphaForNode(int32_t model_id, int32_t node_id, double alpha)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model && model->network)
    {
        NodePtr node = nodeForId(model->network, node_id);
        if(node) dmSetAlphaForNode(node, alpha);
    }
}


double dmLibLoglikelyhood(int32_t model_id)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
    {
        if(model->has_kappa!=0 || 1) //slower but considering network configuration on each infection step
            return dmLoglikelyhoodCasewise(model);
        else //faster but each node influence is independent
            return dmLoglikelyhoodNodewise(model);
    }
    return .0;
}


double dmLibLoglikelyhoodICM(int32_t model_id)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
        return dmLoglikelyhoodICM(model);
    return .0;
}
