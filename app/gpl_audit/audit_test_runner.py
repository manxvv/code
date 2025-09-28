import os
import importlib
from datetime import datetime
import pandas as pd
import sys
path_nsa_sa = os.path.join(os.path.join(os.getcwd(), "app"), "gpl_audit")
sys.path.append(path_nsa_sa)
from AuditUSID import AuditUSID
from AuditReport import AuditReport
from custom_log import Custom_Log

def run_gpl_audit(curr_dir, circle, enmFile_list, siteList_file_path, task_id):
    current_time = datetime.now().strftime('%m%d%Y_%H%M%S')
    folder_name = task_id+"_"+circle+"_"+current_time
    nsa_sa_path = os.path.join(curr_dir, "app", "gpl_audit")
    file_path = os.path.join(curr_dir, "downloads")
    base_dir = os.path.join(file_path, "gpl_audit", folder_name)
    if not os.path.exists(base_dir): os.makedirs(base_dir)
    log_file = os.path.join(base_dir,  F'{folder_name}.log')
    para_file = []
    for one_enmFile in enmFile_list: para_file.append(os.path.join(curr_dir, one_enmFile))
    site_file = os.path.join(curr_dir, siteList_file_path)

    custom_log = Custom_Log(log_file=log_file)
    a_usid = AuditUSID(nsa_sa_path=nsa_sa_path, base_dir=base_dir, custom_log=custom_log,
                       para_file=para_file, site_file=site_file, circle=circle)
    for node in list(a_usid.df_site.node.unique()):
        a_usid.custom_log.log.info(F'Audit Started for {node}')
        self = getattr(importlib.import_module('Audit'), 'Audit')(a_usid=a_usid, node=node)
        self.run()
        # self.run_all_parameters_audit()
    AuditReport(a_usid=a_usid)
    a_usid.custom_log.log.info(F'Audit Completed!!!')
    a_usid.custom_log.release()

    return os.path.join("downloads", "gpl_audit", folder_name)
