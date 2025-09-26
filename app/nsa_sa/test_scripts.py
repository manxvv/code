import os
import importlib
from datetime import datetime
import pandas as pd
from USID import USID
from custom_log import Custom_Log

current_time = datetime.now().strftime('%m%d%Y_%H%M%S')
site_name = 'Script_09_26_2025'
circle, enm = 'AP', 'enmap1'
nsa_sa_path = r'/Users/aj_mac/Documents/Atel/server/code/app/nsa_sa'
base_dir = r'/Users/aj_mac/Documents/Atel/Inputs'
base_dir = os.path.join(r'/Users/aj_mac/Documents/Atel/Inputs', site_name)
log_file = os.path.join(base_dir, F'{site_name}_{current_time}.log')
para_file = os.path.join(base_dir, 'Scripts.txt')
site_file = os.path.join(base_dir, 'site_list.xlsx')

custom_log = Custom_Log(log_file=log_file)
usid = USID(nsa_sa_path=nsa_sa_path, base_dir=base_dir, custom_log=custom_log, para_file=para_file, site_file=site_file, circle=circle, enm=enm)
modules = ['aa_01_5qiTable_BWP', 'aa_02_MOs_Create', 'aa_03_Lock_NR', 'aa_04_Parameter', 'aa_05_UnLock_NR']
print(base_dir)

for node in usid.nodes:
    for module in modules:
        print(F'{node} --- {module}')
        self = getattr(importlib.import_module(F'nsa_sa.{module}'), module)(usid=usid, node=node)
        self.run()

# Write a command Files and Process docs
if len(usid.nodes) > 0:
    print(F'{usid.nodes} --- aa_Command')
    node = usid.nodes[0]
    self = getattr(importlib.import_module(F'nsa_sa.aa_Command'), 'aa_Command')(usid=usid, node=node)
    self.run()
usid.df_gpl = pd.DataFrame(usid.gpl_list)
usid.save_different_dataframe(current_time=current_time)
print('OK')
print(F'cmedit get {usid.log_mos} --dynamic')
