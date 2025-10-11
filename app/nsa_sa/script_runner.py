import os
import importlib
from datetime import datetime
import uuid
import shutil
import sys
import pandas as pd
path_nsa_sa = os.path.join(os.path.join(os.getcwd(), "app"), "nsa_sa")
sys.path.append(path_nsa_sa)
from USID import USID
from custom_log import Custom_Log


def scripting_nsa_sa(siteList_original_filename, eFile_original_filename,
                     nsa_sa_path, circle, enm, site_file, para_file, curr_dir):
    print("shdksdfhksdhfkdhf")
    current_time = datetime.now().strftime('%m%d%Y_%H%M%S')
    unq_name = f"{circle}_{enm}_{current_time}"
    site_name = unq_name
    file_path = curr_dir
    base_dir = os.path.join(file_path, "downloads", "nsa_sa", site_name)
    os.mkdir(base_dir)
    shutil.copy(para_file, os.path.join(base_dir,"input_"+eFile_original_filename))
    print("sdfkhsdkjfhksjdhfjsdhf")
    shutil.copy(site_file, os.path.join(base_dir,"input_"+siteList_original_filename))
    print("sdkfhksjdhfkjshdf")
    log_file = os.path.join(base_dir, F'{site_name}_{current_time}.log')
    custom_log = Custom_Log(log_file=log_file)
    try:
        usid = USID(nsa_sa_path=nsa_sa_path, base_dir=base_dir, custom_log=custom_log,
                    para_file=[para_file], site_file=site_file, circle=circle, enm=enm)
        modules = ['aa_01_5qiTable_BWP', 'aa_02_MOs_Create', 'aa_03_Lock_NR', 'aa_04_Parameter', 'aa_05_UnLock_NR']
        print("dsfjkhdkfjhdfhkjdsfhsdf")
        nodes = sorted(list(usid.df_site.loc[usid.df_site.status].node.unique()))
        print("dkshfkjshfkjhskfjhskjdfhsdf")
        if len(nodes) > 0:
            custom_log.log.info(F'Command File Saved for the Activity!!!')
            node = nodes[0]
            self = getattr(importlib.import_module(F'aa_Command'), 'aa_Command')(usid=usid, node=node)
            self.run()
            for node in nodes:
                custom_log.log.info(F'Script Started for {node}')
                print("sdjskjdfhsdfhj")
                for module in modules:
                    custom_log.log.info(module)
                    self = getattr(importlib.import_module(F'{module}'), module)(usid=usid, node=node)
                    self.run()
            usid.df_gpl = pd.DataFrame(usid.gpl_list)
            print("dsfhksdfhksjhfkjsd",len(usid.df_gpl))
            usid.save_different_dataframe(data={'GPL': usid.df_gpl})
            print("sdfhjskfhkshdfkjshdkfjhd")
            custom_log.log.info(F'Scripting Completed Successfully!!!')
    except Exception as e:
        print("sdshkdhskdjh")
        custom_log.log.error(F'Error: \n\n{e}\n\n')
        custom_log.log.info(F'Scripting Failed!!!')
    return base_dir
