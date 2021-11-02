# Created by Gubanov Alexander (aka Derzhiarbuz) at 06.11.2020
# Contacts: derzhiarbuz@gmail.com

from sys import platform
import ctypes
import pathlib
import inspect


class DiffusionModel(object):

    __instance = None

    def __init__(self, echo=False):
        current_path = pathlib.Path(inspect.stack()[0].filename).parent
        path = str(current_path) + '\\c_libs\\DADiffusionSimulation.dll'
        path = 'D:/Projects/Study/DASocialNetworksAnalysis/da_net/c_libs/danet.dll'
        print(path)
        if platform == 'win32' or platform == 'win64':
            self.libr = ctypes.cdll.LoadLibrary(path)
        elif platform == 'linux' or platform == 'linux2':
            self.libr = ctypes.CDLL(str(current_path) + '/c_libs/libdanet.so')
        self.libr = ctypes.cdll.LoadLibrary(path)

        self.libr.dmLibNewDiffusionModel.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int32, ]
        self.libr.dmLibNewDiffusionModel.restype = ctypes.c_int32

        self.libr.dmLibDeleteDiffusionModel.argtypes = [ctypes.c_int32, ]

        self.libr.dmLibSetNCasesForCascade.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ]

        self.libr.dmLibSetObservationTimeForCascade.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_double, ]

        self.libr.dmLibAddCase.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_double, ]

        self.libr.dmLibSetThetas.argtypes = [ctypes.c_int32, ctypes.c_double, ]

        self.libr.dmLibSetRhos.argtypes = [ctypes.c_int32, ctypes.c_double, ]

        self.libr.dmLibSetKappas.argtypes = [ctypes.c_int32, ctypes.c_double, ]

        self.libr.dmLibSetDelta.argtypes = [ctypes.c_int32, ctypes.c_double, ]

        self.libr.dmLibSetThetaForCascade.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_double, ]

        self.libr.dmLibSetRhoForCascade.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_double, ]

        self.libr.dmLibSetKappaForCascade.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_double, ]

        self.libr.dmLibSetAlphaForNode.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_double, ]
        self.libr.dmLibSetAlphaForPattern.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_double]

        self.libr.dmLibLoglikelyhood.argtypes = [ctypes.c_int32]
        self.libr.dmLibLoglikelyhood.restype = ctypes.c_double

        self.libr.dmLibLoglikelyhoodICM.argtypes = [ctypes.c_int32]
        self.libr.dmLibLoglikelyhoodICM.restype = ctypes.c_double

        self.libr.dmLibSetGradientAlphasPatternLength.argtypes = [ctypes.c_int32, ctypes.c_int32]

        self.libr.dmLibSetGradientAlphasPattern.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]

        self.libr.dmLibGradientICM.argtypes = [ctypes.c_int32]

        self.libr.dmLibGetGradient.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.libr.dmLibGetGradient.restype = ctypes.c_double

        self.libr.dmLibGetGradientLength.restype = ctypes.c_int32

        self.libr.dmLibSetGradientValue.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_double]

        if echo:
            self.echo_on()


    @classmethod
    def default(cls, echo=False):
        if not cls.__instance:
            cls.__instance = DiffusionModel(echo)
        return cls.__instance

    def echo_on(self):
        self.libr.DADSEchoOn()

    def echo_off(self):
        self.libr.DADSEchoOn()

    def new_model(self, fname: str, n_cascades: int):
        return self.libr.dmLibNewDiffusionModel(fname.encode('utf-8'), n_cascades)

    def delete_model(self, model_id: int):
        self.libr.dmLibDeleteDiffusionModel(model_id)

    def set_ncases_for_cascade(self, model_id: int, cascade_n: int, n_cases: int):
        self.libr.dmLibSetNCasesForCascade(model_id, cascade_n, n_cases)

    def set_observation_time_for_cascade(self, model_id: int, cascade_n: int, observation_time: float):
        self.libr.dmLibSetObservationTimeForCascade(model_id, cascade_n, observation_time)

    def add_case(self, model_id: int, cascade_n: int, node_id: int, case_time: float):
        self.libr.dmLibAddCase(model_id, cascade_n, node_id, case_time)

    def set_thetas(self, model_id: int, theta: float):
        self.libr.dmLibSetThetas(model_id, theta)

    def set_rhos(self, model_id: int, rho: float):
        self.libr.dmLibSetRhos(model_id, rho)

    def set_kappas(self, model_id: int, kappa: float):
        self.libr.dmLibSetKappas(model_id, kappa)

    def set_delta(self, model_id: int, delta: float):
        self.libr.dmLibSetDelta(model_id, delta)

    def set_theta_for_cascade(self, model_id: int, cascade_n: int, theta: float):
        self.libr.dmLibSetThetaForCascade(model_id, cascade_n, theta)

    def set_rho_for_cascade(self, model_id: int, cascade_n: int, rho: float):
        self.libr.dmLibSetRhoForCascade(model_id, cascade_n, rho)

    def set_kappa_for_cascade(self, model_id: int, cascade_n: int, kappa: float):
        self.libr.dmLibSetKappaForCascade(model_id, cascade_n, kappa)

    def set_alpha_for_node(self, model_id: int, node_id: int, alpha: float):
        self.libr.dmLibSetAlphaForNode(model_id, node_id, alpha)

    def set_alpha_for_pattern(self, model_id: int, alpha_n: int, alpha: float):
        self.libr.dmLibSetAlphaForNode(model_id, alpha_n, alpha)

    def loglikelyhood(self, model_id: int):
        return  self.libr.dmLibLoglikelyhood(model_id)

    def loglikelyhoodICM_(self, model_id: int):
        return  self.libr.dmLibLoglikelyhoodICM(model_id)

    def loglikelyhoodTRD(self, model_id: int, theta: float, rho: float, delta: float):
        self.set_thetas(model_id, theta)
        self.set_rhos(model_id, rho)
        self.set_delta(model_id, delta)
        return self.loglikelyhood(model_id)

    def loglikelyhoodTsRsD(self, model_id: int, thetas: list, rhos: list, delta: float):
        for i in range(len(thetas)):
            self.set_theta_for_cascade(model_id, i, thetas[i])
            self.set_rho_for_cascade(model_id, i, rhos[i])
        self.set_delta(model_id, delta)
        return self.loglikelyhood(model_id)

    def loglikelyhoodTsRsKsD(self, model_id: int, thetas: list, rhos: list, kappas: list, delta: float):
        for i in range(len(thetas)):
            self.set_theta_for_cascade(model_id, i, thetas[i])
            self.set_rho_for_cascade(model_id, i, rhos[i])
            self.set_kappa_for_cascade(model_id, i, kappas[i])
        self.set_delta(model_id, delta)
        return self.loglikelyhood(model_id)

    def loglikelyhoodICM(self, model_id: int, theta: float, rho: float):
        self.set_thetas(model_id, theta)
        self.set_rhos(model_id, rho)
        return self.loglikelyhoodICM_(model_id)

    def loglikelyhoodICM_pattern(self, model_id: int, thetas=None, rhos=None, alphas=None, x=None):
        if x is not None:
            for i in range(len(x)):
                self.libr.dmLibSetGradientValue(model_id, i, x[i])
        else:
            if thetas:
                for i in range(len(thetas)):
                    self.set_theta_for_cascade(model_id, i, thetas[i])
            if rhos:
                for i in range(len(rhos)):
                    self.set_rho_for_cascade(model_id, i, rhos[i])
            if alphas:
                for i in range(len(alphas)):
                    self.set_alpha_for_pattern(model_id, i, alphas[i])
        return self.loglikelyhoodICM_(model_id)

    def gradientICM_pattern(self, model_id: int, x: list):
        for i in range(len(x)):
            self.libr.dmLibSetGradientValue(model_id, i, x[i])
        self.libr.dmLibGradientICM(model_id)
        result = []
        for i in range(len(x)):
            val = self.libr.dmLibGetGradient(model_id, i)
            result.append(val)
        return result

    def testParallel(self):
        self.libr.testLikelyhood()


    def setAlphasPattern(self, model_id: int, node_ids):
        print('LEN ' + str(len(node_ids)))
        self.libr.dmLibSetGradientAlphasPatternLength(model_id, len(node_ids))
        for i in range(len(node_ids)):
            self.libr.dmLibSetGradientAlphasPattern(model_id, node_ids[i], i)
        print('PATTERN ' + str(self.libr.dmLibGetGradientLength(model_id)))

    def gradientICM(self, model_id: int, thetas: list, rhos: list, alphas: list):
        point = thetas + rhos + alphas
        for i in range(len(point)):
            self.libr.dmLibSetGradientValue(model_id, i, point[i])
        self.libr.dmLibGradientICM(model_id)
        result = []
        for i in range(len(point)):
            val = self.libr.dmLibGetGradient(model_id, i)
            result.append(val)
        dthetas = result[0:len(thetas)]
        drhos = result[len(thetas):(len(thetas)+len(rhos))]
        dalphas = result[(len(thetas)+len(rhos)):]
        return {'dthetas': dthetas, 'drhos': drhos, 'dalphas': dalphas}