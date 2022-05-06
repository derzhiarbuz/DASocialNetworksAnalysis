#include "DiffusionTests.h"

#include <omp.h>

//theta = 0.02, delta = 0.02, rho = 0.001
double cascade_1[29][2] = {{1, 0.}, {3, 11.0}, {25, 16.0}, {4, 17.0}, {5, 26.0}, {2, 27.0},
{21, 27.0}, {22, 41.0}, {17, 42.0}, {18, 45.0}, {13, 51.0},
{6, 53.0}, {24, 55.0}, {16, 56.0}, {29, 57.0}, {11, 62.0},
{23, 70.0}, {7, 74.0}, {10, 82.0}, {8, 84.0}, {27, 88.0},
{12, 103.0}, {19, 104.0}, {15, 105.0}, {9, 111.0}, {14, 118.0},
{30, 131.0}, {20, 136.0}, {28, 139.0}};
//theta = 0.02, delta = 0.02, rho = 0.001
double cascade_2[25][2] = {{1, 0.}, {22, 15.0}, {24, 16.0}, {3, 19.0}, {23, 20.0}, {2, 26.0},
{26, 30.0}, {16, 32.0}, {6, 33.0}, {20, 35.0}, {25, 35.0},
{21, 44.0}, {17, 45.0}, {9, 66.0}, {7, 89.0}, {29, 113.0},
{5, 114.0}, {4, 125.0}, {11, 136.0}, {12, 153.0}, {10, 177.0},
{15, 183.0}, {8, 201.0}, {30, 245.0}, {14, 289.0}};
//theta = 0.02, delta = 0.02, rho = 0.001
double cascade_3[29][2] = {{1, 0.}, {3, 4.0}, {23, 4.0}, {26, 5.0}, {22, 8.0}, {25, 27.0},
{4, 41.0}, {28, 44.0}, {6, 46.0}, {18, 47.0}, {2, 59.0},
{29, 62.0}, {27, 66.0}, {16, 69.0}, {7, 73.0}, {24, 79.0},
{9, 89.0}, {31, 97.0}, {17, 104.0}, {14, 107.0}, {13, 113.0},
{21, 113.0}, {10, 114.0}, {8, 116.0}, {12, 116.0}, {11, 129.0},
{15, 204.0}, {20, 230.0}, {19, 250.0}};

DiffusionModelPtr diffusionModel = NULL;

void testLikelyhood()
{
    double t_start, t_end;
    DADSEchoOn();
    printf("\nLoading the network.");
    t_start = omp_get_wtime();
    DiffusionModelPtr model = newDiffusionModel("test_network.dos", 3);
    //DiffusionModelPtr model = newDiffusionModel("D:/BigData/Charity/Cascades/Zhestu_network.dos", 3);
    t_end = omp_get_wtime();
    printf ("\nLoaded network with with %d nodes. Time parallel %f", model->network->N, t_end - t_start);
    return;
    printf("\nAdding cascades.");
    t_start = omp_get_wtime();
    dmSetNCasesForCascade(model, 0, 29);
    dmSetObservationTimeForCascade(model, 0, 300.);
    for(int i=0; i<29; i++) {
        dmAddCase(model, 0, (int)cascade_1[i][0], cascade_1[i][1]);
    }
    dmSetNCasesForCascade(model, 1, 25);
    dmSetObservationTimeForCascade(model, 1, 300.);
    for(int i=0; i<25; i++) {
        dmAddCase(model, 1, (int)cascade_2[i][0], cascade_2[i][1]);
    }
    dmSetNCasesForCascade(model, 2, 29);
    dmSetObservationTimeForCascade(model, 2, 300.);
    for(int i=0; i<29; i++) {
        dmAddCase(model, 2, (int)cascade_3[i][0], cascade_3[i][1]);
    }
    t_end = omp_get_wtime();
    printf ("\nAdded. Time parallel %f", t_end - t_start);

    printf("\nPreparing for estimation.");
    t_start = omp_get_wtime();
    dmPrepareForEstimation(model);
    t_end = omp_get_wtime();
    printf ("\nPrepared. Time parallel %f", t_end - t_start);

    for(int i=0; i<3; i++)
    {
        model->thetas[i] = 0.001;
        model->rhos[i] = 0.001;
    }
    model->delta = 0.02;

    printf("\nCalculating loglikelyhood.");
    double ll;
    t_start = omp_get_wtime();
    ll = dmLoglikelyhoodCasewise(model);
    t_end = omp_get_wtime();
    printf ("\nLoglikelyhood: %f \n Time parallel %f", ll, t_end - t_start);
}

void testMinimizer()
{
    //DiffusionModelPtr model = newDiffusionModelWithCascades("/home/derzhiarbuz/Bigdata/Charity/Cascades/Zashitim_taigu_-164443025_8726_8021_6846u_network.dos",
    //                                                        "/home/derzhiarbuz/Bigdata/Charity/Cascades/Zashitim_taigu_-164443025_8726_8021_6846_outcomes_bin.cb", 3600);
    DiffusionModelPtr model = newDiffusionModelWithCascades("/home/derzhiarbuz/Bigdata/Charity/Cascades/Zashitim_taigu_-164443025_8726_8021_6846u_network.dos",
                                                            "/home/derzhiarbuz/Bigdata/Charity/Cascades/Zashitim_taigu_-164443025_8726_8021_6846_8726_seq_bin.cb", 3600);
    //DiffusionModelPtr model = newDiffusionModelWithCascades("/home/derzhiarbuz/Bigdata/Charity/Cascades/RussianBirchu_network.dos",
    //                                                        "/home/derzhiarbuz/Bigdata/Charity/Cascades/RussianBirch_outcomes_bin.cb", 3600);
    //DiffusionModelPtr model = newDiffusionModelWithCascades("/home/derzhiarbuz/Bigdata/Charity/Cascades/WorldVitau_network.dos",
    //                                                        "/home/derzhiarbuz/Bigdata/Charity/Cascades/WorldVita_outcomes_bin.cb", 3600);
    //dmPrepareForEstimation(model);
    //dmSetGradientAlphasPatternLength(model, 0);
    //dmSetThetas(model, 1e-8);
    //dmSetRhos(model, 1e-8);
    //model->has_thetas = 1;
    //model->has_rhos = 1;
    //model->has_alphas = 0;
    //dmSaveModelState(model, "/home/derzhiarbuz/Bigdata/Charity/Cascades/Zashitim_taigu_-164443025_8726_8021_6846_state1seq.csv");
    dmLoadModelState(model, "/home/derzhiarbuz/Bigdata/Charity/Cascades/Zashitim_taigu_-164443025_8726_8021_6846_state1seq.csv");
    dmMaximizeICM(model, 3000);
    dmSaveModelState(model, "/home/derzhiarbuz/Bigdata/Charity/Cascades/Zashitim_taigu_-164443025_8726_8021_6846_state1seq.csv");
    //dmSetAlphasPatternOutliers(model);
    //dmSaveModelState(model, "/home/derzhiarbuz/Bigdata/Charity/Cascades/Zashitim_taigu_-164443025_8726_8021_6846_state2seq.csv");
    //dmLoadModelState(model, "/home/derzhiarbuz/Bigdata/Charity/Cascades/Zashitim_taigu_-164443025_8726_8021_6846_state3seq.csv");
    //model->has_thetas = 0;
    //model->has_rhos = 0;
    //model->has_alphas = 1;
    //dmMaximizeICM(model, 600);
    //dmSaveModelState(model, "/home/derzhiarbuz/Bigdata/Charity/Cascades/Zashitim_taigu_-164443025_8726_8021_6846_state3seq.csv");
}
