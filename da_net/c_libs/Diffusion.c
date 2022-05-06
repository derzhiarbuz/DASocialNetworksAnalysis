// Created by Gubanov Alexander (aka Derzhiarbuz) at 02.11.2020
// Contacts: derzhiarbuz@yandex.ru

#ifndef NN
#define NN 30000000
#endif // N

#include <math.h>
#include <omp.h>
#include <stdio.h>
#include "Diffusion.h"

ool_diff_Hv_accel *ool_accel;


int inegerPairCompareA(const void *n1, const void *n2)
{
    IntegerPair* ip1 = (IntegerPair*)n1;
    IntegerPair* ip2 = (IntegerPair*)n2;
    return ip1->a - ip2->a;
}


void createNumbersInDiffusionNodeData(DiffusionNodeDataPtr dnd, int32_t n_cases)
{
    dnd->n_case_numbers = n_cases;
    if(n_cases <= 0)
    {
        dnd->n_case_numbers = 0;
        dnd->case_numbers = NULL;
        return;
    }

    dnd->case_numbers = (IntegerPair*)malloc(sizeof(IntegerPair)*n_cases);
    for(int32_t i=0; i<n_cases; i++)
    {
        dnd->case_numbers[i].a = i;
        dnd->case_numbers[i].b = -1;
    }
}


DiffusionNodeDataPtr newDiffusionNodeData(int32_t n_cases)
{
    DiffusionNodeDataPtr newDND;
    newDND = (DiffusionNodeDataPtr)malloc(sizeof(DiffusionNodeData));
    newDND->alpha = 1.0;
    if(n_cases>0)
    {
        //createNumbersInDiffusionNodeData(newDND, n_cases);
        createNumbersInDiffusionNodeData(newDND, n_cases);
    }
    else
    {
        newDND->n_case_numbers = 0;
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
    newDM->gradient_alpha_pattern = NULL;
    newDM->gradient_alpha_length = 0;
    newDM->gradient_vector = NULL;
    newDM->gradient_vector_length = 0;
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

DiffusionModelPtr newDiffusionModelWithCascades(const char* network_file_path, const char* cascades_file_path, float normalisation_factor)
{
    DiffusionModelPtr newDM = newDiffusionModelEmpty();
    newDM->network = newNetwork();
    loadNetworkFromFile(newDM->network, network_file_path);

    FILE * f;
    int32_t a, b;
    int j;

    f = fopen(cascades_file_path, "rb");
    if(!f)
    {
        DADSLog("\nError: Unable to open cascades file %s", cascades_file_path);
        return newDM;
    }

    DADSLog("\nReading cascades from %s", cascades_file_path);
    fread((void *)(&newDM->N_cascades), 4, 1, f);
    DADSLog("\nNumber of cascades: %d", newDM->N_cascades);

    newDM->cascades = malloc(sizeof(CascadePtr)*newDM->N_cascades);
    newDM->thetas = malloc(sizeof(double)*newDM->N_cascades);
    newDM->rhos = malloc(sizeof(double)*newDM->N_cascades);
    newDM->kappas = malloc(sizeof(double)*newDM->N_cascades);

    for(int i=0; i<newDM->N_cascades; i++)
    {
        newDM->cascades[i] = newCascade();
        newDM->cascades[i]->network = newDM->network;
        newDM->thetas[i] = .0;
        newDM->rhos[i] = .0;
        newDM->kappas[i] = .0;

        DADSLog("\nReading cascade %d", i+1);
        DADSLog(" of %d", newDM->N_cascades);
        fread((void *)(&a), 4, 1, f);
        dmSetNCasesForCascade(newDM, i, a);
        DADSLog("\nNumber of cases: %d", newDM->cascades[i]->cases_length);
        fread((void *)(&newDM->cascades[i]->from_id), 4, 1, f);
        fread((void *)(&newDM->cascades[i]->id), 4, 1, f);
        fread((void *)(&b), 4, 1, f);
        newDM->cascades[i]->observation_time = b/normalisation_factor;
        DADSLog("\nFrom id: %d", newDM->cascades[i]->from_id);
        for(j=0; j<newDM->cascades[i]->cases_length; j++) {
            fread((void *)(&a), 4, 1, f);
            fread((void *)(&b), 4, 1, f);
            dmAddCase(newDM, i, a, b/normalisation_factor);
        }
        DADSLog("\nId: %d", newDM->cascades[i]->id);
    }
    DADSLog("\nReaded.");
    fclose(f);
    DADSLog("\nClosed.");
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
    if(model->gradient_alpha_pattern) free(model->gradient_alpha_pattern);
    model->gradient_alpha_pattern = NULL;
    model->prepared = 0;
}


void freeDiffusionModel(DiffusionModelPtr model)
{
    clearDiffusionModel(model);
    free(model);
}


int32_t diffusionNodeDataGetCaseNumber(DiffusionNodeDataPtr userdata, int32_t cascade_n)
{
    IntegerPair tmp = {cascade_n, 0};
    IntegerPair *result;
    result = (IntegerPair*)bsearch(&tmp, userdata->case_numbers, userdata->n_case_numbers, sizeof(IntegerPair), inegerPairCompareA);
    if(!result) return -1;
    return result->b;
}


void diffusionNodeDataSetCaseNumber(DiffusionNodeDataPtr userdata, int32_t case_n, int32_t cascade_n)
{
    if(!userdata->case_numbers)
    {
        userdata->n_case_numbers = 1;
        userdata->case_numbers = (IntegerPair*)malloc(sizeof(IntegerPair)*userdata->n_case_numbers);
        userdata->case_numbers[0].a = cascade_n;
        userdata->case_numbers[0].b = case_n;
    }
    else
    {
        IntegerPair tmp = {cascade_n, 0};
        IntegerPair *result;
        result = (IntegerPair*)bsearch(&tmp, userdata->case_numbers, userdata->n_case_numbers, sizeof(IntegerPair), inegerPairCompareA);
        if(result) result->b = case_n;
        else
        {
            result = (IntegerPair*)malloc(sizeof(IntegerPair)*(userdata->n_case_numbers+1));
            int32_t i;
            for(i=0; i<userdata->n_case_numbers && userdata->case_numbers[i].a<cascade_n; i++)
                result[i] = userdata->case_numbers[i];
            result[i].a = cascade_n;
            result[i].b = case_n;
            i++;
            userdata->n_case_numbers++;
            for(; i<userdata->n_case_numbers && userdata->case_numbers[i].a<cascade_n; i++)
                result[i] = userdata->case_numbers[i-1];
            free(userdata->case_numbers);
            userdata->case_numbers = result;
        }
    }
}


int dmCaseNumberForNode(NodePtr node, int32_t cascade_n) {
    DiffusionNodeDataPtr node_data = (DiffusionNodeDataPtr)node->userdata;
    if(!node_data) return -1;
    if(!node_data->case_numbers) return -1;
    //return node_data->case_numbers[cascade_n];
    return diffusionNodeDataGetCaseNumber(node_data, cascade_n);
}


int dmIsNodeInfected(NodePtr node, int32_t cascade_n, int32_t case_n) {
    int case_number = dmCaseNumberForNode(node, cascade_n);
    if(case_number < 0) return 0;
    if(case_number < case_n) return 1;
    return 0;
}


void dmSetAlphaForNode(NodePtr node, double alpha)
{
    if(!node)
        return;
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


void dmSetGradientAlphasPatternLength(DiffusionModelPtr model, int32_t n_nodes)
{
    if(model)
    {
        if(model->gradient_alpha_pattern)
        {
            free(model->gradient_alpha_pattern);
            model->gradient_alpha_pattern = NULL;
            model->gradient_alpha_length = 0;
        }
        if(model->gradient_vector)
        {
            free(model->gradient_vector);
            model->gradient_vector = NULL;
            model->gradient_vector_length = 0;
        }
        if(n_nodes>=0)
        {
            if(n_nodes>0)
            {
                model->gradient_alpha_pattern = malloc(sizeof(NodePtr)*n_nodes);
                model->gradient_alpha_length = n_nodes;
            }
            model->gradient_vector = malloc(sizeof(double)*(2*model->N_cascades + n_nodes));
            model->gradient_vector_length = 2*model->N_cascades + n_nodes;
        }
    }
}


int gradientCompare(const void *n1, const void *n2)
{
    double x1 = *((double*)n1);
    double x2 = *((double*)n2);
    return (int)(x2 - x1);
}


void dmSetAlphasPatternOutliers(DiffusionModelPtr model)
{
    int32_t n, i;
    NodePtr node;
    double *dlldalpha;

    n = 0;
    for(i=0; i<model->network->N; i++)
    {
        node=model->network->nodes[i];
        if(node->userdata && ((DiffusionNodeDataPtr)node->userdata)->case_numbers) n++;
    }
    dmSetGradientAlphasPatternLength(model, n);

    n = 0;
    for(i=0; i<model->network->N; i++)
    {
        node=model->network->nodes[i];
        if(node->userdata && ((DiffusionNodeDataPtr)node->userdata)->case_numbers)
        {
            dmSetGradientAlphasPattern(model, node->id, n);
            n++;
        }
    }
    dmPrepareForEstimation(model);
    dmGradientICM(model);
    dlldalpha = malloc(model->gradient_alpha_length * sizeof(double));

    for(i=0; i<model->gradient_alpha_length; i++)
    {
        dlldalpha[i] = model->gradient_vector[model->gradient_vector_length-1-model->gradient_alpha_length+i];
    }
    qsort(dlldalpha, model->gradient_alpha_length, sizeof(double), gradientCompare);

    int n_outliers = 5;
    double min = dlldalpha[n-n_outliers];
    double max = dlldalpha[n_outliers-1];
    double a;
    NodePtr *uncommon_nodes = malloc(4 * n_outliers * sizeof(NodePtr));

    n = 0;
    for(i=0; i<model->gradient_alpha_length; i++)
    {
        a = model->gradient_vector[model->gradient_vector_length-1-model->gradient_alpha_length+i];
        if(a <= min || a >= max)
        {
            uncommon_nodes[n] = model->gradient_alpha_pattern[i];
            printf("\n%d   %f", uncommon_nodes[n]->id, a);
            if(((DiffusionNodeDataPtr)uncommon_nodes[n]->userdata)->case_numbers)
            {
                printf("\n");
                for(int k=0; k<model->N_cascades; k++)
                    //printf("%d ", ((DiffusionNodeDataPtr)uncommon_nodes[n]->userdata)->case_numbers[k]);
                    printf("%d ", diffusionNodeDataGetCaseNumber((DiffusionNodeDataPtr)uncommon_nodes[n]->userdata, k));
            }
            n++;
        }
    }

    dmSetGradientAlphasPatternLength(model, n);
    for(i=0; i<n; i++)
    {
        model->gradient_alpha_pattern[i] = uncommon_nodes[i];
    }

    free(uncommon_nodes);
    free(dlldalpha);
}


void dmSetAlphaForPattern(DiffusionModelPtr model, int32_t alpha_n, double alpha)
{
    if(!model->gradient_alpha_pattern)
        return;
    if(model->gradient_alpha_length <= alpha_n)
        return;
    dmSetAlphaForNode(model->gradient_alpha_pattern[alpha_n], alpha);
}


double dmAlphaForPattern(DiffusionModelPtr model, int32_t alpha_n)
{
    if(!model->gradient_alpha_pattern)
        return 0;
    if(model->gradient_alpha_length <= alpha_n)
        return 0;
    return dmAlphaForNode(model->gradient_alpha_pattern[alpha_n]);
}



void dmSetGradientAlphasPattern(DiffusionModelPtr model, int32_t node_id, int32_t node_n)
{
    if(model)
    {
        NodePtr node = nodeForId(model->network, node_id);
        model->gradient_alpha_pattern[node_n] = node;
    }
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
                    //node->userdata = newDiffusionNodeData(model->N_cascades);
                    node->userdata = newDiffusionNodeData(0);
                }
                DiffusionNodeDataPtr dnd = (DiffusionNodeDataPtr)node->userdata;
//            #pragma omp atomic
                //if(dnd->case_numbers == NULL)
                //    createNumbersInDiffusionNodeData(dnd, model->N_cascades);
                //dnd->case_numbers[cascade_n] = i;
                diffusionNodeDataSetCaseNumber(dnd, i, cascade_n);
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


void dmSetThetas(DiffusionModelPtr model, double theta)
{
    if(model && model->thetas)
        for(int i=0; i<model->N_cascades; i++)
            model->thetas[i] = theta;
}


void dmSetRhos(DiffusionModelPtr model, double rho)
{
    if(model && model->rhos)
        for(int i=0; i<model->N_cascades; i++)
            model->rhos[i] = rho;
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
                        node->userdata = newDiffusionNodeData(0); //creating userdata with NULL cases array
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
        DADSLog("\nAdding case %d", i);
        DADSLog(" of %d", model->N_cascades);
        //#pragma omp parallel for shared(cascade) schedule(guided)
        for(int j=0; j<cascade->N_cases; j++)
        {
            ICasePtr cas = cascade->cases[j];
            cas->index = j;
            //printf("\n%d ", ((DiffusionNodeDataPtr)cas->node));
            //((DiffusionNodeDataPtr)cas->node->userdata)->case_numbers[i] = j;
            diffusionNodeDataSetCaseNumber((DiffusionNodeDataPtr)cas->node->userdata, j, i);
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
            //if(dnd && dnd->case_numbers && dnd->case_numbers[i] > -1)
            if(dnd && dnd->case_numbers && diffusionNodeDataGetCaseNumber(dnd, i) > -1)
            {
                nnodes++;
            }
            else
            {
                for(int k=0; k<node->actual_degree; k++)
                {
                    neighbor = node->neigbors[k];
                    dnd = (DiffusionNodeDataPtr)neighbor->userdata;
                    //if(dnd && dnd->case_numbers && dnd->case_numbers[i] > -1)
                    if(dnd && dnd->case_numbers && diffusionNodeDataGetCaseNumber(dnd, i) > -1)
                    {
                        nnodes++;
                        break;
                    }
                }
            }
        }
        DADSLog("\nNode cases updated. Allocate %d nodes.", nnodes);

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
            //if(dnd && dnd->case_numbers && dnd->case_numbers[i] > -1)
            if(dnd && dnd->case_numbers && diffusionNodeDataGetCaseNumber(dnd, i) > -1)
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
                    //if(dnd && dnd->case_numbers && dnd->case_numbers[i] > -1)
                    if(dnd && dnd->case_numbers && diffusionNodeDataGetCaseNumber(dnd, i) > -1)
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

//derivatives
double dmdLogliklelyhooddThetaICM(DiffusionModelPtr model, int32_t cascade_n)
{
    double reduction_result = .0;
    for(int l=0; l<model->N_cascades; l++) //going through all cases
    {

        if(cascade_n != l) //derivative by p_k is non zero only for k cascade
            continue;
        double theta = model->thetas[cascade_n];
        double rho = model->rhos[cascade_n];
        CascadePtr cascade = model->cascades[cascade_n];
        #pragma omp parallel for shared(model, theta, rho, cascade_n, cascade) schedule(static) reduction(+ : reduction_result)
        for(int32_t i=0; i<cascade->N_nodes_to_check; i++)
        {
            double temp;
            double Y;
            //double Yexp;
            int32_t j;
            NodePtr cur_node = cascade->nodes_to_check[i];
            NodePtr neighbor;

            int case_number = dmCaseNumberForNode(cur_node, cascade_n);
            if(case_number>0 && cascade->cases[case_number]->time>.0) //if node was infected and it was not initially infected
            {
                Y = 1.;
                //Yexp = .0;
                temp = .0;
                for(j=0; j<cur_node->actual_degree; j++)
                {
                    neighbor = cur_node->neigbors[j];
                    if(dmCaseNumberForNode(neighbor, cascade_n) >= 0) //if neighbor is in infection cases
                    {
                        if(cascade->cases[dmCaseNumberForNode(neighbor, cascade_n)]->time < cascade->cases[case_number]->time) //if it was infected earlier
                        {
                            Y *= (1. - dmAlphaForNode(neighbor) * theta);
                            temp += - dmAlphaForNode(neighbor) / (1. - dmAlphaForNode(neighbor) * theta);
                        }
                    }
                }
                for(j=0; j<case_number; j++)
                {
                    if(cascade->cases[j]->time < cascade->cases[case_number]->time)
                    {
                        //Yexp += dmAlphaForNode(cascade->cases[j]->node) * rho;
                        Y *= (1. - dmAlphaForNode(cascade->cases[j]->node) * rho);
                    }
                }
                //Y *= exp(-Yexp);
                if(temp !=.0)
                {
                    reduction_result += Y/(Y - 1.) * temp;
                }
            }
            else if (case_number<0) //node is not initial
            {
                temp = .0;
                for(j=0; j<cur_node->actual_degree; j++)
                {
                    neighbor = cur_node->neigbors[j];
                    if(dmIsNodeInfected(neighbor, cascade_n, cascade->N_cases)) //if neighbor is in infection cases
                    {
                        temp += - dmAlphaForNode(neighbor) / (1. - dmAlphaForNode(neighbor) * theta);
                    }
                }
                reduction_result += temp;
            }
        }
    }
    return reduction_result;
}

double dmdLogliklelyhooddRhoICM(DiffusionModelPtr model, int32_t cascade_n)
{
    double reduction_result = .0;
    for(int l=0; l<model->N_cascades; l++) //going through all cases
    {
        if(cascade_n != l) //derivative by p_k is non zero only for k cascade
            continue;
        double theta = model->thetas[cascade_n];
        double rho = model->rhos[cascade_n];
        if(rho==0)
            continue;
        CascadePtr cascade = model->cascades[cascade_n];
        #pragma omp parallel for shared(model, theta, rho, cascade) schedule(static) reduction(+ : reduction_result)
        for(int32_t i=0; i<cascade->N_cases; i++)
        {
            double Y;
            //double Yexp;
            double temp;
            int32_t j;
            NodePtr cur_node = cascade->cases[i]->node;
            NodePtr neighbor;

            int case_number = i;
            if(cascade->cases[case_number]->time>.0) //if node was infected and it was not initially infected
            {
                Y = 1.;
                //Yexp = .0;
                temp = .0;
                for(j=0; j<cur_node->actual_degree; j++)
                {
                    neighbor = cur_node->neigbors[j];
                    if(dmCaseNumberForNode(neighbor, cascade_n) >= 0) //if neighbor is in infection cases
                    {
                        if(cascade->cases[dmCaseNumberForNode(neighbor, cascade_n)]->time < cascade->cases[case_number]->time) //if it was infected earlier
                        {
                            Y *= (1. - dmAlphaForNode(neighbor) * theta);
                        }
                    }
                }
                for(j=0; j<case_number; j++)
                {
                    if(cascade->cases[j]->time < cascade->cases[case_number]->time)
                    {
                        Y *= (1. - dmAlphaForNode(cascade->cases[j]->node) * rho);
                        //Yexp += dmAlphaForNode(cascade->cases[j]->node) * rho;
                        temp += - dmAlphaForNode(cascade->cases[j]->node) / (1. - dmAlphaForNode(cascade->cases[j]->node) * rho);
                    }
                }
                //Y *= exp(-Yexp);
                if(temp != .0)
                    reduction_result += Y/(Y - 1.) * temp;
            }
        }
        //for all non infected cases the value is the same
        double temp;
        temp = .0;
        for(int32_t i=0; i<cascade->N_cases; i++)
        {
            temp += - dmAlphaForNode(cascade->cases[i]->node) / (1. - dmAlphaForNode(cascade->cases[i]->node) * rho);
        }
        reduction_result += temp * (model->network->N - cascade->N_cases);
    }
    return reduction_result;
}

double dmdLogliklelyhooddAlphaICM(DiffusionModelPtr model, NodePtr alpha_node)
{
    if(!alpha_node)
        return .0;
    double reduction_result = .0;
    for(int l=0; l<model->N_cascades; l++) //going through all cases
    {
        int cascade_n = l;
//        if(alpha_node->id == 190654130) printf("\nNODE 1");
        //if alpha node was not infected in l cascade thet the derivative is 0
        if(dmCaseNumberForNode(alpha_node, cascade_n) < 0)
            continue;
//        if(alpha_node->id == 190654130) printf("\nNODE 2");
        double theta = model->thetas[cascade_n];
        double rho = model->rhos[cascade_n];
        CascadePtr cascade = model->cascades[cascade_n];
        //#pragma omp parallel for shared(model, theta, rho, cascade_n) schedule(static) reduction(+ : reduction_result)
        for(int32_t i=0; i<cascade->N_nodes_to_check; i++)
        {
            double temp;
            double Y;
            int32_t j;
            NodePtr cur_node = cascade->nodes_to_check[i];
            NodePtr neighbor;

            int case_number = dmCaseNumberForNode(cur_node, cascade_n);
            if(case_number>0 && cascade->cases[case_number]->time>.0) //if node was infected and it was not initially infected
            {
                Y = 1.;
                temp = .0;
                for(j=0; j<cur_node->actual_degree; j++)
                {
                    neighbor = cur_node->neigbors[j];
                    if(dmCaseNumberForNode(neighbor, cascade_n) >= 0) //if neighbor is in infection cases
                    {
                        if(cascade->cases[dmCaseNumberForNode(neighbor, cascade_n)]->time < cascade->cases[case_number]->time) //if it was infected earlier
                        {
                            Y *= (1. - dmAlphaForNode(neighbor) * theta);
                            if(alpha_node == neighbor)
                                temp += - theta / (1. - dmAlphaForNode(neighbor) * theta);
                        }
                    }
                }
                for(j=0; j<case_number; j++)
                {
                    if(cascade->cases[j]->time < cascade->cases[case_number]->time)
                    {
                        Y *= (1. - dmAlphaForNode(cascade->cases[j]->node) * rho);
                        if(alpha_node == cascade->cases[j]->node)
                            temp += - rho / (1. - dmAlphaForNode(cascade->cases[j]->node) * rho);
                    }
                }
                reduction_result += Y/(Y - 1.) * temp;
//                if(alpha_node->id == 190654130 && temp != 0) printf("\nNUMBER %d TEMP %f YMULT %f", case_number, Y/(Y - 1.) * temp, Y/(Y - 1.));
            }
            else if (case_number<0) //was not infected
            {
                temp = .0;
                for(j=0; j<cur_node->actual_degree; j++)
                {
                    neighbor = cur_node->neigbors[j];
                    if(dmIsNodeInfected(neighbor, cascade_n, cascade->N_cases)) //if neighbor is in infection cases
                    {
                        if(alpha_node == neighbor)
                            temp += - theta / (1. - dmAlphaForNode(neighbor) * theta);
                    }
                }
                reduction_result += temp;
//                if(alpha_node->id == 190654130 && temp != 0) {
//                   printf("\nNUMBER2 %d TEMP %f", case_number, temp);
//                }
            }
        }
        //the member that is the same for all non infected nodes
        reduction_result += (- rho / (1. - dmAlphaForNode(alpha_node) * rho)) * (model->network->N - cascade->N_cases);
    }
    return reduction_result;
}

void dmGradientICM(DiffusionModelPtr model)
{
    if(!model) return;
    if(!model->prepared) dmPrepareForEstimation(model);

    for(int k=0; k<model->gradient_vector_length; k++)
    {
        if(k<model->N_cascades) //p
        {
            model->gradient_vector[k] = dmdLogliklelyhooddThetaICM(model, k);
        }
        else if(k<2*model->N_cascades) //q
        {
            model->gradient_vector[k] = dmdLogliklelyhooddRhoICM(model, k-model->N_cascades);
        }
        else //alpha
        {
            model->gradient_vector[k] = dmdLogliklelyhooddAlphaICM(model, model->gradient_alpha_pattern[k-2*model->N_cascades]);
        }
    }
}

void dmHessianICM(DiffusionModelPtr model)
{

}

void dmSetGslVector(DiffusionModelPtr model, const gsl_vector *v)
{
    int32_t i, j;
    double val;

    j = 0;
    if(model->has_thetas)
    {
        for(i=0; i<model->N_cascades; i++)
        {
            val = gsl_vector_get(v, j);
            model->thetas[i] = val;
            j++;
        }
    }
    if(model->has_rhos)
    {
        for(i=0; i<model->N_cascades; i++)
        {
            val = gsl_vector_get(v, j);
            model->rhos[i] = val/300;
            j++;
        }
    }
    if(model->has_alphas)
    {
        for(i=0; i<model->gradient_alpha_length; i++)
        {
            val = gsl_vector_get(v, j);
            dmSetAlphaForPattern(model, i, val);
            j++;
        }
    }
}

//function for using in GSL minimization procedure
double dmLoglikelyhoodICMGSL(const gsl_vector *v, void *params)
{
    DiffusionModelPtr model = (DiffusionModelPtr)params;
    dmSetGslVector(model, v);
    /*printf("\nFunc: ");
    for(int i=0; i<model->gradient_vector_length; i++)
    {
        printf("%.15f ", gsl_vector_get (v, i));
    }*/
    printf("\nLogLikelyhood: ");
    double f = -dmLoglikelyhoodICM(model);
    printf("%.5f", f);

    return f;
}

//function gradient for using in GSL minimization procedure
void dmLoglikelyhoodICMGSLgradient(const gsl_vector *v, void *params, gsl_vector *df)
{
    DiffusionModelPtr model = (DiffusionModelPtr)params;
    dmSetGslVector(model, v);

    /*printf("\nGrad: ");
    for(int i=0; i<model->gradient_vector_length; i++)
    {
        printf("%.15f ", gsl_vector_get (v, i));
    }*/
    int j=0;

    printf("\nGradient: ");
    dmGradientICM(model);
    printf("done");
    if(model->has_thetas)
    {
        for(int32_t i=0; i<model->N_cascades; i++)
        {
            gsl_vector_set(df, j, -model->gradient_vector[i]);
            j++;
        }
    }
    if(model->has_rhos)
    {
        for(int32_t i=0; i<model->N_cascades; i++)
        {
            gsl_vector_set(df, j, -model->gradient_vector[model->N_cascades+i]);
            j++;
        }
    }
    if(model->has_alphas)
    {
        for(int32_t i=0; i<model->gradient_alpha_length; i++)
        {
            gsl_vector_set(df, j, -model->gradient_vector[2*model->N_cascades+i]);
            j++;
        }
    }
}


//function gradient for using in GSL minimization procedure
void dmlldllICMGSL(const gsl_vector *v, void *params, double *f, gsl_vector *df)
{
    DiffusionModelPtr model = (DiffusionModelPtr)params;
    dmSetGslVector(model, v);

    /*printf("\nFuncGrad: ");
    for(int i=0; i<model->gradient_vector_length; i++)
    {
        printf("%.15f ", gsl_vector_get (v, i));
    }*/

    *f = -dmLoglikelyhoodICM(model);

    int j=0;

    dmGradientICM(model);
    if(model->has_thetas)
    {
        for(int32_t i=0; i<model->N_cascades; i++)
        {
            gsl_vector_set(df, j, -model->gradient_vector[i]);
            j++;
        }
    }
    if(model->has_rhos)
    {
        for(int32_t i=0; i<model->N_cascades; i++)
        {
            gsl_vector_set(df, j, -model->gradient_vector[model->N_cascades+i]);
            j++;
        }
    }
    if(model->has_alphas)
    {
        for(int32_t i=0; i<model->gradient_alpha_length; i++)
        {
            gsl_vector_set(df, j, -model->gradient_vector[2*model->N_cascades+i]);
            j++;
        }
    }
}


void dmNumHessICMGSL( const gsl_vector *X, void *params, const gsl_vector *V, gsl_vector *hv )
{
    printf("\nHessian!");
    ool_diff_Hv(ool_accel, &dmlldllICMGSL, X, params, V, hv, 1e-8);
}


void dmLoadModelState(DiffusionModelPtr model, const char * state_path)
{
    if(!model) return;

    //read point coordinates
    FILE * f;

    f = fopen(state_path, "rt");
    if(!f)
    {
        DADSLog("\ndmMaximizeICM: unable to read current coordinates from %s", state_path);
        return;
    }

    int32_t n;
    int32_t a;
    double b;
    NodePtr node;

    //reading thetas
    fscanf(f, "%d", &n);
    //printf("%d ", n);
    fscanf(f, "%d", &model->has_thetas);
    //printf("%d\n", model->has_thetas);
    if(n != model->N_cascades)
    {
        DADSLog("\ndmMaximizeICM: number of thetas does not fit number of cascades. Aborting.");
        fclose(f);
        return;
    }
    for(int32_t i=0; i<n; i++)
    {
        fscanf(f, "%d", &a);
        //printf("%d ", a);
        fscanf(f, "%d", &a);
        //printf("%d ", a);
        fscanf(f, "%le", &b);
        //printf("%e\n", b);
        model->thetas[i]=b;
    }

    //reading rhos
    fscanf(f, "%d", &n);
    fscanf(f, "%d", &model->has_rhos);
    if(n != model->N_cascades)
    {
        DADSLog("\ndmMaximizeICM: number of rhos does not fit number of cascades. Aborting.");
        fclose(f);
        return;
    }
    for(int32_t i=0; i<n; i++)
    {
        fscanf(f, "%d", &a);
        fscanf(f, "%d", &a);
        fscanf(f, "%le", &b);
        model->rhos[i] = b;
    }

    //reading alphas
    fscanf(f, "%d", &n);
    for(int32_t i=0; i<n; i++)
    {
        fscanf(f, "%d", &a);
        fscanf(f, "%le", &b);
        node = nodeForId(model->network, a);
        if(!node)
        {
            DADSLog("\ndmMaximizeICM: can not find node %d to get alpha. Aborting.");
            fclose(f);
            return;
        }
        dmSetAlphaForNode(node, b);
    }


    fscanf(f, "%d", &n);
    dmSetGradientAlphasPatternLength(model, n);
    for(int32_t i=0; i<n; i++)
    {
        fscanf(f, "%d", &a);
        dmSetGradientAlphasPattern(model, a, i);
    }

    fclose(f);
}


void dmSaveModelState(DiffusionModelPtr model, const char * state_path)
{
        if(!model) return;

    //read point coordinates
    FILE * f;

    f = fopen(state_path, "wt");
    if(!f)
    {
        DADSLog("\ndmMaximizeICM: unable to write current coordinates to %s", state_path);
        return;
    }

    int32_t n;
    int32_t a;
    double b;
    NodePtr node;

    //writing thetas
    fprintf(f, "%d ", model->N_cascades);
    fprintf(f, "%d\n", model->has_thetas);
    for(int32_t i=0; i<model->N_cascades; i++)
    {
        fprintf(f, "%d ", model->cascades[i]->from_id);
        fprintf(f, "%d ", model->cascades[i]->id);
        fprintf(f, "%le\n", model->thetas[i]);
    }

    //writing rhos
    fprintf(f, "%d ", model->N_cascades);
    fprintf(f, "%d\n", model->has_thetas);
    for(int32_t i=0; i<model->N_cascades; i++)
    {
        fprintf(f, "%d ", model->cascades[i]->from_id);
        fprintf(f, "%d ", model->cascades[i]->id);
        fprintf(f, "%le\n", model->rhos[i]);
    }

    //writing alphas
    n = 0;
    for(int32_t i=0; i<model->network->N; i++)
    {
        node = model->network->nodes[i];
        if(node->userdata) n++;
    }
    fprintf(f, "%d\n", n);
    for(int32_t i=0; i<model->network->N; i++)
    {
        node = model->network->nodes[i];
        if(node->userdata)
        {
            fprintf(f, "%d ", node->id);
            fprintf(f, "%le\n", dmAlphaForNode(node));
        }
    }

    //writing alphas pattern
    fprintf(f, "%d\n", model->gradient_alpha_length);
    for(int32_t i=0; i<model->gradient_alpha_length; i++)
    {
        fprintf(f, "%d\n", model->gradient_alpha_pattern[i]->id);
    }

    fclose(f);
}


void dmMaximizeICM(DiffusionModelPtr model, int32_t max_steps)
{
    int32_t N = 0;

    if(model->has_thetas) N += model->N_cascades;
    if(model->has_rhos) N += model->N_cascades;
    if(model->has_alphas) N += model->gradient_alpha_length;

    ool_accel = ool_diff_Hv_accel_alloc(N);

    //maximizing loglikelyhood
    size_t iter = 0;
    int status;
    size_t i, j;

    const ool_conmin_minimizer_type *T;
    ool_conmin_spg_parameters P;
    ool_conmin_minimizer *s;


    gsl_vector *x;
    ool_conmin_function ll_func;
    ool_conmin_constraint C;

    ll_func.n = N;
    ll_func.f = &dmLoglikelyhoodICMGSL;
    ll_func.df = &dmLoglikelyhoodICMGSLgradient;
    ll_func.fdf = &dmlldllICMGSL;
    ll_func.Hv = &dmNumHessICMGSL;
    ll_func.params = (void*)model;

    C.n = N;
    C.U = gsl_vector_alloc(C.n);
    C.L = gsl_vector_alloc(C.n);
    gsl_vector_set_all(C.U, 0.01);
    gsl_vector_set_all(C.L, 1e-14);

    //setting current coordinates
    x = gsl_vector_alloc(N);
    j = 0;
    if(model->has_thetas)
    {
        for(i=0; i<model->N_cascades; i++)
        {
            gsl_vector_set (x, j, model->thetas[i]);
            j++;
        }
    }
    if(model->has_rhos)
    {
        for(i=0; i<model->N_cascades; i++)
        {
            gsl_vector_set (x, j, model->rhos[i]*300);
            j++;
        }
    }
    if(model->has_alphas)
    {
        for(i=0; i<model->gradient_alpha_length; i++)
        {
            gsl_vector_set (x, j, dmAlphaForPattern(model, i));
            gsl_vector_set (C.U, j, 50);
            j++;
        }
    }

    T = ool_conmin_minimizer_spg;
    s = ool_conmin_minimizer_alloc(T, N);
    P.tol = 1e-10;
    P.gamma = 1e-10;
    P.alphamin = 1e-10;
    P.alphamax = 1e30;
    P.M = 1;
    P.sigma1 = 0.5;
    ool_conmin_parameters_default(T, (void*)&P);

    ool_conmin_minimizer_set(s, &ll_func, &C, x, (void*)&P);

    //iterate through descent steps
    do
    {
        iter++;
        status = ool_conmin_minimizer_iterate (s);
        printf("\n%d", status);

        if (status)
        break;

        status = ool_conmin_is_optimal (s);


        printf ("\n%5d", iter);
        printf("\n%.9f", s->f);
    }
    while (status == OOL_CONTINUE && iter < max_steps);
    printf ("Minimum found at:\n");

    printf ("\n%5d\n", iter);
    for(i=0; i<N; i++)
    {
        printf("\n%d %.10f ", i, gsl_vector_get (s->x, i));
    }

    ool_conmin_minimizer_free(s);
    gsl_vector_free (x);
    gsl_vector_free(C.U);
    gsl_vector_free(C.L);

    ool_diff_Hv_accel_free(ool_accel);

    //write point coordinates
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
    dmSetThetas(model, theta);
}


void dmLibSetRhos(int32_t model_id, double rho)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    dmSetRhos(model, rho);
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


void dmLibSetAlphaForPattern(int32_t model_id, int32_t alpha_n, double alpha)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model && model->network)
        dmSetAlphaForPattern(model, alpha_n, alpha);
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

void dmLibSetGradientAlphasPatternLength(int32_t model_id, int32_t n_nodes)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
    {
        dmSetGradientAlphasPatternLength(model, n_nodes);
    }
}

void dmLibSetGradientAlphasPattern(int32_t model_id, int32_t node_id, int32_t node_n)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
    {
        dmSetGradientAlphasPattern(model, node_id, node_n);
    }
}

void dmLibGradientICM(int32_t model_id)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
    {
        dmGradientICM(model);
    }
}

double dmLibGetGradient(int32_t model_id, int32_t var_number)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
    {
        return model->gradient_vector[var_number];
    }
    return .0;
}

int32_t dmLibGetGradientLength(int32_t model_id)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
    {
        return model->gradient_vector_length;
    }
    return 0;
}

void dmLibSetGradientValue(int32_t model_id, int32_t value_n, double value)
{
    DiffusionModelPtr model = diffusionModels[model_id];
    if(model)
    {
        if(value_n < model->N_cascades)
            dmLibSetThetaForCascade(model_id, value_n, value);
        else if(value_n < 2*model->N_cascades)
            dmLibSetRhoForCascade(model_id, value_n-model->N_cascades, value);
        else
            dmSetAlphaForNode(model->gradient_alpha_pattern[value_n-2*model->N_cascades], value);
    }
}
