import copy
import os
import json
import re
from datetime import datetime
import pandas as pd
from pandas import ExcelWriter
import numpy as np
from collections import OrderedDict
from custom_log import Custom_Log
from parse_dynamic_data_to_dict import parse_dynamic_data_to_dict
from Site import Site


dump_list = [
    'TermPointToAmf.(termPointToAmfId,administrativeState,defaultAmf,pwsRestartHandling,ipv6Address1,ipv6Address2,ipv4Address1,ipv4Address2)',
    'SystemFunctions', 'Lm', 'FeatureState.(description,featureState,featureStateId,licenseState,serviceState)',
    'CmFunction.(syncStatus)',
    'ManagedElement',
    'AnrFunction', 'AnrFunctionNR', 'AnrFunctionNRUeCfg', 'AnrFunctionEUtran', 'AnrFunctionEUtranUeCfg',
    'Transport', 'SctpProfile', 'Sctp', 'SctpEndpoint', 'AddressIPv4', 'AddressIPv6',
    'EndpointResource', 'LocalSctpEndpoint', 'LocalIpEndpoint',

    'GNBDUFunction', 'NRCellDU', 'NRSectorCarrier', 'DU5qiTable', 'DU5qi', 'Paging', 'Rrc',
    'RadioBearerTable', 'SignalingRadioBearer',
    'BWP', 'BWPSet', 'DynPowerOpt', 'BWPSetUeCfg', 'BWPSetCfg',
    'UeCC', 'UeBb', 'UeBbProfile', 'UeBbProfileUeCfg', 'Rach', 'RachUeCfg',
    'RadioLinkControl', 'DrbRlc', 'DrbRlcUeCfg', 'UeAdaptiveRlc', 'UeAdaptiveRlcUeCfg',
    'QosPriorityMapping', 'PriorityDomainMapping', 'DrxProfile', 'DrxProfileUeCfg', 'PuschRepRel16Drx',

    'GNBCUCPFunction', 'NRCellCU', 'EmCall', 'SecurityHandling', 'CUCP5qiTable', 'CUCP5qi',
    'NRNetwork', 'NRFrequency', 'NRFreqRelation', 'EUtraNetwork', 'EUtranFrequency', 'EUtranFreqRelation', 'NRCellRelation',
    'Mcpc', 'McpcPCellEUtranFreqRelProfile', 'McpcPCellEUtranFreqRelProfileUeCfg',
    'McpcPCellProfile', 'McpcPCellProfileUeCfg',
    'UeCC', 'InactivityProfile', 'InactivityProfileUeCfg', 'SrHandling', 'SrHandlingUeCfg',
    'DrbRlc', 'DrbRlcUeCfg', 'UserPlaneProfile', 'UserPlaneProfileUeCfg',
    'RrcInactiveProfile', 'RrcInactiveProfileUeCfg',
    'Rohc', 'RohcUeCfg',
    'Mcfb', 'McfbCellProfile', 'McfbCellProfileUeCfg',
    'TrafficSteering', 'TrStPSCellNrFreqRelProfile', 'TrStPSCellNrFreqRelProfileUeCfg',
    'TrStPSCellProfile', 'TrStPSCellProfileUeCfg', 'TrStSaCellProfile', 'TrStSaCellProfileUeCfg',
    'TrStSaEUtranFreqRelProfile', 'TrStSaEUtranFreqRelProfileUeCfg', 'TrStSaNrFreqRelProfile', 'TrStSaNrFreqRelProfileUeCfg',
    'UeMC', 'UeMCNrFreqRelProfile', 'UeMCNrFreqRelProfileUeCfg', 'UeMCCellProfile', 'UeMCCellProfileUeCfg',
    'UeMCEUtranFreqRelProfile', 'UeMCEUtranFreqRelProfileUeCfg',
    'UeCovMeas', 'UcmCellProfile', 'UcmCellProfileUeCfg', 'UcmNrFreqRelProfile',

    'UeGroupSelection', 'PrefUeGroupSelectionProfile', 'UeAdmissionGroupDefinition', 'UeGroupSelectionProfile',
    'UeMobilityGroupDefinition', 'UeServiceGroupDefinition',

    'GNBCUUPFunction', 'CUUP5qiTable', 'CUUP5qi', 'UeCC', 'DcDlCfg', 'GtpuSupervision', 'GtpuSupervisionProfile',
    'ENodeBFunction', 'UePolicyOptimization', 'EUtranCellFDD', 'EUtranCellTDD', 'UeMeasControl', 'ReportConfigB1NR',
    'GUtranSyncSignalFrequency', 'GUtranFreqRelation', 'GUtranCellRelation',
]


class USID:
    def __init__(self, *,nsa_sa_path:str, base_dir: str, custom_log: Custom_Log, para_file: str, site_file: str, circle: str, enm: str):
        self.base_dir = base_dir
        self.custom_log = custom_log
        self.circle = circle
        self.enm = enm
        self.log_mos = ';'.join([F'{_}.<w>' if '(' not in _ else _ for _ in dump_list])

        # DB Process
        self.db = self.db_data(nsa_sa_path)
        # Site List Data
        
        print("site_filesite_file",site_file,"site_filesite_file")
        self.df_site = self.site_data(site_file=site_file)
        self.nodes = list(self.df_site.node.unique())
        # Log Data Process
        self.sites = {}
        mos_dict = parse_dynamic_data_to_dict(para_file=para_file)
        for node in list(self.df_site.node.unique()):
            self.sites[node] = Site(node=node, mos=mos_dict.get(node, {}), custom_log=self.custom_log)
        del mos_dict
        self.nr_node, self.lte_node = [], []
        for node in self.sites.keys():
            if len(self.sites[node].du_cell) > 0 or len(self.sites[node].cu_cell) > 0: self.nr_node += [node]
            if len(self.sites[node].fdd_cell) > 0 or len(self.sites[node].tdd_cell) > 0: self.lte_node += [node]
        # Site List Data Process
        self.df_site = self.site_data(site_file=site_file)
        self.df_amf = self.get_amf_table()
        self.df_feature = self.get_feature_table()
        self.df_site = pd.concat([self.df_site, self.process_df_site_with_logs_data()], axis=1)
        self.df_cell = self.get_cell_table()



        self.df_site.reset_index(drop=True, inplace=True)
        # self.df_site = pd.concat([self.df_site, pd.DataFrame(tmp_list)], axis=1).reset_index(drop=True, inplace=False)

        self.df_gpl = pd.DataFrame([], columns=['node', 'mo', 'parameter', 'value', 'gpl_value', 'flag', 'remark'])
        self.para_list = []
        # self.save_different_dataframe()


    def site_data(self, *, site_file: str) -> pd.DataFrame:
        if site_file is None: df = pd.DataFrame([], columns=['circle', 'ENM', 'SiteID', 'Node'])
        df = pd.read_excel(site_file, sheet_name='Node', usecols=["circle", "ENM", "SiteID", "Node"], dtype='str')
        df = df[['circle', 'ENM', 'SiteID', 'Node']]
        df.columns = df.columns.str.lower()
        df = df.replace({np.nan: None, '': None}, inplace=False).dropna()
        df = df.loc[(df.enm == self.enm)]
        df = df.drop_duplicates(subset="node", keep="first")
        df.reset_index(inplace=True, drop=True)
        return df

    @staticmethod
    def parse_string_to_json(value):
        if isinstance(value, str):
            # if value.strip() in ['null', '<empty>']: return ''
            if (value.startswith("{") and value.endswith("}")) or (value.startswith("[") and value.endswith("]")):
                try: return json.loads(value)
                except json.JSONDecodeError: return value
            elif value.startswith('"') and value.endswith('"'): return value.strip('"')
            elif value.lower() in ['true', 'false']: return value.lower()
        return value

    def db_data(self,nsa_sa_path):
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

        db = {_: pd.DataFrame([], columns=db_dict[_]) for _ in db_dict.keys()}
        for sheet in db_dict.keys():
            try:
                df = pd.read_excel(os.path.join(nsa_sa_path,'DB.xlsx'), sheet_name=sheet, dtype='str')
                df = df[db_dict[sheet]]
                df = df.replace('[^a-zA-Z0-9.,-_/+()[]{}]', '', regex=True)
                df = df.replace({np.nan: None, '': None}, inplace=False).dropna()
                # df.replace({np.nan: None, '': None}, inplace=True)
                df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                df = df.loc[(df.circle.isin(['Airtel', self.circle]))]
                df.drop(['circle'], axis=1, inplace=True)
                if sheet == 'MOC':
                    df['value'] = df['value'].apply(self.parse_string_to_json)
                    df = df.groupby(['mo', 'parameter'], sort=False, as_index=False).tail(1)
                df.reset_index(inplace=True, drop=True)
                db[sheet] = df.copy()
                # print(df)
            except Exception as e:
                self.custom_log.log.info("message")
                self.custom_log.log.exception(e)
                self.custom_log.log.exception(F'sheet {sheet} has missing columns!!!')
                print(f'sheet {sheet} has missing columns!!!'+e)
                return None
        return db


    def get_amf_table(self) -> pd.DataFrame:
        col = ['circle', 'enm', 'node', 'termPointToAmfId', 'administrativeState',  'defaultAmf', 'pwsRestartHandling',
               'ipv6Address1', 'ipv6Address2', 'ipv4Address1', 'ipv4Address2']
        tmp_list = []
        for node in self.sites:
            for fdn in [_ for _ in self.sites[node].fdns if re.match(".*GNBCUCPFunction=[^,]*,TermPointToAmf=([^,]*)$", _)]:
                tmp_list.append([self.circle, self.enm, node] + [self.sites[node].get_fdn_parameter(fdn=fdn, para=_) for _ in col[3:]])
        df = pd.DataFrame(tmp_list, columns=col)
        return df

    def get_feature_table(self) -> pd.DataFrame:
        featureStateId = [
            'CXC4012493', 'CXC4012534', 'CXC4012538', 'CXC4012549', 'CXC4012550', 'CXC4012591', 'CXC4012592', 'CXC4012637',
            'CXC4012607', 'CXC4012475', 'CXC4012548', 'CXC4012724', 'CXC4012680', 'CXC4012688', 'CXC4012601', 'CXC4012330',
            'CXC4012406', 'CXC4012510', 'CXC4012562', 'CXC4012593', 'CXC4012638', 'CXC4012590', 'CXC4012218'
        ]
        tmp_list = []
        description_dict = {'circle': 'description', 'enm': 'description', 'description': 'description'}
        for node in self.sites:
            tmp_dict = {'circle': self.circle, 'enm': self.enm, 'node': node}
            for r in featureStateId:
                tmp_dict[r] = None
                fdn = F'SystemFunctions=1,Lm=1,FeatureState={r}'
                tmp_dict[r] = (F'{self.sites[node].get_fdn_parameter(fdn=fdn, para="featureState")}/'
                               F'{self.sites[node].get_fdn_parameter(fdn=fdn, para="licenseState")}') if fdn in self.sites[node].fdns else None
                if r not in description_dict: description_dict[r] = self.sites[node].get_fdn_parameter(fdn=fdn, para="description")
                elif description_dict[r] is None: description_dict[r] = self.sites[node].get_fdn_parameter(fdn=fdn, para="description")
            tmp_list.append(copy.deepcopy(tmp_dict))
        tmp_list = [copy.deepcopy(description_dict)] + tmp_list
        print(tmp_list)
        df = pd.DataFrame(tmp_list)
        return df

    def get_cell_table(self) -> pd.DataFrame:
        tmp_list = []
        for node in self.sites.keys():
            site = self.sites[node]
            tmp_cu_cell_list = []
            for r in sorted([_ for _ in site.fdns if re.match(".*GNBDUFunction=[^,]*,NRCellDU=([^,]*)$", _)]):
                tmp_dict = {
                    'circle': self.circle, 'enm': self.enm, 'type': 'NR', 'node': node,
                    'gnbid_enbid': site.get_fdn_parameter(fdn=','.join(r.split(',')[:-1]), para='gNBId'),
                    'cellid': site.get_fdn_parameter(fdn=r, para='cellLocalId'),
                    'tac': site.get_fdn_parameter(fdn=r, para='nRTAC'),
                    'cell': r.split('=')[-1],
                    'CU': None,  'nr_intra_rel': None, 'nr_inter_rel': None,
                    'ssbFrequency': site.get_fdn_parameter(fdn=r, para='ssbFrequency'),
                    'ssbSubCarrierSpacing': site.get_fdn_parameter(fdn=r, para='ssbSubCarrierSpacing'),
                    'ssbPeriodicity': site.get_fdn_parameter(fdn=r, para='ssbPeriodicity'),
                    'ssbOffset': site.get_fdn_parameter(fdn=r, para='ssbOffset'),
                    'ssbDuration': site.get_fdn_parameter(fdn=r, para='ssbDuration'),
                }
                for s in sorted([_ for _ in site.fdns if re.match(".*GNBCUCPFunction=[^,]*,NRCellCU=([^,]*)$", _)]):
                    if site.get_fdn_parameter(fdn=r, para='cellLocalId') == site.get_fdn_parameter(fdn=s, para='cellLocalId'):
                        tmp_cu_cell_list.append(s.split('=')[-1])
                        freq = site.get_fdn_parameter(fdn=s, para='nRFrequencyRef')
                        relations = [_ for _ in site.fdns if re.match(F'{s},NRFreqRelation=([^,]*)$', _)]
                        intra_rel = [_ for _ in relations if site.get_fdn_parameter(fdn=s, para='nRFrequencyRef') == freq]
                        inter_rel = [_ for _ in relations if site.get_fdn_parameter(fdn=s, para='nRFrequencyRef') != freq]
                        tmp_dict |= {
                            'CU': s.split('=')[-1],
                            'intra_rel': intra_rel,
                            'inter_rel': inter_rel,
                            'transmitSib2': site.get_fdn_parameter(fdn=s, para='transmitSib2'),
                            'transmitSib4': site.get_fdn_parameter(fdn=s, para='transmitSib4'),
                            'transmitSib5': site.get_fdn_parameter(fdn=s, para='transmitSib5'),
                        }
                tmp_list.append(copy.deepcopy(tmp_dict))
            for s in sorted([_ for _ in site.fdns if re.match(".*GNBDUFunction=[^,]*,NRCellCU=([^,]*)$", _)]):
                if s.split('=')[-1] not in tmp_cu_cell_list:
                    freq = site.get_fdn_parameter(fdn=s, para='nRFrequencyRef')
                    relations = [_ for _ in site.fdns if re.match(F'{s},NRFreqRelation=([^,]*)$', _)]
                    intra_rel = [_ for _ in relations if site.get_fdn_parameter(fdn=s, para='nRFrequencyRef') == freq]
                    inter_rel = [_ for _ in relations if site.get_fdn_parameter(fdn=s, para='nRFrequencyRef') != freq]
                    tmp_dict = {
                        'circle': self.circle, 'enm': self.enm, 'type': 'NR', 'node': node,
                        'cell': None, 'CU': s.split('=')[-1], 'nr_intra_rel': None, 'nr_inter_rel': None,
                        'cellid': site.get_fdn_parameter(fdn=s, para='cellLocalId'),
                        'intra_rel': intra_rel,
                        'inter_rel': inter_rel,
                        'transmitSib2': site.get_fdn_parameter(fdn=s, para='transmitSib2'),
                        'transmitSib4': site.get_fdn_parameter(fdn=s, para='transmitSib4'),
                        'transmitSib5': site.get_fdn_parameter(fdn=s, para='transmitSib5'),
                    }
                    tmp_list.append(copy.deepcopy(tmp_dict))
            #         ENodeBFunction=1,EUtranCellFDD=
            for r in sorted([_ for _ in site.fdns if re.match(".*ENodeBFunction=[^,]*,EUtranCellFDD=([^,]*)$", _)]):
                tmp_dict = {
                    'circle': self.circle, 'enm': self.enm, 'type': 'FDD', 'node': node,
                    'gnbid_enbid': site.get_fdn_parameter(fdn=','.join(r.split(',')[:-1]), para='eNBId'),
                    'cellid': site.get_fdn_parameter(fdn=r, para='cellId'),
                    'cell': r.split('=')[-1],
                    'earfcn': site.get_fdn_parameter(fdn=r, para='earfcndl'),
                    'tac': site.get_fdn_parameter(fdn=r, para='tac'),
                }
                tmp_list.append(copy.deepcopy(tmp_dict))
            for r in sorted([_ for _ in site.fdns if re.match(".*ENodeBFunction=[^,]*,EUtranCellTDD=([^,]*)$", _)]):
                tmp_dict = {
                    'circle': self.circle, 'enm': self.enm, 'type': 'FDD', 'node': node,
                    'gnbid_enbid': site.get_fdn_parameter(fdn=','.join(r.split(',')[:-1]), para='eNBId'),
                    'cellid': site.get_fdn_parameter(fdn=r, para='cellId'),
                    'cell': r.split('=')[-1],
                    'tac': site.get_fdn_parameter(fdn=r, para='tac'),
                    'earfcn': site.get_fdn_parameter(fdn=r, para='earfcn'),
                }
                tmp_list.append(copy.deepcopy(tmp_dict))
        df_cell = pd.DataFrame(tmp_list)
        type_order = ['NR', 'FDD', 'TDD']
        df_cell['type'] = pd.Categorical(df_cell['type'], categories=type_order, ordered=True)
        df_cell = df_cell.sort_values(by='type').reset_index(drop=True)
        return df_cell

    def process_df_site_with_logs_data(self) -> pd.DataFrame:
        tmp_list = []
        for r in self.df_site.itertuples():
            node = r.__getattribute__('node')
            site = self.sites[node]
            tmp_dict = {}
            if len(site.fdns) < 1: tmp_dict |= {'log': False}
            else:
                tmp_dict |= {
                    'log': True if len(site.fdns) > 0 else False,
                    'syncstatus': site.get_fdn_parameter(fdn=F'NetworkElement={node},CmFunction=1', para='syncStatus'),
                    'nr': True if node in self.nr_node else False,
                    'amf': len(self.df_amf.loc[(self.df_amf.node == node)].index),
                    'gNBId': None,
                    'gNBIdLength': None,
                    'lte': True if node in self.lte_node else False,
                    'eNBId': site.get_fdn_parameter(fdn='ENodeBFunction=1', para='eNBId'),
                    'xn_status': site.type_int,
                    'xn_localipzddress': site.xn_ip,
                    'xn_sctpendpoint': site.xn_sctp,
                    'nr_du_Cells': site.du_cell,
                    'nr_cu_Cells': site.cu_cell,
                    'fdd_Cells': site.fdd_cell,
                    'tdd_Cells': site.tdd_cell,
                    'DU_gNBId': site.get_fdn_parameter(fdn='GNBDUFunction=1', para='gNBId'),
                    'CUCP_gNBId': site.get_fdn_parameter(fdn='GNBCUCPFunction=1', para='gNBId'),
                    'CUUP_gNBId': site.get_fdn_parameter(fdn='GNBCUUPFunction=1', para='gNBId'),
                    'DU_gNBIdLength': site.get_fdn_parameter(fdn='GNBDUFunction=1', para='gNBIdLength'),
                    'CUCP_gNBIdLength': site.get_fdn_parameter(fdn='GNBCUCPFunction=1', para='gNBIdLength'),
                    'CUUP_gNBIdLength': site.get_fdn_parameter(fdn='GNBCUUPFunction=1', para='gNBIdLength'),
                }
                if tmp_dict['DU_gNBId'] == tmp_dict['CUCP_gNBId'] == tmp_dict['CUUP_gNBId']:
                    tmp_dict['gNBId'] = tmp_dict['DU_gNBId']
                    del tmp_dict['DU_gNBId'], tmp_dict['CUCP_gNBId'], tmp_dict['CUUP_gNBId']
                if (tmp_dict['DU_gNBIdLength'] == tmp_dict['CUCP_gNBIdLength'] == tmp_dict['CUUP_gNBIdLength']):
                    tmp_dict['gNBIdLength'] = tmp_dict['DU_gNBIdLength']
                    del tmp_dict['DU_gNBIdLength'], tmp_dict['CUCP_gNBIdLength'], tmp_dict['CUUP_gNBIdLength']
                tmp_list.append(tmp_dict)


        new_df = pd.DataFrame(tmp_list)
        return new_df


    def save_different_dataframe(self, *, current_time: str) -> None:
        data = {'Site': self.df_site, 'Cell': self.df_cell, 'AMF': self.df_amf, 'GPL': self.df_gpl,
                'Feature': self.df_feature}
        with ExcelWriter(os.path.join(self.base_dir, F'Script_Status_{current_time}.xlsx')) as writer:
            for key in data:
                df = data.get(key).copy()
                df.reset_index().to_excel(writer, key, index=False)
