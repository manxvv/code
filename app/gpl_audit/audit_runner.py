import os
import importlib
from datetime import datetime
from AuditUSID import AuditUSID
from custom_log import Custom_Log
import shutil

def audit_nsa_sa(siteList_original_filename,eFile_original_filename,nsa_sa_path,circle,site_file,para_file,curr_dir):
    current_time = datetime.now().strftime('%m%d%Y_%H%M%S')
    unq_name = f"{circle}_{current_time}"
    site_name = unq_name
    file_path = curr_dir
    base_dir = os.path.join(file_path,"downloads","nsa_sa", site_name)
    os.mkdir(base_dir)
    shutil.copy(para_file,os.path.join(base_dir,"input_"+eFile_original_filename))
    shutil.copy(site_file,os.path.join(base_dir,"input_"+siteList_original_filename))
    log_file = os.path.join(base_dir, F'{site_name}_{current_time}.log')
    custom_log = Custom_Log(log_file=log_file)
    a_usid = AuditUSID(nsa_sa_path=nsa_sa_path, base_dir=base_dir, custom_log=custom_log,
                     para_file=para_file, site_file=site_file, circle=circle)
    modules = ['aa_01_5qiTable_BWP', 'aa_02_MOs_Create', 'aa_03_Lock_NR', 'aa_04_Parameter', 'aa_05_UnLock_NR']
    # aa_Command
    for node in a_usid.nodes:
        for module in modules:
            self = getattr(importlib.import_module(F'{module}'), module)(a_usid=a_usid, node=node)
            self.run()
    if len(a_usid.nodes) > 0:
        node = a_usid.nodes[0]
        self = getattr(importlib.import_module(F'aa_Command'), 'aa_Command')(a_usid=a_usid, node=node)
        self.run()
    a_usid.save_different_dataframe(current_time=current_time)
    return base_dir
