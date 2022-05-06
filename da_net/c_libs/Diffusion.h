// Created by Gubanov Alexander (aka Derzhiarbuz) at 02.11.2020
// Contacts: derzhiarbuz@yandex.ru

/*!
@file
\~russian @brief Модель диффузии
@details -

\~english @brief -
@details -
*/

#ifndef _DIFFUSION_H_INCLUDED_
#define _DIFFUSION_H_INCLUDED_

#ifdef  __cplusplus
extern "C" {
#endif

#include <malloc.h>
#include <gsl/gsl_multimin.h>
#include <ool/ool_conmin.h>
#include <ool/ool_tools_diff.h>
#include "DaNet.h"

typedef struct IntegerPair_ IntegerPair;
typedef struct DiffusionNodeData DiffusionNodeData;
typedef struct DiffusionModel DiffusionModel;
/*! \~russian \addtogroup DiffusionGroup Модель диффузии
    @{
    \~english \addtogroup DiffusionGroup Diffusion model
    @{
*/
typedef DiffusionNodeData* DiffusionNodeDataPtr;
typedef DiffusionModel* DiffusionModelPtr;

struct IntegerPair_ {
    int32_t a;
    int32_t b;
};

int inegerPairCompareA(const void *n1, const void *n2);

/*!
\~russian @brief Параметры узла в модели диффузии
@details Струкутра описывает данные, которые должен содержать узел в сети, с которой работает модель диффузии.
В частности это индивидуальный модификатор интенсивности заражения alpha и массив случаев заражения,
с которыми ассоциирован данный узел.

\~english @brief -
@details -
*/
struct DiffusionNodeData {
    /*!
    \~russian @brief Индексы случаев заражения, ассоциированных с узлом.
    @details Если не NULL, то это массив, число элементов в котором совпадает с числом каскадов (CascadePtr) в модели
    (поле cascades объекта DiffusionModelPtr). Каждый i-й
    элемент массива - индекс случая заражения (ICasePtr), ассоциированного с данным узлов в i-м каскаде (i-й элемент массива
    cascades объекта DiffusionModelPtr). Если данный узел не был заражён в i-м каскаде (а значит и нет для него случая
    заражения), то i-й элемент массива равен -1.

    \~english @brief -
    @details -
    */
    IntegerPair *case_numbers;
    int32_t n_case_numbers;
    double alpha; ///<\~russian Модификатор интенсивности заражения \~english Infection rate modifier
};
void createNumbersInDiffusionNodeData(DiffusionNodeDataPtr dnd, int32_t n_cases);
/*!
\~russian @brief конструктор для DiffusionNodeDataPtr
@details функция создаёт новый объект DiffusionNodeDataPtr. Если узел учавствует хотя бы в одном каскаде, то
в качестве аргумента передаётся число каскадов в модели. Если нет, то 0 (в этом случае память под массив case_numbers
не выделяется)
@param n_cases - количество каскадов в модели, если узел задействован хотя бы в одном каскаде, или 0 в противном случае.
@return вновь созданный объект DiffusionNodeDataPtr
\~english @brief -
@details -
*/
DiffusionNodeDataPtr newDiffusionNodeData(int32_t n_cases);
/*!
\~russian @brief деструктор для DiffusionNodeDataPtr
@details освобождает память от объекта DiffusionNodeDataPtr
@param dnd - объект DiffusionNodeDataPtr
\~english @brief -
@details -
*/
void freeDiffusionNodeData(DiffusionNodeDataPtr dnd);

int32_t diffusionNodeDataGetCaseNumber(DiffusionNodeDataPtr userdata, int32_t cascade_n);

void diffusionNodeDataSetCaseNumber(DiffusionNodeDataPtr userdata, int32_t case_n, int32_t cascade_n);

/*!
\~russian @brief Модель диффузии
@details Струкутра описывает модель диффузии. Модель отвечает за создание и уничтожение объекта сети (NetworkPtr), на
которой происходит процесс диффузии, а так же массива каскадов (CascadePtr). Важно помнить, что модель при своей работе
изменяет сеть, поэтому использование одного объекта NetworkPtr для нескольких моделей не предполагается.

\~english @brief -
@details -
*/
struct DiffusionModel {
    NetworkPtr network; ///<\~russian Сеть \~english Network
    CascadePtr *cascades; ///<\~russian Множество каскадов на сети \~english A set of cascades on network
    int32_t N_cascades; ///<\~russian Число каскадов \~english Number of cascades

    double *thetas; ///<\~russian Массив параметров theta для каскадов \~english Array of model parameters thetas for cascades
    double *rhos; ///<\~russian Массив параметров rho для каскадов \~english Array of model parameters rhos for cascades
    double delta;  ///<\~russian Параметр модели delta \~english The delta model parameter
    double *kappas; ///<\~russian Массив параметров kappa для каскадов \~english Array of model parameters kappas for cascades

    NodePtr *gradient_alpha_pattern;
    int gradient_alpha_length;
    double *gradient_vector;
    int gradient_vector_length;
    double *hessian_matrix;

    int32_t has_thetas;
    int32_t has_rhos;
    int32_t has_alphas;
    int32_t has_delta;
    int32_t has_kappa;

    int prepared;
};
/*!
\~russian @brief конструктор для DiffusionModelPtr
@details функция создаёт новый объект DiffusionModelPtr. Все поля инициализируются значениями 0 или NULL.
@return вновь созданный объект DiffusionModelPtr
\~english @brief -
@details -
*/
DiffusionModelPtr newDiffusionModelEmpty();
/*!
\~russian @brief функция, создающая модель на заданной сети
@details функция создаёт новый объект DiffusionModelPtr. В качестве сети-подложки загружается сеть из файла network_file_path.
Так же инициализируется массив каскадов размера n_cascades.
@return вновь созданный объект DiffusionModelPtr
\~english @brief -
@details -
*/
DiffusionModelPtr newDiffusionModel(const char* network_file_path, int16_t n_cascades);
/*!
\~russian @brief функция, создающая модель на заданной сети с заданными каскадами
@details функция создаёт новый объект DiffusionModelPtr. В качестве сети-подложки загружается сеть из файла network_file_path.
Так же из файла cascades_file_path загружаются каскады. Так как время в файле каскадов указывается в секундах, то задаётся фактор
нормализации, задающий единичный временной интервал в модели (например, 3600 для единичного интервала в 1 час)
@return вновь созданный объект DiffusionModelPtr
\~english @brief -
@details -
*/
DiffusionModelPtr newDiffusionModelWithCascades(const char* network_file_path, const char* cascades_file_path, float normalisation_factor);
/*!
\~russian @brief функция, сбрасывающая модель
@details в функции освобождается динамическая память, выделенная моделью, а так же обнуляются значения всех полей
\param network объект DiffusionModelPtr, который необходимо сбросить

\~english @brief -
@details -
*/
void clearDiffusionModel(DiffusionModelPtr model);
/*!
\~russian @brief деструктор для DiffusionModelPtr
@details освобождает память от объекта DiffusionModelPtr
@param model - объект DiffusionModelPtr
\~english @brief -
@details -
*/
void freeDiffusionModel(DiffusionModelPtr model);
/*!
\~russian @brief индекс случая заражения, ассоциированного с узлом в cascade_n'м каскаде
@details если в модели данный узел был заражён хотя бы в одном каскаде, то в его поле userdata содержится объект
DiffusionNodeDataPtr, который, в свою очередь, содержит массив case_numbers, в котором перечислены номера случаев
заражения, ассоциированных с данным узлом в каскадах модели. Функция возвращает этот номер (или -1, если в каскаде
с номером cascade_n данный узел заражён не был)
@param node - узел
@param cascade_n - номер каскада
@return номер случая заражения, ассоциированного с данным узлом в каскаде с номером cascade_n или -1
\~english @brief -
@details -
*/
int dmCaseNumberForNode(NodePtr node, int32_t cascade_n);
/*!
\~russian @brief проверка на то, был ли узел инфецирован до случая зараения case_n в каскаде cascade_n
@details -
@param node - узел
@param cascade_n - номер каскада
@param case_n - номер случая заражения
@return 1, если узел был инфецирован в каскаде с номером cascade_n до момента, в который произошёл случай заражения
с номером case_n. 0 в противном случае.
\~english @brief -
@details -
*/
int dmIsNodeInfected(NodePtr node, int32_t cascade_n, int32_t case_n);

void dmSetAlphaForNode(NodePtr node, double alpha);
double dmAlphaForNode(NodePtr node);
void dmSetGradientAlphasPatternLength(DiffusionModelPtr model, int32_t n_nodes);
void dmSetAlphasPatternOutliers(DiffusionModelPtr model);
void dmSetAlphaForPattern(DiffusionModelPtr model, int32_t alpha_n, double alpha);
double dmAlphaForPattern(DiffusionModelPtr model, int32_t alpha_n);
void dmSetGradientAlphasPattern(DiffusionModelPtr model, int32_t node_id, int32_t node_n);
void dmSetNCasesForCascade(DiffusionModelPtr model, int32_t cascade_n, int32_t n_cases);
void dmSetObservationTimeForCascade(DiffusionModelPtr model, int32_t cascade_n, double observation_time);
void dmAddCase(DiffusionModelPtr model, int32_t cascade_n, int32_t node_id, double case_time);
void dmSetThetas(DiffusionModelPtr model, double theta);
void dmSetRhos(DiffusionModelPtr model, double rho);
void dmPrepareForEstimation(DiffusionModelPtr model);

double dmLoglikelyhoodForCase(DiffusionModelPtr model, int32_t cascade_n, int32_t case_n);
double dmLoglikelyhoodCasewise(DiffusionModelPtr model);
double dmLoglikelyhoodNodewise(DiffusionModelPtr model);
double dmLoglikelyhoodICM(DiffusionModelPtr model);

double dmdLogliklelyhooddThetaICM(DiffusionModelPtr model, int32_t cascade_n);
double dmdLogliklelyhooddRhoICM(DiffusionModelPtr model, int32_t cascade_n);
double dmdLogliklelyhooddAlphaICM(DiffusionModelPtr model, NodePtr alpha_node);
void dmGradientICM(DiffusionModelPtr model);
void dmHessianICM(DiffusionModelPtr model);

void dmLoadModelState(DiffusionModelPtr model, const char * state_path);
void dmSaveModelState(DiffusionModelPtr model, const char * state_path);
void dmMaximizeICM(DiffusionModelPtr model, int32_t max_steps);

/*! @} */


/*! \~russian \addtogroup LibraryGroup Библиотечные функции вызова
    @{
    \~english \addtogroup LibraryGroup Library functions
    @{
*/
int32_t dmLibNewDiffusionModel(const char* network_file_path, int32_t n_cascades);
void dmLibDeleteDiffusionModel(int32_t model_id);
void dmLibSetNCasesForCascade(int32_t model_id, int32_t cascade_n, int32_t n_cases);
void dmLibSetObservationTimeForCascade(int32_t model_id, int32_t cascade_n, double observation_time);
void dmLibAddCase(int32_t model_id, int32_t cascade_n, int32_t node_id, double case_time);
void dmLibSetThetas(int32_t model_id, double theta);
void dmLibSetRhos(int32_t model_id, double rho);
void dmLibSetKappas(int32_t model_id, double kappa);
void dmLibSetDelta(int32_t model_id, double delta);
void dmLibSetThetaForCascade(int32_t model_id, int32_t cascade_n, double theta);
void dmLibSetRhoForCascade(int32_t model_id, int32_t cascade_n, double rho);
void dmLibSetKappaForCascade(int32_t model_id, int32_t cascade_n, double kappa);
void dmLibSetAlphaForNode(int32_t model_id, int32_t node_id, double alpha);
void dmLibSetAlphaForPattern(int32_t model_id, int32_t alpha_n, double alpha);
double dmLibLoglikelyhood(int32_t model_id);
double dmLibLoglikelyhoodICM(int32_t model_id);
void dmLibSetGradientAlphasPatternLength(int32_t model_id, int32_t n_nodes);
void dmLibSetGradientAlphasPattern(int32_t model_id, int32_t node_id, int32_t node_n);
void dmLibGradientICM(int32_t model_id);
double dmLibGetGradient(int32_t model_id, int32_t var_number);
int32_t dmLibGetGradientLength(int32_t model_id);
void dmLibSetGradientValue(int32_t model_id, int32_t value_n, double value);
/*! @} */

#ifdef  __cplusplus
}
#endif

#endif  /* _DIFFUSION_H_INCLUDED_ */
