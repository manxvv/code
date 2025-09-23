import os
import importlib
from datetime import datetime
import pandas as pd
import sys
path_nsa_sa = os.path.join(os.path.join(os.getcwd(),"app"),"gpl_audit")
sys.path.append(path_nsa_sa)
print(sys.path,"sys.pathsys.pathsys.path audit_script_runner")
from AuditUSID import AuditUSID
from custom_log import Custom_Log



def run_gpl_audit(curr_dir,circle,enmFile_list,siteList_file_path,task_id):
    
    
    
    print(curr_dir,circle,enmFile_list,siteList_file_path,"curr_dir,circle_name,enmFile_list,siteList_file_path")
    
    
    # base_dir = os.path.join(file_path,"downloads","nsa_sa", site_name)
    current_time = datetime.now().strftime('%m%d%Y_%H%M%S')
    site_name = 'Audit_09_23_2025'
    
    folder_name = task_id+"_"+circle+"_"+current_time
    nsa_sa_path = os.path.join(curr_dir,"app","gpl_audit")
    
    
    

    
    print(nsa_sa_path,"nsa_sa_pathnsa_sa_path")
    file_path = os.path.join(curr_dir,"downloads")
    base_dir = os.path.join(file_path, "gpl_audit",folder_name)
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    # base_dir = os.path.join(file_path, site_name)
    log_file = os.path.join(base_dir,  F'{folder_name}.log')

    para_file = []
    
    for one_enmFile in enmFile_list:
        para_file.append(os.path.join(curr_dir,one_enmFile))

    site_file = os.path.join(curr_dir,siteList_file_path)
    
    print(site_file)
    print(para_file)

    custom_log = Custom_Log(log_file=log_file)
    audit_usid = AuditUSID(nsa_sa_path=nsa_sa_path, base_dir=base_dir, custom_log=custom_log,
                        para_file=para_file, site_file=site_file, circle=circle)
    modules = ['aa_01_NR_Parameter']

    print(base_dir)
    audit_usid.df_gpl = pd.DataFrame(audit_usid.gpl_list)

    for node in audit_usid.nodes:
        for module in modules:
            print(F'{node} --- {module}')
            self = getattr(importlib.import_module(F'{module}'), module)(audit_usid=audit_usid, node=node)
            self.run()

    audit_usid.df_gpl = pd.DataFrame(audit_usid.gpl_list)
    audit_usid.save_logic_dataframe(current_time=current_time)
    audit_usid.save_audit_dataframe(current_time=current_time)
    print('OK')
    print(base_dir)
    
    
    
    return os.path.join("downloads", "gpl_audit",folder_name)
# print(F'cmedit get {usid.log_mos} --dynamic')
