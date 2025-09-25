import os
import importlib
from datetime import datetime
import pandas as pd
from AuditUSID import AuditUSID
from custom_log import Custom_Log

current_time = datetime.now().strftime('%m%d%Y_%H%M%S')
site_name = 'Audit_09_24_2025'
circle = 'AP'
nsa_sa_path = r'/Users/aj_mac/Documents/Atel/server/code/app/gpl_audit'
file_path = r'/Users/aj_mac/Documents/Atel/Inputs'
base_dir = os.path.join(file_path, site_name)
# base_dir = os.path.join(file_path, site_name)
log_file = os.path.join(base_dir,  F'{site_name}_{current_time}.log')
para_file = os.path.join(base_dir, F'pre_dump_{circle}.txt')
para_file = [
    r'/Users/aj_mac/Documents/Atel/Inputs/Audit_09_24_2025/1.txt',
    r'/Users/aj_mac/Documents/Atel/Inputs/Audit_09_24_2025/2.txt',
    r'/Users/aj_mac/Documents/Atel/Inputs/Audit_09_24_2025/3.txt',
    r'/Users/aj_mac/Documents/Atel/Inputs/Audit_09_24_2025/4.txt'
]

site_file = os.path.join(base_dir, 'site_list.xlsx')

custom_log = Custom_Log(log_file=log_file)
audit_usid = AuditUSID(nsa_sa_path=nsa_sa_path, base_dir=base_dir, custom_log=custom_log,
                       para_file=para_file, site_file=site_file, circle=circle)
modules = ['aa_01_NR_Parameter', 'aa_02_LTE_Parameter']
# , 'aa_01_LTE_Parameter'
print(base_dir)
for node in list(audit_usid.df_site.node.unique()):
    for module in modules:
        self = getattr(importlib.import_module(F'{module}'), module)(audit_usid=audit_usid, node=node)
        self.run()

audit_usid.df_gpl = pd.DataFrame(audit_usid.gpl_list)
audit_usid.save_logic_dataframe(current_time=current_time)
audit_usid.save_audit_dataframe(current_time=current_time)
print('OK')
print(base_dir)
#
# git stash
# git pull
# pm2 logs 0