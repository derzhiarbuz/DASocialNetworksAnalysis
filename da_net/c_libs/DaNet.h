// Created by Gubanov Alexander (aka Derzhiarbuz) at 29.10.2020
// Contacts: derzhiarbuz@yandex.ru

/*!
@file
\~russian @brief Основные структуры, описывающие сеть и каскад
@details В этом файле содержатся разное, но если у типа есть постфикс Ptr (TypePtr), то он считается объектом.
Создавать его нужно при помощи функции new (newTypePtr()), а удалять с помощью функции delete (deleteTypePtr)

\~english @brief -
@details -
*/

#ifndef _DANET_H_INCLUDED_
#define _DANET_H_INCLUDED_

#ifdef  __cplusplus
extern "C" {
#endif

#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <malloc.h>
//#include <omp.h>

typedef struct Node_ Node;
typedef struct Network_ Network;
typedef struct ICase_ ICase;
typedef struct Cascade_ Cascade;
typedef struct Derivatives_ Derivatives;

/*! \~russian \addtogroup CascadeGroup Каскад
    @{
    \~english \addtogroup CascadeGroup Cascade
    @{
*/
typedef ICase* ICasePtr;
typedef Cascade* CascadePtr;
/*! @} */


/*! \~russian \addtogroup NodeGroup Сеть
    @{
    \~english \addtogroup NodeGroup Network
    @{
*/
typedef Node* NodePtr;
typedef Network* NetworkPtr;
/*!
\~russian @brief Узел сети
@details Структура описывает узел сети. Используется не сама по себе, в виде указателя (тип NodePtr)

\~english @brief -
@details -
*/
struct Node_ {
    int32_t id; ///<\~russian Идентификатор узла \~english Node identifier
    NodePtr *neigbors; ///<\~russian Массив указателей на соседей \~english Array of neighbors
    int32_t actual_degree; ///<\~russian Длина массива 'neighbors' \~english Length of 'neighbors' array
    /*!
    \~russian @brief Номинальная степень
    @details Часто возникает ситуация, когда для вычислений используется фрагмент реальной сети. В этом случае
    actual_degree может не соответствовать числу соседей вершины в реальной сети, тогда как для некоторых
    вычислений (например, в пороговой модели) требуется знать степень вершины в реальной сети.

    \~english @brief Nominal degree
    @details -
    */
    int32_t nominal_degree;
    void* userdata; ///<\~russian Произвольные данные \~english Pointer for user data
    void (*userdataDestructor)(void*); ///<\~russian Деструктор произвольных данных \~english User data destructor
};

/*!
\~russian @brief функция, создающая объект типа Node
@return указатель NodePtr на вновь созданный Node с инициализированными полями (нули и NULL)

\~english @brief function creates Node object
@return pointer NodePtr to newly allocated Node with pre-initialized values (zeros and NULLs)
*/
NodePtr newNode();
/*!
\~russian @brief функция, освобождающая память от объекта Node
@details в функции так же освобождается память, выделенная объектом Node в процессе работы
\param ptr указатель NodePtr на объект, от которого необходимо освободить память

\~english @brief -
@details -
*/
void freeNode(NodePtr node);
/*!
\~russian @brief функция сравнения двух узлов по их id
@details функция используется при сортировке массивов, содержащих объекты типа NodePtr,
а так же для дальнейшего дихотомического поиска элементов в массиве.
@param n1, n2 указатели на переменные типа NodePtr (имеют тип NodePtr*)

\~english @brief -
@details -
*/
int nodeCompare(const void *n1, const void *n2);
//NodePtr* getInNeighbors(NodePtr node);
//int32_t getInNeighborsN(NodePtr node);
//NodePtr* getOutNeighbors(NodePtr node);
//int32_t getOutNeighborsN(NodePtr node);

/*!
\~russian @brief Сеть
@details Структура описывает сеть. Используется не сама по себе, в виде указателя (тип NodePtr)

\~english @brief -
@details -
*/
struct Network_ {
    NodePtr *nodes; ///<\~russian Массив узлов \~english Array of nodes
    int32_t N; ///<\~russian Количество узлов \~english Number of nodes
};

NetworkPtr newNetwork();
/*!
\~russian @brief функция, инициализирующая сеть
@details в функции присваиваются начальные нулевые значения полям структуры. Вызывается при создании сети.
Проверок на выделенную память не осуществляется.
\param network указатель NetworkPtr на сеть, которую необходимо инициализировать

\~english @brief -
@details -
*/
void initNetwork(NetworkPtr network);
/*!
\~russian @brief функция, сбрасывающая содержимое сети
@details в функции освобождается динамическая память, выделенная сетью, а так же обнуляются значения всех полей
\param network указатель NetworkPtr на сеть, которую необходимо сбросить

\~english @brief -
@details -
*/
void clearNetwork(NetworkPtr network);
/*!
\~russian @brief функция, освобождающая память от сети
@details в функции так же осовобождается память, выделенная объектом Network во время работы
\param network указатель NetworkPtr на сеть, которую необходимо удалить

\~english @brief -
@details -
*/
void freeNetwork(NetworkPtr network);
/*!
\~russian @brief загрузка сети из файла
@details сеть хранится в бинарном файле в виде списка смежности. Каждый узел представляет из себя целочисленный четырёхбайтовый
идентификатор типа int32_t. Данные в файл записаны следующим образом (одна буква обозначает один байт, пробелы проставлены
для удобства:

NNNN MMMM PPPP XXXX XXXX ... XXXX MMMM PPPP XXXX XXXX ... XXXX ... MMMM PPPP XXXX XXXX ... XXXX

NNNN - количество узлов в сети. Затем идйт последовательность узлов.
Каждому узлу соответствует строка байт вида MMMM PPPP XXXX XXXX ... XXXX, где MMMM - количество соседей узла,
PPPP - идентификатор узла, XXXX XXXX ... XXXX - последовательность идентификаторов соседей (в количестве
MMMM штук). Таким образом, файл представляет из себя последовательность четырёхбайтовых целых.

\param network указатель NetworkPtr на сеть, в которую нужно загрузить данные
\param fname путь к файлу

\~english @brief -
@details -
*/
void loadNetworkFromFile(NetworkPtr network, const char * fpath);
/*!
\~russian @brief преобразование списка рёбер в бинарный файл с сетью
@details список рёбер ...

\param network указатель NetworkPtr на сеть, в которую нужно загрузить данные
\param fname путь к файлу

\~english @brief -
@details -
*/
void edgeListToBinary(const char * list_path, const char * network_path);
/*!
\~russian @brief функция, возвращающая узел сети по его идентификатору
@param network указатель NetworkPtr на сеть
@param id идентификатор узла
@return указатель на найденый узел или NULL

\~english @brief -
@details -
*/
NodePtr nodeForId(NetworkPtr network, int32_t id);
/*! @} */


/*! \~russian \addtogroup CascadeGroup Каскад
    @{
    \~english \addtogroup CascadeGroup Cascade
    @{
*/
/*!
\~russian @brief Случай заражения
@details Структура описывает один случай заражения, характеризующийся узлом и моментом времени

\~english @brief -
@details -
*/
struct ICase_ {
    NodePtr node; ///<\~russian Указатель на заразившийся узел \~english Pointer to node infected
    double time; ///<\~russian Момент заражения \~english The moment of infection
    int32_t index; ///<\~russian Индекс случая заражения в своём каскаде \~english Index of the infection case in it's cascade

    double value1;
    double value2;
};

ICasePtr newCase();
void freeCase(ICasePtr cas);
/*!
\~russian @brief функция сравнения двух случаев заражения по времени заражения (поле time)
@details функция используется при сортировке массивов, содержащих объекты типа ICase, по времени.
@param c1, c2 указатели на переменные типа ICase

\~english @brief -
@details -
*/
int ICaseCompare(const void *c1, const void *c2);

/*!
\~russian @brief Каскад
@details Структура описывает один каскад на сети. Каскад это последовательность случаев заражения в различные
моменты времени. Источник каскада - множество узлов, для которых заражение произошло в момент времени 0

\~english @brief -
@details -
*/
struct Cascade_ {
    ICasePtr *cases;  ///<\~russian Массив случаев заражения \~english Array of the moments of infection
    int32_t N_cases;  ///<\~russian Количество случаев заражения \~english Number of the moments of infection
    int32_t cases_length;
    /*!
    \~russian @brief Общее время наблюдения (должно быть не меньше, чем момент последнего случая заражения)
    \~english @brief Total observation time (should not be less than last infection case moment)
    */
    double observation_time;
    int32_t id;  ///<\~russian Идентификатор каскада \~english Cascade id
    int32_t from_id;  ///<\~russian Идентификатор источника каскада \~english Cascade source id
    NetworkPtr network;  ///<\~russian Сеть, на которой имеет место каскад \~english Cascade's network


    NodePtr *nodes_to_check; ///<\~russian Массив узлов, имеющих отношения к каскаду \~english Array of nodes considered as related to cascade
    int32_t N_nodes_to_check; ///<\~russian Длина массива nodes_to_check \~english Length of nodes_to_check array
};

CascadePtr newCascade();
void initCascade(CascadePtr cascade);
void freeCascade(CascadePtr cascade);

/*! @} */

/*!
\~russian @brief функция сравнения двух целых чисел
@details функция используется при сортировке массивов, содержащих целые числа, а также для дихотомического поиска.
@param c1, c2 указатели на переменные типа int_32t

\~english @brief -
@details -
*/
int int32Compare(const void *c1, const void *c2);

int32_t echo; ///<\~russian Флаг вывода в консоль \~english Console output flag

/*!
\~russian @brief ненужная функция
@details функция, не имеющая никакого смысла. Выводин в консоль "This is number a" и возвращает a*2.
Была первой функцией, с которой началось написание библиотеки,
и служила для проверки вызова библиотечных функций в Python. Осталась как реликт и музейный экспонат.
А если ты дочитал до этого места справки, о достойный, то заслужил перерыв и чай с печенькой.
@param a просто a
@return (просто a)*2

\~english @brief function you don't need
@details the function doesn't make any sense. It outputs "This is number a" in the console and returns a*2.
It was the first function from which the library began. It was used for testing the calling of library functions in Python.
It's left here as a relict and a museum exhibit. And you the one who've read the reference until this point,
you are the worf, and have deserved to take a break with tea and cookies.
@param a just a
@return (just a)*2
*/
int32_t hello_func(int32_t a);
/*!
\~russian @brief включение вывода в консоль
\~english @brief -
@details -
*/
void DADSEchoOn();
/*!
\~russian @brief выключение вывода в консоль
\~english @brief -
@details -
*/
void DADSEchoOff();
/*!
\~russian @brief форматированный вывод в консоль
@details по правде сказать, параметр может быть только один
@param text строка формата
@param ... параметры
\~english @brief -
@details -
*/
void DADSLog(char *text, ...);

Network und_network;

//**************************************************
//functions
//**************************************************
//utilities
void DADSInitNetwork();
void DADSClearNetwork();
NodePtr DADSNodeForId(int32_t id);
ICase DADSICaseForNodePtr(NodePtr node);
//loading
void DADSLoadNetworkFromFile(const char * fpath);

#ifdef  __cplusplus
}
#endif

#endif  /* _DANET_H_INCLUDED_ */
