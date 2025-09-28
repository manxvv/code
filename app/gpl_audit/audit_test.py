import os
import importlib
from datetime import datetime
import pandas as pd
from AuditUSID import AuditUSID
from AuditReport import AuditReport
from custom_log import Custom_Log

current_time = datetime.now().strftime('%m%d%Y_%H%M%S')
site_name = 'Audit_09_27_2025'
circle = 'AP'
nsa_sa_path = r'/Users/aj_mac/Documents/Atel/server/code/app/gpl_audit'
file_path = r'/Users/aj_mac/Documents/Atel/Inputs'
base_dir = os.path.join(file_path, site_name)
para_file = [os.path.join(base_dir, _) for _ in os.listdir(base_dir) if _.endswith(".txt")]
site_file = os.path.join(base_dir, 'site_list.xlsx')
log_file = os.path.join(base_dir,  F'{site_name}_{current_time}.log')
print(para_file)
custom_log = Custom_Log(log_file=log_file)
a_usid = AuditUSID(nsa_sa_path=nsa_sa_path, base_dir=base_dir, custom_log=custom_log,
                   para_file=para_file, site_file=site_file, circle=circle)
for node in list(a_usid.df_site.node.unique()):
    a_usid.custom_log.log.info(F'Audit Started for {node}')
    self = getattr(importlib.import_module('Audit'), 'Audit')(a_usid=a_usid, node=node)
    self.run()
    self.run_all_parameters_audit()

AuditReport(a_usid=a_usid)
a_usid.custom_log.log.info(F'Audit Completed!!!')
a_usid.custom_log.release()

print(base_dir)
# a_usid.df_gpl = pd.DataFrame(a_usid.gpl_list)
# a_usid.save_logic_dataframe(current_time=current_time)
# a_usid.save_audit_dataframe(current_time=current_time)
print('OK')
print(base_dir)
#
# git stash
# git pull
# pm2 logs 0