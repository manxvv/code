import copy
import re
import sys
from itertools import product

from custom_log import Custom_Log


class Site:
    def __init__(self, *, node: str, mos: dict, custom_log: Custom_Log):
        self.node = node
        self.mos = mos
        self.me = F'SubNetwork=ONRM_ROOT_MO,SubNetwork=LTE_5G,MeContext={self.node},ManagedElement={self.node}'
        if 'me_me' in self.mos.keys():
            self.me = self.mos['me_me']
            del self.mos['me_me']
        else:
            custom_log.log.exception(F'Error : For Node: {self.node} dnPrefix could not be found')
        self.fdns = sorted(list(self.mos.keys()))
        self.bbu = self.get_bbu_id()

        self.du_cell = sorted([re.match(".*,NRCellDU=([^,]*)$", _).group(1)
                               for _ in self.fdns if re.match(".*,NRCellDU=([^,]*)$", _)])
        self.cu_cell = sorted([re.match(".*,NRCellCU=([^,]*)$", _).group(1)
                               for _ in self.fdns if re.match(".*,NRCellCU=([^,]*)$", _)])
        self.fdd_cell = sorted([re.match(".*,EUtranCellFDD=([^,]*)$", _).group(1)
                                for _ in self.fdns if re.match(".*,EUtranCellFDD=([^,]*)$", _)])
        self.tdd_cell = sorted([re.match(".*,EUtranCellTDD=([^,]*)$", _).group(1)
                                for _ in self.fdns if re.match(".*,EUtranCellTDD=([^,]*)$", _)])
        self.tn_dict, self.xn_ip, self.xn_sctp, self.type_int = self.get_sctp_local_sctp_dicts()

    def fdn_exists(self, *, fdn: str) -> bool: return fdn in self.fdns

    def get_fdn_parameter(self, *, fdn: str, para: str) -> dict or list or str or None:
        return self.mos[fdn].get(para, None) if self.fdn_exists(fdn=fdn) else None

    def ldn_exists(self, *, ldn: str) -> bool:
        return len([_ for _ in self.fdns if _.endswith(ldn)]) > 0

    def get_fdn_from_ldn(self, *, ldn: str) -> str or None:
        return [_ for _ in self.fdns if _.endswith(ldn)][0] if self.ldn_exists(ldn=ldn) else None

    def get_ldn_parameter(self, *, ldn: str, para: str) -> dict or list or str or None:
        return self.mos[self.get_fdn_from_ldn(ldn=ldn)].get(para, None) if self.ldn_exists(ldn=ldn) else None

    def get_sctp_ip(self, *, fdn: str, type_interface: str) -> (str or None, str or None):
        ip, sctp = None, None
        # local_sctp_mos =
        mo = [self.get_fdn_parameter(fdn=_, para='sctpEndpointRef') for _ in
              [_ for _ in self.fdns if re.match(F'{fdn},LocalSctpEndpoint=[^,]*$', _)]
              if self.get_fdn_parameter(fdn=_, para='interfaceUsed') == type_interface]
        if len(mo) > 0:
            ip, sctp = self.get_fdn_parameter(fdn=mo[0], para='localIpAddress'), self.get_fdn_parameter(fdn=mo[0], para='sctpProfile')
            if ip and len(ip) > 0: ip = ip[0]
        return ip, sctp, type_interface

    def get_sctp_local_sctp_dicts(self) -> (dict, str, str, str):
        xn_ip, xn_sctp, type_int = None, None, None
        tn_dict = {
            'Transport': {'transportId': '1', 'SctpEndpoint': {
                'attributes': {'xc:operation': 'create'}, 'sctpEndpointId': 'XN', 'dtlsSctpSecurityMode': 'DISABLED',
                'portNumber': '38422', 'localIpAddress': 'Transport=1,Router=LTE_NR,InterfaceIPv6=NR,AddressIPv6=NR_S1U_OAM',
                'sctpProfile': 'Transport=1,SctpProfile=1'}},
            'GNBCUCPFunction': {'gNBCUCPFunctionId': '1', 'EndpointResource': {
                'endpointResourceId': '1', 'LocalSctpEndpoint': {
                    'attributes': {'xc:operation': 'create'}, 'localSctpEndpointId': '4', 'interfaceUsed': 'XN',
                    'sctpEndpointRef': 'Transport=1,SctpEndpoint=XN'}
            }}
        }
        tmp_fdns = [_ for _ in self.fdns if re.match('GNBCUCPFunction=1,EndpointResource=[^,]*$', _)]
        if len(tmp_fdns) > 0:
            endpointResourceId, localSctpEndpointId, sctpEndpointId = tmp_fdns[0].split('=')[-1], '4', 'XN'
            tmp_list = [_.split('=')[-1] for _ in self.fdns if re.match(F'{tmp_fdns[0]},LocalSctpEndpoint=[^,]*$', _)]
            if localSctpEndpointId in tmp_list: localSctpEndpointId = 'XN' if 'XN' not in tmp_list else 'XN_1'
            tmp_list = [_.split('=')[-1] for _ in self.fdns if re.match(F'{tmp_fdns[0]},LocalSctpEndpoint=[^,]*$', _)]
            if sctpEndpointId in tmp_list: sctpEndpointId = 'XN_XN' if 'XN_XN' not in tmp_list else 'XN_1'
            xn_ip, xn_sctp, xn_type_interface = self.get_sctp_ip(fdn=tmp_fdns[0], type_interface='XN')
            if xn_ip and xn_sctp:
                tn_dict, xn_ip, xn_sctp, type_int = {}, xn_ip, xn_sctp, 'Exist - Please Validate'
            else:
                ng_ip, ng_sctp, ng_type_interface = self.get_sctp_ip(fdn=tmp_fdns[0], type_interface='NG')
                x2_ip, x2_sctp, x2_type_interface = self.get_sctp_ip(fdn=tmp_fdns[0], type_interface='X2')
                if ng_ip and ng_sctp:
                    tn_dict['Transport']['SctpEndpoint'] |= {'sctpEndpointId': sctpEndpointId, 'localIpAddress': ng_ip, 'sctpProfile': ng_sctp}
                    tn_dict['GNBCUCPFunction']['EndpointResource']['LocalSctpEndpoint'] |= {
                        'localSctpEndpointId': localSctpEndpointId, 'sctpEndpointRef': F'Transport=1,SctpEndpoint={sctpEndpointId}'}
                    xn_ip, xn_sctp, type_int = ng_ip, ng_sctp, ng_type_interface
                elif x2_ip or x2_sctp:
                    tn_dict['Transport']['SctpEndpoint'] |= {'sctpEndpointId': sctpEndpointId, 'localIpAddress': x2_ip, 'sctpProfile': x2_sctp}
                    tn_dict['GNBCUCPFunction']['EndpointResource']['LocalSctpEndpoint'] |= {
                        'localSctpEndpointId': localSctpEndpointId, 'sctpEndpointRef': F'Transport=1,SctpEndpoint={sctpEndpointId}'}
                    xn_ip, xn_sctp, type_int = x2_ip, x2_sctp, x2_type_interface
                else: type_int = 'NotFound'
        else:
            tn_dict['GNBCUCPFunction']['EndpointResource'] |= {'attributes': {'xc:operation': 'create'}}
        if xn_ip and re.match(F'.*,ManagedElement=[^,]*,(.*)', xn_ip):
            xn_ip = re.match(F'.*,ManagedElement=[^,]*,(.*)', xn_ip).group(1)
        if xn_sctp and re.match(F'.*,ManagedElement=[^,]*,(.*)', xn_sctp):
            xn_sctp = re.match(F'.*,ManagedElement=[^,]*,(.*)', xn_sctp).group(1)
        return tn_dict, xn_ip, xn_sctp, type_int

    def get_bbu_id(self) -> str:
        for fdn in [_ for _ in self.fdns if re.match('Equipment=1,FieldReplaceableUnit=([^,]*)$', _)]:
            product = None
            if 'productData' in self.mos[fdn].keys() and self.mos[fdn].get('productData') is not None:
                product = self.mos[fdn].get('productData').get('productName')
            if product and len([_ for _ in ['Baseband ', 'RAN Processor '] if _ in product]) > 0:
                return re.match('Equipment=1,FieldReplaceableUnit=([^,]*)$', fdn).group(1)
        return 'NA'
