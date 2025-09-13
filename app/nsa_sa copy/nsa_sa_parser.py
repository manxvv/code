from USID import USID

def nsa_sa_script(base_dir: str, in_files: str, site_list: str, circle: str, enm: str) -> str:
    
    usid = USID(base_dir=base_dir, custom_log=custom_log, in_files=in_files, circle=circle, enm=enm)
    # Write Scripts
    modules = ['aa_01_5qiTable_BWP', 'aa_02_MOs_Create', 'aa_03_Lock_NR', 'aa_04_Parameter', 'aa_05_UnLock_NR']
    for node in usid.nodes:
        for module in modules:
            self = getattr(importlib.import_module(F'airtel.nsa_sa.{module}'), module)(usid=usid, node=node)
            self.run()
    # Write a command Files and Process docs
    if len(usid.nodes) > 0:
        node = usid.nodes[0]
        self = getattr(importlib.import_module(F'airtel.nsa_sa.aa_Command'), 'aa_Command')(usid=usid, node=node)
        self.run()