# Created by Gubanov Alexander (aka Derzhiarbuz) at 06.02.2020
# Contacts: derzhiarbuz@gmail.com

from sys import platform
import ctypes
import pathlib
import inspect
from da_icascades_manager import CascadesManager


class DiffusionEstimator(object):

    __instance = None

    def __init__(self, echo=False):
        current_path = pathlib.Path(inspect.stack()[0].filename).parent
        if platform == 'win32' or platform == 'win64':
            self.libr = ctypes.cdll.LoadLibrary(str(current_path)+'/c_libs/DADiffusionSimulation.dll')
        elif platform == 'linux' or platform == 'linux2':
            self.libr = ctypes.cdll.LoadLibrary(str(current_path) + '/c_libs/DADiffusionSimulation.dll')
        self.libr.DADSLoadNetworkFromFile.argtypes = [ctypes.POINTER(ctypes.c_char), ]
        self.libr.DADSSetMetaForNode.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ]
        self.libr.DADSSetNumberOfInfections.argtypes = [ctypes.c_int32]
        self.libr.DADSAddInfectionCaseForInfection.argtypes = [ctypes.c_int32, ctypes.c_double, ctypes.c_int32, ]
        self.libr.DADSAddInfectionCase.argtypes = [ctypes.c_int32, ctypes.c_double, ]
        self.libr.DADSLogLikelyhoodTKDR.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                                    ctypes.c_double, ctypes.c_double, ]
        self.libr.DADSLogLikelyhoodTKDR.restype = ctypes.c_double
        self.libr.DADSLogLikelyhoodKDR.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ]
        self.libr.DADSLogLikelyhoodKDR.restype = ctypes.c_double
        self.libr.DADSLogLikelyhoodByNodeTheta.argtypes = [ctypes.c_double, ctypes.c_int32, ctypes.c_double,
                                                           ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                                           ctypes.c_double, ]
        self.libr.DADSLogLikelyhoodByNodeTheta.restype = ctypes.c_double
        self.libr.DADSLogLikelyhoodTKDRByInfectionsEnsemble.argtypes = [ctypes.c_double, ctypes.c_double,
                                                                        ctypes.c_double, ctypes.c_double,
                                                                        ctypes.c_double, ]
        self.libr.DADSLogLikelyhoodTKDRByInfectionsEnsemble.restype = ctypes.c_double
        self.libr.DADSCalculateDerivatives.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                                       ctypes.c_double, ctypes.c_double, ]
        self.libr.DADSDLogLikelyhoodDthetaForId.argtypes = [ctypes.c_int32]
        self.libr.DADSDLogLikelyhoodDthetaForId.restype = ctypes.c_double
        if echo:
            self.echo_on()

    #def __del__(self):
    #    self.libr.DADSClearNetwork()

    @classmethod
    def default(cls, echo=False):
        if not cls.__instance:
            cls.__instance = DiffusionEstimator(echo)
        return cls.__instance

    def echo_on(self):
        self.libr.DADSEchoOn()

    def echo_off(self):
        self.libr.DADSEchoOn()

    def load_network_from_file(self, fname: str):
        self.libr.DADSLoadNetworkFromFile(fname.encode('utf-8'))

    def set_counters(self, counters: dict):
        for key, value in counters.items():
            self.libr.DADSSetMetaForNode(key, value[0], value[1])

    def purify_network(self):
        self.libr.DADSPurifyNetwork()

    def add_outcome(self, outcome: dict):
        for key, value in outcome.items():
            self.libr.DADSAddInfectionCase(key, value)

    def add_outcomes(self, outcomes: list):
        self.libr.DADSSetNumberOfInfections(len(outcomes))
        for i in range(len(outcomes)):
            outcome = outcomes[i]
            for key, value in outcome.items():
                self.libr.DADSAddInfectionCaseForInfection(key, value, i)

    def prepare_for_estimation(self):
        self.libr.DADSPrepareForEstimation()

    def load_network(self, fname: str, counters: dict, outcome: dict):
        self.load_network_from_file(fname)
        if counters:
            self.set_counters(counters)
        self.purify_network()
        self.add_outcome(outcome)
        self.prepare_for_estimation()

    def load_network_inf_ensemble(self, fname: str, counters: dict, outcomes: list):
        self.load_network_from_file(fname)
        if counters:
            self.set_counters(counters)
        self.purify_network()
        self.add_outcomes(outcomes)
        self.prepare_for_estimation()

    def loglikelyhood(self, theta, confirm, decay, relic, observe_time=-1.):
        return self.libr.DADSLogLikelyhoodTKDR(theta, confirm, decay, relic, observe_time)

    def loglikelyhood_ensemble(self, theta, confirm, decay, relic, observe_time=-1):
        return self.libr.DADSLogLikelyhoodTKDRByInfectionsEnsemble(theta, confirm, decay, relic, observe_time)

    def loglikelyhood_by_node_theta(self, node_theta, node_id, theta, confirm, decay, relic, observe_time=-1):
        return self.libr.DADSLogLikelyhoodByNodeTheta(node_theta, node_id, theta, confirm, decay, relic
                                                      , observe_time)

    def thetas_derivatives(self, theta, confirm, decay, relic, ids, observe_time):
        self.libr.DADSCalculateDerivatives(theta, confirm, decay, relic, observe_time)
        derivatives = {}
        for id in ids:
            derivatives[id] = self.libr.DADSDLogLikelyhoodDthetaForId(id)
        return derivatives



if __name__ == '__main__':
    casman = CascadesManager(name='Zashitim_taigu_-164443025_8726_8021_6846', base_dir='D:/BigData/Charity/Cascades/')
    casman.load_from_file()
    cascade = casman.get_cascade_by_id(8726)
    min_delay = cascade.get_minimum_delay()
    outcome = cascade.get_outcome(normalization_factor=min_delay)
    counters = casman.underlying_net.counters_meta

    estmtr = DiffusionEstimator(True)
    estmtr.load_network('D:/BigData/Charity/Cascades/Zashitim_taigu_-164443025_8726_8021_6846u_network.dos',
                        counters,
                        outcome)
    for i in range(10):
        ll = estmtr.loglikelyhood(0.0000001, 0.5, 0.00001, 0.00000001)
        print(str(i) + '  ' + str(ll))

#150437823 28082048 519339743
