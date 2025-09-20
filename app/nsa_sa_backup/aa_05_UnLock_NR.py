import copy
import re
from Script import Script


class aa_05_UnLock_NR(Script):
    def create_rpc_msg(self):
        if self.node not in self.usid.nr_node: return
        self.mo_dict['DU'] = {'managedElementId': self.node, 'GNBDUFunction': {'gNBDUFunctionId': '1', 'NRCellDU': [], 'NRSectorCarrier': []}}
        for aa in ['NRCellDU', 'NRSectorCarrier']:
            for r in sorted([_ for _ in self.site.fdns if re.match(F".*,{aa}=([^,]*)$", _)]):
                if self.site.get_fdn_parameter(fdn=r, para='administrativeState') == 'UNLOCKED':
                    self.mo_dict['DU']['GNBDUFunction'][aa].append({
                        'attributes': {'xc:operation': 'update'}, F'{aa[0].lower() + aa[1:]}Id': r.split('=')[-1], 'administrativeState': 'UNLOCKED'})
