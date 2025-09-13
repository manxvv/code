from USID import USID
from datetime import datetime


from USID import USID
import os
import sys
import django
import importlib
from datetime import datetime
from common_func.custom_log import Custom_Log
sys.path.append(r'C:\Project\stool\Airtel\airtel')
sys.path.append(r'C:\Project\stool\Airtel\airtel\nsa_sa')
curr_dt = datetime.now().strftime('%Y%m%d%H%M%S')
site_name = 'NEW'
base_dir = os.path.join(r'C:\Project\Input\Airtel\test', site_name)
log_file = os.path.join(base_dir, F'{site_name}_{curr_dt}.log')
custom_log = Custom_Log(log_file=log_file)
print(base_dir)
circle = 'ROTN'
enm = 'ENM1'
para_file = r'C:\\Project\Input\Airtel\test\NEW\Paraemeter.txt'
site_list = r'C:\Project\Input\Airtel\test\NEW\Paraemeter.txt'

# def nsa_sa_script(base_dir: str, log_file: str, site_list: str, circle: str, enm: str) -> str:
#     from USID import USID
#     usid = USID(base_dir=base_dir, custom_log=custom_log, para_file=para_file, site_list=site_list, circle=circle, enm=enm)
#     # Write Scripts
#     modules = ['aa_01_5qiTable_BWP', 'aa_02_MOs_Create', 'aa_03_Lock_NR', 'aa_04_Parameter', 'aa_05_UnLock_NR']
#     for node in usid.nodes:
#         for module in modules:
#             self = getattr(importlib.import_module(F'airtel.nsa_sa.{module}'), module)(usid=usid, node=node)
#             self.run()
#     # Write a command Files and Process docs
#     if len(usid.nodes) > 0:
#         node = usid.nodes[0]
#         self = getattr(importlib.import_module(F'airtel.nsa_sa.aa_Command'), 'aa_Command')(usid=usid, node=node)
#         self.run()


usid = USID(base_dir=base_dir, custom_log=custom_log, para_file=para_file, site_list=site_list, circle=circle, enm=enm)
modules = ['aa_01_5qiTable_BWP', 'aa_02_MOs_Create', 'aa_03_Lock_NR', 'aa_04_Parameter', 'aa_05_UnLock_NR']
# aa_Command
for node in usid.nodes:
    for module in modules:
        # print(module)
        self = getattr(importlib.import_module(F'airtel.nsa_sa.{module}'), module)(usid=usid, node=node)
        self.run()
# Write a command Files and Process docs
if len(usid.nodes) > 0:
    self = getattr(importlib.import_module(F'airtel.nsa_sa.aa_Command'), 'aa_Command')(usid=usid, node=node)
    self.run()




bb = ''
for i in usid.dump_list:
    bb += F';{i}.<w>'
print(usid.dump_list)
print(F'cmedit get {";".join(usid.nodes)} {bb[1:]} --list')
print(F'cmedit get {";".join(usid.nodes)} {bb[1:]} --dynamic')
