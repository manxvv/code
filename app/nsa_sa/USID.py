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
    'FieldReplaceableUnit.(administrativeState,operationalState,productData)',
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
    'McpcPCellNrFreqRelProfileUeCfg', 'McpcPSCellNrFreqRelProfileUeCfg'
]


def highlight_even_row(*, row) -> list:
    return ['background-color: #D2D3D3; border: 1px solid black;' if _ % 2 == 1 else
            'border: 1px solid black;' for _ in range(len(row))]


class USID:
    def __init__(self, *, nsa_sa_path: str, base_dir: str, custom_log: Custom_Log,
                 para_file: list, site_file: str, circle: str, enm: str):
        self.base_dir = base_dir
        self.custom_log = custom_log
        self.circle = circle
        self.enm = enm
        self.log_mos = ';'.join([F'{_}.<w>' if '(' not in _ else _ for _ in dump_list])
        # print(self.log_mos)
        # DB Process
        self.db = self.db_data(nsa_sa_path=nsa_sa_path)
        # Site List Data
        self.df_site = self.site_data(site_file=site_file)
        # Log Data Process
        self.sites = {}
        mos_dict = parse_dynamic_data_to_dict(para_file=para_file)
        for node in list(self.df_site.node.unique()):
            self.sites[node] = Site(node=node, mos=mos_dict.get(node, {}), custom_log=self.custom_log)
        del mos_dict

        # Site List Data Process
        self.df_amf = self.get_amf_table()
        self.df_feature = self.get_feature_table()
        self.df_cell = self.get_cell_table()
        self.df_site = pd.concat([self.df_site, self.process_df_site_with_logs_data()], axis=1)
        self.df_site.reset_index(drop=True, inplace=True)
        self.df_gpl = pd.DataFrame([], columns=['node', 'mo', 'parameter', 'value', 'gpl_value', 'flag', 'remark'])
        self.gpl_list = []
        date_time = datetime.now().strftime("%m%d%Y_%H%M%S")
        self.status_file = os.path.join(self.base_dir, F'Status_{self.circle}_{self.enm}_{date_time}.xlsx')
        self.para_file = os.path.join(self.base_dir, F'Parameter_{self.circle}_{self.enm}_{date_time}.csv')
        self.save_different_dataframe(data=None)

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

    def db_data(self, *, nsa_sa_path):
        db_dict = {
            'TermPointToAmf': ['circle', 'termPointToAmfId', 'ipv6Address1', 'ipv6Address2', 'ipv4Address1', 'ipv4Address2',
                               'administrativeState', 'defaultAmf', 'pwsRestartHandling'],
            'EUtranFreqRelation': ['circle', 'eUtranFreqRelationId', 'allowedMeasBandwidth', 'anrMeasOn', 'cellReselectionPriority',
                                   'eUtranFallbackPrioEc', 'pMaxEUtra', 'presenceAntennaPort1', 'qRxLevMin', 'tReselectionEUtra',
                                   'threshXHighP', 'threshXLowP', 'voicePrio', 'eUtranFrequencyRef', 'mcpcPCellEUtranFreqRelProfileRef',
                                   'trStSaEUtranFreqRelProfileRef', 'ueMCEUtranFreqRelProfileRef', 'UeMCEUtranFreqRelProfileUeCfg_blindRwrAllowed',
                                   'UeMCEUtranFreqRelProfileUeCfg_connModeAllowedPCell', 'UeMCEUtranFreqRelProfileUeCfg_connModePrioPCell'],
            'DU5qi': ['circle', 'dU5qiId', 'aqmMode', 'dscp', 'estimatedE2ERTT', 'logicalChannelGroupId', 'packetDelayBudget',
                      'packetDelayBudgetOffset', 'priorityLevel', 'profile5qi', 'rlcSNLength',
                      'tReassemblyDl', 'tReassemblyUl'], # 'puschRepRef', 'srHandlingRef',
            'CUCP5qi': ['circle', 'cUCP5qiId', 'pdcpSnSize', 'profile5qi', 'rlcMode', 'tPdcpDiscard', 'tReorderingDl', 'tReorderingUl'],
            'CUUP5qi': ['circle', 'cUUP5qiId', 'aqmMode', 'counterActiveMode', 'dcDlPdcpAggrPrioCg', 'dcDlPdcpAggrTimeDiffCg',
                        'dcDlPdcpAggrTimeDiffProhibit', 'dcDlPdcpAggrTimeDiffThresh', 'dscp', 'estimatedE2ERTT',
                        'packetDelayBudget', 'packetDelayBudgetOffset', 'profile5qi', 'tOooUlDelivery'], # 'drbRef',


            'MOC': ['circle', 'sw', 'tech', 'mo', 'parameter', 'value', 'flag'],
        }

        db = {_: pd.DataFrame([], columns=db_dict[_]) for _ in db_dict.keys()}
        for sheet in db_dict.keys():
            df = pd.read_excel(os.path.join(nsa_sa_path, 'DB.xlsx'), sheet_name=sheet, dtype='str')
            df = df[db_dict[sheet]]
            df = df.replace('[^a-zA-Z0-9.,-_/+()[]{}]', '', regex=True)
            df = df.replace({np.nan: None, '': None}, inplace=False).dropna()
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            df = df.loc[(df.circle.isin(['Airtel', self.circle]))]
            df.drop(['circle'], axis=1, inplace=True)
            if sheet == 'MOC':
                df['value'] = df['value'].apply(self.parse_string_to_json)
                df['flag'] = df.flag.str.lower()
                df = df.loc[(df.flag.str.lower().isin(['true']))]
                df = df.groupby(['mo', 'parameter'], sort=False, as_index=False).tail(1)
            df.reset_index(inplace=True, drop=True)
            db[sheet] = df.copy()
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
            # NR Features
            'CXC4012493', 'CXC4012534', 'CXC4012538', 'CXC4012549', 'CXC4012550', 'CXC4012591',
            'CXC4012592', 'CXC4012637', 'CXC4012607', 'CXC4012475', 'CXC4012548', 'CXC4012724',
            'CXC4012680', 'CXC4012688', 'CXC4012601', 'CXC4012330', 'CXC4012406', 'CXC4012510',
            'CXC4012562', 'CXC4012593', 'CXC4012638', 'CXC4012590', 'CXC4012503', 'CXC4012589',
            'CXC4012668', 'CXC4012673', 'CXC4012635',

            # LTE Features
            'CXC4012578', 'CXC4012385', 'CXC4012371', 'CXC4010620', 'CXC4012324', 'CXC4012218',
            'CXC4012580'
        ]
        tmp_list = []
        description_dict = {'circle': '', 'enm': '', 'node': 'description'}
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
        df = pd.DataFrame(tmp_list)
        return df

    def get_cell_table(self) -> pd.DataFrame:
        tmp_list = []
        for node in self.sites.keys():
            siteid = self.df_site.loc[(self.df_site['node'] == node), 'siteid'].iloc[0]
            site = self.sites[node]
            tmp_cu_cell_list = []
            for r in sorted([_ for _ in site.fdns if re.match(".*GNBDUFunction=[^,]*,NRCellDU=([^,]*)$", _)]):
                tmp_dict = {
                    'circle': self.circle, 'enm': self.enm, 'siteid': siteid, 'node': node, 'type': 'NR',
                    'gnbid_enbid': site.get_fdn_parameter(fdn=','.join(r.split(',')[:-1]), para='gNBId'),
                    'cellid': site.get_fdn_parameter(fdn=r, para='cellLocalId'),
                    'tac': site.get_fdn_parameter(fdn=r, para='nRTAC'),
                    'cell': r.split('=')[-1],
                    'cu': None,  'sib2': None, 'sib4': None, 'sib5': None, 'nr_intra_rel': None, 'nr_inter_rel': None,
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
                            'cu': s.split('=')[-1],
                            'sib2': len(intra_rel) > 0,
                            'sib4': len(inter_rel) > 0,
                            'sib5': len([_ for _ in site.fdns if re.match(F'{s},EUtranFreqRelation=([^,]*)$', _)]) > 0,
                            'intra_rel': intra_rel,
                            'inter_rel': inter_rel,
                            'transmitSib2': site.get_fdn_parameter(fdn=s, para='transmitSib2'),
                            'transmitSib4': site.get_fdn_parameter(fdn=s, para='transmitSib4'),
                            'transmitSib5': site.get_fdn_parameter(fdn=s, para='transmitSib5'),
                        }
                tmp_list.append(copy.deepcopy(tmp_dict))
            for s in sorted([_ for _ in site.fdns if re.match(".*GNBCUCPFunction=[^,]*,NRCellCU=([^,]*)$", _)]):
                if s.split('=')[-1] not in tmp_cu_cell_list:
                    freq = site.get_fdn_parameter(fdn=s, para='nRFrequencyRef')
                    relations = [_ for _ in site.fdns if re.match(F'{s},NRFreqRelation=([^,]*)$', _)]
                    intra_rel = [_ for _ in relations if site.get_fdn_parameter(fdn=s, para='nRFrequencyRef') == freq]
                    inter_rel = [_ for _ in relations if site.get_fdn_parameter(fdn=s, para='nRFrequencyRef') != freq]
                    tmp_dict = {
                        'circle': self.circle, 'enm': self.enm, 'siteid': siteid, 'node': node, 'type': 'NR',
                        'cell': None, 'cu': s.split('=')[-1], 'nr_intra_rel': None, 'nr_inter_rel': None,
                        'cellid': site.get_fdn_parameter(fdn=s, para='cellLocalId'),
                        'intra_rel': intra_rel,
                        'inter_rel': inter_rel,
                        'transmitSib2': site.get_fdn_parameter(fdn=s, para='transmitSib2'),
                        'transmitSib4': site.get_fdn_parameter(fdn=s, para='transmitSib4'),
                        'transmitSib5': site.get_fdn_parameter(fdn=s, para='transmitSib5'),
                    }
                    tmp_list.append(copy.deepcopy(tmp_dict))
            for r in sorted([_ for _ in site.fdns if re.match(".*ENodeBFunction=[^,]*,EUtranCell.DD=([^,]*)$", _)]):
                cell_type = r.split(',')[-1].split('=')[0][-3:]
                tmp_dict = {
                    'circle': self.circle, 'enm': self.enm, 'siteid': siteid, 'node': node, 'type': cell_type,
                    'gnbid_enbid': site.get_fdn_parameter(fdn=','.join(r.split(',')[:-1]), para='eNBId'),
                    'cellid': site.get_fdn_parameter(fdn=r, para='cellId'),
                    'cell': r.split('=')[-1],
                    'earfcn': site.get_fdn_parameter(fdn=r, para='earfcndl' if cell_type == 'FDD' else 'earfcn'),
                    'tac': site.get_fdn_parameter(fdn=r, para='tac'),
                }
                tmp_list.append(copy.deepcopy(tmp_dict))
        if len(tmp_list) > 0:
            df_cell = pd.DataFrame(tmp_list)
        else:
            df_cell = pd.DataFrame(tmp_list, columns=[
                'circle', 'enm', 'siteid', 'node', 'type', 'gnbid_enbid', 'cellid', 'tac', 'cell', 'cu', 'sib2', 'sib4',
                'sib5', 'nr_intra_rel', 'nr_inter_rel', 'ssbFrequency', 'ssbSubCarrierSpacing', 'ssbPeriodicity', 'ssbOffset',
                'ssbDuration', 'intra_rel', 'inter_rel', 'transmitSib2', 'transmitSib4', 'transmitSib5', 'earfcn'])
        return df_cell

    def process_df_site_with_logs_data(self) -> pd.DataFrame:
        tmp_list = []
        site_with_cell_config_issue_sites = self.df_cell.loc[((self.df_cell.type.isin(['NR'])) &
                                                              ((self.df_cell.cell.isna()) | (self.df_cell.cu.isna())))].siteid.unique()
        for r in self.df_site.itertuples():
            siteid = r.__getattribute__('siteid')
            node = r.__getattribute__('node')
            site = self.sites[node]
            tmp_dict = {}
            if not hasattr(site, 'fdns') or len(site.fdns) < 1: tmp_dict |= {'status': False, 'remark': 'No Site Found in log File',
                                                                             'log': False, 'nr': False, 'lte': False}
            else:
                tmp_dict |= {
                    'status': False if siteid in site_with_cell_config_issue_sites else True,
                    'remark': 'Config Issue' if siteid in site_with_cell_config_issue_sites else None,
                    'log': True if len(site.fdns) > 0 else False,
                    'nr': len(self.df_cell.loc[((self.df_cell['node'] == node) & (self.df_cell.type.isin(['NR'])))].index) > 0,
                    'lte': len(self.df_cell.loc[((self.df_cell['node'] == node) & (self.df_cell.type.isin(['FDD', 'TDD'])))].index) > 0,
                    'amf': len(self.df_amf.loc[(self.df_amf.node == node)].index),
                    'syncstatus': site.get_fdn_parameter(fdn=F'NetworkElement={node},CmFunction=1', para='syncStatus'),
                    'gNBId': None,
                    'gNBIdLength': None,
                    'eNBId': site.get_fdn_parameter(fdn='ENodeBFunction=1', para='eNBId'),
                    'xn_status': site.type_int,
                    'xn_localipzddress': site.xn_ip,
                    'xn_sctpendpoint': site.xn_sctp,
                    'nr_du_Cells': site.get_du_cell(),
                    'nr_cu_Cells': site.get_cu_cell(),
                    'fdd_Cells': site.get_fdd_cell(),
                    'tdd_Cells': site.get_tdd_cell(),
                    'DU_gNBId': site.get_fdn_parameter(fdn='GNBDUFunction=1', para='gNBId'),
                    'CUCP_gNBId': site.get_fdn_parameter(fdn='GNBCUCPFunction=1', para='gNBId'),
                    'CUUP_gNBId': site.get_fdn_parameter(fdn='GNBCUUPFunction=1', para='gNBId'),
                    'DU_gNBIdLength': site.get_fdn_parameter(fdn='GNBDUFunction=1', para='gNBIdLength'),
                    'CUCP_gNBIdLength': site.get_fdn_parameter(fdn='GNBCUCPFunction=1', para='gNBIdLength'),
                    'CUUP_gNBIdLength': site.get_fdn_parameter(fdn='GNBCUUPFunction=1', para='gNBIdLength'),
                    'bbu': site.bbu,
                }
                if tmp_dict['DU_gNBId'] == tmp_dict['CUCP_gNBId'] == tmp_dict['CUUP_gNBId']:
                    tmp_dict['gNBId'] = tmp_dict['DU_gNBId']
                    del tmp_dict['DU_gNBId'], tmp_dict['CUCP_gNBId'], tmp_dict['CUUP_gNBId']
                if (tmp_dict['DU_gNBIdLength'] == tmp_dict['CUCP_gNBIdLength'] == tmp_dict['CUUP_gNBIdLength']):
                    tmp_dict['gNBIdLength'] = tmp_dict['DU_gNBIdLength']
                    del tmp_dict['DU_gNBIdLength'], tmp_dict['CUCP_gNBIdLength'], tmp_dict['CUUP_gNBIdLength']
                tmp_dict['status'] = tmp_dict['status'] and tmp_dict['log'] and (tmp_dict['nr'] or tmp_dict['lte'])
            tmp_list.append(tmp_dict)
        if len(tmp_list) > 0:
            new_df = pd.DataFrame(tmp_list)
        else:
            new_df = pd.DataFrame(tmp_list, columns=[
                'status', 'remark', 'log', 'nr', 'lte', 'amf', 'syncstatus', 'gNBId',
                'gNBIdLength', 'eNBId', 'xn_status', 'xn_localipzddress',
                'xn_sctpendpoint', 'nr_du_Cells', 'nr_cu_Cells', 'fdd_Cells',
                'tdd_Cells', 'bbu'
            ])
        print(new_df.columns)
        return new_df

    def save_different_dataframe(self, *, data: dict = None) -> None:
        if data is None:
            data = {'Site': self.df_site, 'Cell': self.df_cell, 'AMF': self.df_amf, 'Feature': self.df_feature}
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
        if os.path.exists(self.status_file):
            audit_file = pd.ExcelWriter(self.status_file, engine='openpyxl', mode='a')
        else:
            audit_file = pd.ExcelWriter(self.status_file, engine='openpyxl', mode='w')
        for sheet_name in data.keys():
            df = data.get(sheet_name).copy()
            df_style = df.style.apply(lambda x: highlight_even_row(row=x))
            df_style.to_excel(excel_writer=audit_file, sheet_name=sheet_name, index=False)
            audit_file.sheets[sheet_name].auto_filter.ref = audit_file.sheets[sheet_name].calculate_dimension()
            audit_file.sheets[sheet_name].auto_filter.enable = True
        audit_file.close()

    def save_parameter_data_in_csv_file(self, *, df: pd.DataFrame = None) -> None:
        if df is None or len(df.index) < 1: return
        df.to_csv(self.para_file, index=False)
