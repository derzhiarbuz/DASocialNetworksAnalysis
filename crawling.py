# Created by Gubanov Alexander (aka Derzhiarbuz) at 28.04.2019
# Contacts: derzhiarbuz@gmail.com

import da_connections_network_manager as nwm
import da_socnetworks_crawler as snc
import da_sna_data_manager as dm
from da_ic_network_manager import ICNetworkManager
from da_connections_network_manager import ConnectionsNetworkManager
from da_icascades_manager import CascadesManager
from da_information_conductivity import InformationConductivity


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

casman = CascadesManager(name='Zhest', base_dir='D:/BigData/Charity/Cascades/')
# casman.save_to_file()
casman.load_from_file()
# casman.schedule_crawl_posts_for_group(-65970801, 1, post_ids={845213})
# casman.schedule_crawl_posts_for_group(-145583685, 500)
# casman.continue_crawling()
# casman.save_to_file()
# casman.load_from_file()
# casman.schedule_crawl_underlying_network()
casman.underlying_net.schedule_crawl_ego_network(-65970801, deep=1, force=True)
# print(casman.crawl_plan)
casman.continue_crawling()
casman.save_to_file()
# casman.update_cascades(uselikes=False, usehiddens=False)
# casman.save_to_file()
#
# cond_net = InformationConductivity()
# cond_net.make_cascades_summary(casman.cascades)
# print(cond_net.cascades_network.links)
# print(cond_net.cascades_network.nodes)
# print(cond_net.cascades_network.nodes_attributes)
# cond_net.cascades_network.export_gexf('D:/BigData/Charity/Cascades/Dobroserd500Summary.gexf', drop_singletones=True)