import copy
import os
import json
import re
import pandas as pd
from pandas import ExcelWriter
import numpy as np
from collections import OrderedDict
from common_func.custom_log import Custom_Log
from parse_dynamic_data_to_dict import parse_dynamic_data_to_dict
from Site import Site


dump_list = [
    'ManagedElement', 'SystemFunctions', 'Lm', 'FeatureState', 'TermPointToAmf',
    'AnrFunction', 'AnrFunctionNR', 'AnrFunctionNRUeCfg', 'AnrFunctionEUtran', 'AnrFunctionEUtranUeCfg',
    'Transport', 'SctpProfile', 'Sctp', 'SctpEndpoint', 'AddressIPv4', 'AddressIPv6', 'EndpointResource', 'LocalSctpEndpoint', 'LocalIpEndpoint',

    'GNBDUFunction', 'NRCellDU', 'NRSectorCarrier', 'DU5qiTable', 'DU5qi',
    'BWP', 'BWPSet', 'DynPowerOpt', 'BWPSetUeCfg', 'BWPSetCfg',
    'UeCC', 'UeBb', 'UeBbProfile', 'UeBbProfileUeCfg',
    'QosPriorityMapping', 'PriorityDomainMapping', 'DrxProfile', 'DrxProfileUeCfg', 'PuschRepRel16Drx',

    'GNBCUCPFunction', 'NRCellCU', 'EmCall', 'CUCP5qiTable', 'CUCP5qi',
    'NRNetwork', 'NRFrequency', 'NRFreqRelation', 'EUtraNetwork', 'EUtranFrequency', 'EUtranFreqRelation', 'NRCellRelation',
    'Mcpc', 'McpcPCellEUtranFreqRelProfile', 'McpcPCellEUtranFreqRelProfileUeCfg',
    'McpcPCellProfile', 'McpcPCellProfileUeCfg',
    'UeCC', 'InactivityProfile', 'InactivityProfileUeCfg', 'SrHandling', 'SrHandlingUeCfg',
    'RadioLinkControl', 'DrbRlc', 'DrbRlcUeCfg', 'UserPlaneProfile', 'UserPlaneProfileUeCfg',
    'RrcInactiveProfile', 'RrcInactiveProfileUeCfg',
    'Mcfb', 'McfbCellProfile', 'McfbCellProfileUeCfg',
    'TrafficSteering', 'TrStPSCellNrFreqRelProfile', 'TrStPSCellNrFreqRelProfileUeCfg',
    'TrStPSCellProfile', 'TrStPSCellProfileUeCfg', 'TrStSaCellProfile', 'TrStSaCellProfileUeCfg',
    'TrStSaEUtranFreqRelProfile', 'TrStSaEUtranFreqRelProfileUeCfg', 'TrStSaNrFreqRelProfile', 'TrStSaNrFreqRelProfileUeCfg',
    'UeMC', 'UeMCNrFreqRelProfile', 'UeMCNrFreqRelProfileUeCfg', 'UeMCCellProfile', 'UeMCCellProfileUeCfg',
    'UeMCEUtranFreqRelProfile', 'UeMCEUtranFreqRelProfileUeCfg',
    'UeGroupSelection', 'PrefUeGroupSelectionProfile', 'UeAdmissionGroupDefinition', 'UeGroupSelectionProfile',
    'UeMobilityGroupDefinition', 'UeServiceGroupDefinition',

    'GNBCUUPFunction', 'CUUP5qiTable', 'CUUP5qi', 'UeCC', 'DcDlCfg', 'GtpuSupervision', 'GtpuSupervisionProfile',
    'ENodeBFunction', 'EUtranCellTDD', 'UePolicyOptimization', 'EUtranCellFDD', 'UeMeasControl', 'ReportConfigB1NR',
    'GUtranFreqRelation', 'GUtranSyncSignalFrequency',

]


class USID:
    def __init__(self, *, base_dir: str, custom_log: Custom_Log, para_file: str, site_list: str, circle: str, enm: str):
        self.base_dir = base_dir
        self.custom_log = custom_log
        self.site_list = site_list
        self.circle = circle
        self.enm = enm

        self.df_site = pd.DataFrame()
        self.nr_node = []
        self.lte_node = []
        # DB Process
        self.db = {}
        self.db_data()
        # Log Data Process
        self.sites = {}
        mos_dict = parse_dynamic_data_to_dict(para_file=para_file)
        # print(mos_dict)
        for node in mos_dict.keys():
            self.sites[node] = Site(node=node, mos=mos_dict.get(node, {}))
        del mos_dict
        self.nodes = self.sites.keys()
        self.df_amf = self.get_amf_table()
        self.df_cell = self.get_cell_table()
        for node in self.sites.keys():
            site = self.sites[node]
            if len(self.sites[node].du_cell) > 0 or len(self.sites[node].cu_cell) > 0: self.nr_node += [node]
            if len(self.sites[node].fdd_cell) > 0 or len(self.sites[node].tdd_cell) > 0: self.lte_node += [node]
            print(node)

        self.dump_list = copy.deepcopy(dump_list)
        self.save_different_dataframe()

    @staticmethod
    def parse_string_to_json(value):
        if isinstance(value, str):
            if value.strip() in ['null', '<empty>']: return ''
            if value.strip() in ['"', '[', '{']: return value.lower() == 'true'
            try: return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    def db_data(self):
        db_dict = {
            'TermPointToAmf': ['circle', 'termPointToAmfId', 'ipv6Address1', 'ipv6Address2', 'ipv4Address1', 'ipv4Address2',
                               'administrativeState', 'defaultAmf', 'pwsRestartHandling'],
            'EUtranFreqRelation': ['circle', 'eUtranFreqRelationId', 'allowedMeasBandwidth', 'anrMeasOn', 'cellReselectionPriority',
                                   'eUtranFallbackPrioEc', 'pMaxEUtra', 'presenceAntennaPort1', 'qRxLevMin', 'tReselectionEUtra',
                                   'threshXHighP', 'threshXLowP', 'voicePrio', 'eUtranFrequencyRef', 'mcpcPCellEUtranFreqRelProfileRef',
                                   'trStSaEUtranFreqRelProfileRef', 'ueMCEUtranFreqRelProfileRef', 'UeMCEUtranFreqRelProfileUeCfg_blindRwrAllowed',
                                   'UeMCEUtranFreqRelProfileUeCfg_connModeAllowedPCell', 'UeMCEUtranFreqRelProfileUeCfg_connModePrioPCell'],
            'DU5qi': ['circle', 'dU5qiId', 'aqmMode', 'dscp', 'estimatedE2ERTT', 'logicalChannelGroupId', 'packetDelayBudget',
                      'packetDelayBudgetOffset', 'priorityLevel', 'profile5qi', 'puschRepRef', 'rlcSNLength', 'srHandlingRef',
                      'tReassemblyDl', 'tReassemblyUl'],
            'CUCP5qi': ['circle', 'cUCP5qiId', 'pdcpSnSize', 'profile5qi', 'rlcMode', 'tPdcpDiscard', 'tReorderingDl', 'tReorderingUl'],
            'CUUP5qi': ['circle', 'cUUP5qiId', 'aqmMode', 'counterActiveMode', 'dcDlPdcpAggrPrioCg', 'dcDlPdcpAggrTimeDiffCg',
                        'dcDlPdcpAggrTimeDiffProhibit', 'dcDlPdcpAggrTimeDiffThresh', 'drbRef', 'dscp', 'estimatedE2ERTT', 'l4sCfgRef',
                        'packetDelayBudget', 'packetDelayBudgetOffset', 'profile5qi', 'tOooUlDelivery'],
            'MOC': ['circle', 'mo', 'parameter', 'value', 'flag'],
        }

        self.db = {_: pd.DataFrame([], columns=db_dict[_]) for _ in db_dict.keys()}
        for sheet in db_dict.keys():
            try:
                df = pd.read_excel('DB.xlsx', sheet_name=sheet, dtype='str')
                df = df[db_dict[sheet]]
                df = df.replace('[^a-zA-Z0-9.,-_/+()[]{}]', '', regex=True)
                df.replace({np.nan: None, '': None}, inplace=True)
                df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                df = df.loc[(df.circle.isin(['Airtel', self.circle]))]
                df.drop(['circle'], axis=1, inplace=True)
                df.reset_index(inplace=True, drop=True)
                if sheet == 'MOC':
                    df['value'] = df['value'].apply(self.parse_string_to_json)
                    df = df.groupby(['mo', 'parameter'], sort=False, as_index=False).tail(1)
                self.db[sheet] = df.copy()

                # print(df)
            except Exception as e:
                self.custom_log.log.exception("message")
                self.custom_log.log.exception(e)
                self.custom_log.log.exception(F'sheet {sheet} has missing columns!!!')
                return

    def pass_cli_mos_file(self, *, mo_file: str) -> dict:
        mos_dict = {}
        mo_start = False
        with open(mo_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.rstrip('\n')
                if line.startswith('FDN :'):
                    mo = line.split("FDN :")[-1].strip()
                    if len(mo) == 0: continue
                    mo = self.parse_string_to_json(value=mo)
                    # re.match('.*ManagedElement=[^,]*,(.*)', val).group(1)
                    if ',MeContext=' in mo: node = re.match('.*,MeContext=([^,]*),.*', mo).group(1)
                    elif mo.startswith('NetworkElement='): node = re.match('NetworkElement=([^,]*),.*', mo).group(1)
                    else: continue
                    if node not in mos_dict.keys(): mos_dict[node] = {}
                    if mo not in mos_dict.get(node, {}).keys(): mos_dict[node][mo] = {}
                    tmp_mo_dict = {}
                    mo_start = True
                while mo_start:
                    line = f.readline().rstrip('\n')
                    if len(line) == 0:
                        mo_start = False
                        mos_dict[node][mo] = copy.deepcopy(tmp_mo_dict)
                        self.custom_log.log.info(mo)
                        self.custom_log.log.info(tmp_mo_dict)
                        continue
                    else:
                        line_sp = line.split(':')
                        if len(line_sp) == 2:
                            tmp_mo_dict[line_sp[0].strip()] = self.parse_string_to_json(line_sp[1].strip())
                        else:
                            tmp_mo_dict[line_sp[0].strip()] = None

        return mos_dict

    def get_amf_table(self) -> pd.DataFrame:
        col = ['circle', 'enm', 'node', 'termPointToAmfId', 'administrativeState',  'defaultAmf', 'pwsRestartHandling',
               'ipv6Address1', 'ipv6Address2', 'ipv4Address1', 'ipv4Address2', 'cellLocalId']
        tmp_list = []
        for node in self.sites:
            for fdn in [_ for _ in self.sites[node].fdns if re.match(".*,GNBCUCPFunction=[^,]*,TermPointToAmf=([^,]*)$", _)]:
                tmp_list.append([self.circle, self.enm, node] + [self.sites[node].get_fdn_parameter(fdn=fdn, para=_) for _ in col[3:]])
        df = pd.DataFrame(tmp_list, columns=col)
        return df

    def get_cell_table(self) -> pd.DataFrame:
        tmp_list = []
        for node in self.nodes:
            # self.sites[node] = Site(node=node, mos=self.mos.get(node, {}))
            site = self.sites[node]
            # ssbSubCarrierSpacing, ssbFrequency, ssbFrequencyAutoSelected
            for r in sorted([_ for _ in site.fdns if re.match(".*,NRCellDU=([^,]*)$", _)]):
                tmp_dict = {
                    'circle': self.circle, 'enm': self.enm, 'type': 'NR', 'node': node, 'DU': r.split('=')[-1],
                    'cellid': site.get_fdn_parameter(fdn=r, para='cellLocalId'), 'CU': None,
                    'ssbFrequency': site.get_fdn_parameter(fdn=r, para='ssbFrequency'),
                    'ssbSubCarrierSpacing': site.get_fdn_parameter(fdn=r, para='ssbSubCarrierSpacing'),
                    'XN_localIpAddress': site.xn_ip,
                    'XN_SctpEndpoint': site.xn_ip,
                    'XN_Type_Status': site.type_int,
                    'AMF_Count': len(self.df_amf.loc[(self.df_amf.node == node)].index),
                }
                for s in sorted([_ for _ in site.fdns if re.match(".*,NRCellCU=([^,]*)$", _)]):
                    if site.get_fdn_parameter(fdn=r, para='cellLocalId') == site.get_fdn_parameter(fdn=s, para='cellLocalId'):
                        freq_ref = site.get_fdn_parameter(fdn=s, para='nRFrequencyRef')
                        # print(freq_ref)
                        nr_frq = len([_ for _ in site.fdns if re.match(F'{s},NRFreqRelation=([^,]*)$', _)])
                        tmp_dict |= {'CU': s.split('=')[-1], 'nr_intra': nr_frq == 1, 'nr_inter': nr_frq > 1}
                tmp_list.append(copy.deepcopy(tmp_dict))
        df_cell = pd.DataFrame(tmp_list)
        # print(tmp_list)
        # print(df_cell)
        df = pd.DataFrame()
        return df


    def save_different_dataframe(self):
        data = {
            'ActivityDetails': self.df_site,
            'Node': self.df_cell,
            'Amf': self.df_amf,
        }
        with ExcelWriter(os.path.join(self.base_dir, F'NSA_SA_Info.xlsx')) as writer:
            for key in data:
                df = data.get(key).copy()
                df.reset_index().to_excel(writer, key, index=False)

    # def save_xls(self, data, xls_path):
    #     with ExcelWriter(xls_path) as writer:
    #         for key in data:
    #             if key == 'Cell_Move':
    #                 df = data.get(key).copy()
    #                 df.index.name = 'cell'
    #                 df.reset_index().to_excel(writer, key, index=False)
    #             else:
    #                 data.get(key).to_excel(writer, key, index=False)

        #
        # # Save Different DataFrames for LTE
        # if len(self.enodeb) > 0:
        #     data = {
        #         'EUtranFrequency': self.df_enb_ef,
        #         'EUtranFreqRelation': self.df_enb_er,
        #         'EUtranCellRelation': self.df_enb_ee,
        #         'ExternalENodeBFunction': self.df_enb_ex,
        #         'ExternalEUtranCell': self.df_enb_ec,
        #     }
        #     if self.df_enb_ef.shape[0] > 0 or self.df_enb_er.shape[0] > 0 or self.df_enb_ee.shape[0] > 0 or self.df_enb_ex.shape[0] > 0 or self.df_enb_ec.shape[0] > 0:
        #         self.save_xls(data, os.path.join(self.base_dir, F'2_EUtraNetwork.xlsx'))
        #
        #     data = {
        #         'GUtranSyncSignalFrequency': self.df_enb_nf,
        #         'GUtranFreqRelation': self.df_enb_nr,
        #         'GUtranCellRelation': self.df_enb_ne,
        #         'ExternalGNodeBFunction': self.df_enb_nx,
        #         'ExternalGUtranCell': self.df_enb_nc,
        #     }
        #     if self.df_enb_nf.shape[0] > 0 or self.df_enb_nr.shape[0] > 0 or self.df_enb_ne.shape[0] > 0 or self.df_enb_nx.shape[0] > 0 or self.df_enb_nc.shape[0] > 0:
        #         self.save_xls(data, os.path.join(self.base_dir, F'3_GUtraNetwork.xlsx'))


    # Process Data Table for Cells and Scripting; Info displayed after scripts is processed

    # ssbSubCarrierSpacing, ssbFrequency, ssbFrequencyAutoSelected
    # for r in sorted([_ for _ in self.fdns if re.match(".*,NRCellCU=([^,]*)$", _)]):
    #     tmp_list.append({
    #         'circle': self.circle, 'enm': self.enm, 'type': 'CU', 'node': node, 'cell': r.split('=')[-1],
    #         'cellid': site.get_fdn_parameter(fdn=r, para='cellLocalId'),
    #         'ssbfreq': site.get_fdn_parameter(fdn=r, para='ssbFrequency'),
    #         'ssbsub': site.get_fdn_parameter(fdn=r, para='ssbSubCarrierSpacing'),
    #     })
    #
