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


casman = CascadesManager(name='Komitet_Naziya_i_Svoboda_-17736722_26618', base_dir='D:/BigData/Charity/Cascades/')
# casman.save_to_file()
casman.load_from_file()
# casman.schedule_crawl_posts_for_group(-150565101, 1, post_ids={51320})
# # casman.schedule_crawl_posts_for_group(-145583685, 500)
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
# cond_net.cascades_network.export_gexf('D:/BigData/Charity/Cascades/Komanda_Navalny_-140764628_8377_8554_8425.gexf', drop_singletones=False)
#
# i = 0
casman.update_cascades(uselikes=False, usehiddens=False, logdyn=False, start_from_zero=False)
# casman.write_diffusion_speed_csv('D:/BigData/Charity/Cascades/Zashitim_taigu_-164443025_8726.csv',
#                                  8726, derivative=True)
for cascade in casman.cascades:
    print(cascade.post_meta)
    if cascade.post_meta['postinfo']['id'] == 26618:
        #### estimating parameters #####
        min_delay = cascade.get_minimum_delay()
        outcome = cascade.get_outcome(normalization_factor=min_delay)
        print('minimum delay: ' + str(min_delay))
        print(outcome)
        print(sorted(outcome.values()))
        print(len(casman.underlying_net.network.nodes))
        pest = Simulator.estimate_SI_relic(underlying=casman.underlying_net.network,
                                           outcome=outcome,
                                           theta=0.001,
                                           relic=0.001,
                                           initials={-17736722}, tmax=8384, dt=1, echo=True)
        print(pest)
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
