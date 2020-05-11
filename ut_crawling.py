# Created by Gubanov Alexander (aka Derzhiarbuz) at 28.04.2019
# Contacts: derzhiarbuz@gmail.com

import da_connections_network_manager as nwm
import da_socnetworks_crawler as snc
import da_sna_data_manager as dm
from da_ic_network_manager import ICNetworkManager
from da_connections_network_manager import ConnectionsNetworkManager
from da_icascades_manager import CascadesManager
from da_information_conductivity import InformationConductivity
import math
from Statistics.da_diffusion_simulation import Simulator
import numpy as np
import matplotlib.pyplot as plt
import Statistics.da_diffusion_estimation as est

import da_socnetworks_crawler as crowler


# mngr = ConnectionsNetworkManager(name='test_manager')
# mngr.load_from_file()
# mngr.schedule_crawl_ego_network(22793365, deep=1)
# mngr.schedule_load_nodes_meta()
# mngr.continue_crawling()
# mngr.save_to_file()

# print(len(mngr.network.nodes))
# print(len(mngr.crawled_nodes))

# ids = {-174104490, -34797321, -36498255, -78711486}
# res = snc.get_vk_groups(ids)
# print(res)

# res = snc.get_posts_by_id(-65970801, {845213, 814932})
# print(res)

# mngr.load_from_file()
# print(mngr.network.nodes)

# icnetm = ICNetworkManager(name='post_-56176996_16343', base_dir='D:/BigData/Charity/Cascades/')
# icnetm.schedule_crawl_post_from_source(-56176996, 16343)
# icnetm.continue_crawling()
# icnetm.save_to_file()

# icnetm.load_from_file()
# print(len(icnetm.hiddens))
# print(len(icnetm.likers))
# print(len(icnetm.posters))
# print(icnetm.post_meta)

# -73225212 - PomogatLegko
# -56176996 - WorldVita
# -30800293 - RussianBirch
# -145583685 - Dobroserd
# -65970801 - Zhest Tomska

# Komanda_Navalny_-140764628_8377_8554_8425
# Zashitim_taigu_-164443025_8726_8021_6846
# Komitet_Naziya_i_Svoboda_-17736722_26618
# Navalny_live_-150565101_51320
# Tomsk_v_zaschitu_-192308068_9
# Tomsk_v_zaschitu_-192308068_all


# casman = CascadesManager(name='Tomsk_v_zaschitu_-192308068_all', base_dir='D:/BigData/Charity/Cascades/')
# casman.save_to_file()
# casman.load_from_file()
# casman.schedule_crawl_posts_for_group(-192308068, 1, post_ids={9})
# casman.schedule_crawl_posts_for_group(-192308068, 500)
# casman.continue_crawling()
# casman.save_to_file()
# # casman.load_from_file()
# casman.schedule_crawl_underlying_network()
# # casman.underlying_net.schedule_crawl_ego_network(-65970801, deep=1, force=True)
# # print(casman.crawl_plan)
# casman.continue_crawling()
# casman.save_to_file()
# casman.update_cascades(uselikes=False, usehiddens=False)
# casman.save_to_file()
#

# cond_net = InformationConductivity()
# cond_net.make_cascades_summary(casman.cascades)
# print(cond_net.cascades_network.links)
# print(cond_net.cascades_network.nodes)
# print(cond_net.cascades_network.nodes_attributes)
# cond_net.cascades_network.export_gexf('D:/BigData/Charity/Cascades/Tomsk_v_zaschitu_-192308068_9.gexf', drop_singletones=False)
#
# i = 0
# casman.update_cascades(uselikes=False, usehiddens=False, logdyn=False, start_from_zero=False)
# casman.write_diffusion_speed_csv('D:/BigData/Charity/Cascades/Zashitim_taigu_-164443025_8726.csv',
#                                  8726, derivative=True)

#loading counters
###casman.underlying_net.counters_meta = {}
# casman.underlying_net.crawl_plan = []
# casman.underlying_net.schedule_load_counters_meta()
# casman.continue_crawling()
# casman.save_to_file()


#8726: 1615.7052609591547   [1.13705951e-06 1.74581006e-03 3.25539755e-03 5.87984155e-09] //садим
#8021: 1183.585359582195   [1.00457047e-06 3.01659167e-03 2.99908438e-03 5.07020291e-09] //уничтожают
#6846: 4495.705121637081   [1.00019217e-12 3.61779381e-01 4.07895457e-06 1.24224204e-07]


# for cascade in casman.cascades:
#     print(cascade.post_meta)
#     if cascade.post_meta['postinfo']['id'] == 8726:
#
#         #### estimating parameters #####
#         min_delay = cascade.get_minimum_delay()
#         outcome = cascade.get_outcome(normalization_factor=min_delay)
#         print('minimum delay: ' + str(min_delay))
        # print(outcome)
        # print(sorted(outcome.values()))
        # print(len(casman.underlying_net.network.nodes))
        #
        # print(len(casman.underlying_net.crawled_nodes))
        # print(len(casman.underlying_net.network.nodes))
        # print(len(casman.underlying_net.counters_meta))
        # casman.underlying_net.crawl_plan = []
        # casman.underlying_net.schedule_load_counters_meta()
        # casman.continue_crawling()
        # casman.save_to_file()

        # thetas = np.arange(0.000014, 0.000020, 0.0000009)
        # relics = np.arange(0.00000001, 0.0000002, 0.00000003)
        # relics = np.array([1e-08])
        # decays = np.arange(0.0001, 0.005, 0.001)
        # decays = np.array([8.5e-04])
        # confirms = np.arange(-0.95, 1.1, 0.2)
        # print(thetas)
        # print(decays)
        # ests = {'theta': .0, 'relic': .0, 'halflife': .0}
        # ps = np.zeros((len(relics), len(thetas), len(decays), len(confirms)))
        # max_log = -99999999.
        # N = len(thetas) * len(relics) * len(decays) * len(confirms)
        # n = 0
        # relic_est_i = 0
        # decay_est_k = 0
        # for j in range(len(thetas)):
        #     for i in range(len(relics)):
        #         for k in range(len(decays)):
        #             for l in range(len(confirms)):
        #                 n+=1
        #                 print(str(n) + ' of ' + str(N))
        #                 pest = Simulator.estimate_SI_relic_decay_confirm_continuous(underlying=casman.underlying_net.network,
        #                                                                     outcome=outcome,
        #                                                                     theta=thetas[j],
        #                                                                     relic=relics[i],
        #                                                                     decay=decays[k],
        #                                                                     confirm=confirms[l],
        #                                                                     confirm_drop=0.1,
        #                                                                     initials={-17736722}, tmax=8384, echo=False,
        #                                                                             leafs_degrees=casman.underlying_net.uncrawled_meta)
        #                 print(pest)
        #                 if pest > max_log:
        #                     max_log = pest
        #                     relic_est_i = i
        #                     decay_est_k = k
        #                     ests['theta'] = thetas[j]
        #                     ests['relic'] = relics[i]
        #                     ests['decay'] = decays[k]
        #                     ests['confirm'] = confirms[l]
        #                 ps[i][j][k][l] = pest
        # max_log -= 300
        # np.save('test_halflife_5.np', ps)
        # ps = np.load('test_halflife_5.np.npy')
        # print(ests)
        # z = np.zeros((len(confirms), len(thetas)))
        # print(z.shape)
        # print(ps[0])
        # for j in range(len(thetas)):
        #     for l in range(len(confirms)):
        #         if ps[relic_est_i][j][decay_est_k][l] > max_log:
        #             max_log = ps[relic_est_i][j][decay_est_k][l]
        # max_log -= 300
        # for j in range(len(thetas)):
        #     for l in range(len(confirms)):
        #         if ps[relic_est_i][j][decay_est_k][l] >= max_log:
        #             z[l][j] = math.exp(ps[relic_est_i][j][decay_est_k][l] - max_log)
        #         else:
        #             z[l][j] = .0
        # print(z)
        # plt.figure(figsize=(5, 5))
        # plt.xlabel('$\\theta$ (virulence)')
        # plt.ylabel('$\\rho$ (background)')
        # plt.contourf(thetas, confirms, z, levels=15)
        # plt.show()


        #### export graph to gefi/json #####
#        cascade.network.export_gexf('D:/BigData/Charity/Cascades/Navalny_live_-150565101_51320.gexf',
#                                    dynamic=True)
        #cascade.network.export_json('D:/BigData/Charity/Cascades/Zashitim_taigu_-164443025_8021.json')
#     print(str(len(cascade.posters)) + " " + str(len(cascade.hiddens)) + " " + str(len(cascade.likers)))
#     print(cascade.network.nodes.keys())
#     likes = set()
#     for poster in cascade.posters.values():
#         print(poster)
#         likes |= poster['likes']
#     print(len(likes))
#     mislikes = likes - set(cascade.posters.keys()) - cascade.likers - cascade.hiddens
#     print(mislikes)
#     print(len(mislikes))
#     print(cascade.likers)
#     # if 349224610 in cascade.likers:
#     #     print('She is a liker!')
#     # if 349224610 in cascade.hiddens:
#     #     print('She is a hidden!')
#     post = cascade.post_meta
#     # print(post['text'])
#     # content_md5 = cascade.post_meta['md5']
#     # search_string = cascade.post_meta['search_string']
#     # source_date = cascade.post_meta['postinfo']['date']
#     # new_post_info = crowler.find_post_on_wall(74398255, content_md5, search_string, -164443025,
#     #                                         source_date, wallsearch=True,
#     #                                         use_cache=False, original_id=8726)
#     # print(new_post_info)
#     i += 1

# print("piu")
# casman.load_from_file(crowled_only=True)
# print("piu-piu")
# # casman.write_gexf(casman.base_dir+"/"+casman._name+".gexf")
# casman.write_stat_csv(casman.base_dir+"/"+casman._name+".csv")
# casman.write_diffusion_speed_csv(casman.base_dir+"/"+casman._name+"_speed.csv")

#1742083f38846b5db117dc2f3a609bd5 - sobaka plachet
#id 166967

# f = open('D:/BigData/Charity/sobaka.csv', 'rt')
# times = []
# for line in f.readlines():
#     parts = line.split('[')
#     if len(parts) > 1:
#         num = parts[1].split(',')[0]
#         times.append(math.exp(float(num)))
# f.close()
# times.sort()
# print(times)
# f = open('D:/BigData/Charity/sobaka_times_drv.csv', 'wt')
# i = 1
# t = 0
# dt = 14400
# for time in times:
#     if time >= t and time < t + dt:
#         i += 1
#     else:
#         f.write(str(t) + ',' + str(i) + '\n')
#         i = 1
#         t = (time // dt) * dt
# f.close()

plt.subplot(1, 2, 1)
plt.bar(x=[-1, 0, 1], height=[0, 0, 5])
plt.subplot(1, 2, 2)
plt.bar(x=[-1, 0, 1], height=[100, 0, 105])
plt.show()