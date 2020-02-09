# Created by Gubanov Alexander (aka Derzhiarbuz) at 06.02.2020
# Contacts: derzhiarbuz@gmail.com

import ctypes

if __name__ == '__main__':
    #libr = ctypes.windll.LoadLibrary('D:/Projects/Study/DASocialNetworkAnalysisCpp/Lib/DASocialNetworkAnalysisCpp.dll')
    libr = ctypes.cdll.LoadLibrary('D:/Projects/Study/DASocialNetworksAnalysis/C_libs/DADiffusionSimulation.dll')

    # Указываем, что функция возвращает int
    libr.hello_func.restype = ctypes.c_int32
    # Указываем, что функция принимает аргумент int
    libr.hello_func.argtypes = [ctypes.c_int32, ]

    libr.DADSLoadNetworkFromFile.argtypes = [ctypes.POINTER(ctypes.c_char), ]

    print('Return value: ' + str(libr.hello_func(342)))
    libr.DADSEchoOn()
    libr.DADSLoadNetworkFromFile('D:/BigData/Charity/Cascades/Komitet_Naziya_i_Svoboda_-17736722_26618u_network.dos'.encode('utf-8'))
#150437823 28082048 519339743