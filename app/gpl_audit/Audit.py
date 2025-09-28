import re
import os
import pandas as pd
from AuditUSID import AuditUSID
from AuditReport import audit_report_complete_site


class Audit:
    def __init__(self, *, a_usid: AuditUSID, node: str):
        self.node = node
        self.a_usid = a_usid
        self.site = self.a_usid.sites[self.node]
        self.me = self.site.me
        self.set_node_site_and_para_for_dcgk(node)
        self.tech = 'NR'
        self.gpl_list = []
        self.gpl_completed_mo_para = []

    @staticmethod
    def compare_current_and_gs_value(*, value, gpl) -> bool:
        if type(value) not in (dict, str, list): value = str(value)
        if value == 'None' and gpl == '': return True
        if type(value) is list and (sum([type(_) is dict for _ in value]) == len(value)) and \
                type(gpl) is list and (sum([type(_) is dict for _ in gpl]) == len(gpl)):
            return set([str(_) for _ in value]).difference(set([str(_) for _ in gpl])) == \
                set([str(_) for _ in gpl]).difference(set([str(_) for _ in value]))
        return value == gpl

    def add_mo_para_to_para_list(self, *, ldn: str, para: str, gpl, para_type: str = None, remark: str = None) -> None:
        def add_mo_para() -> None:
            if F'{self.node}.{ldn}.{para}' not in self.gpl_completed_mo_para:
                self.gpl_list.append({
                    'Node': self.node,
                    'Technology': self.tech,
                    'MO_Class': self.get_end_moc(ldn),
                    'Parameter': para,
                    'MO': ldn,
                    'Current_Value': value,
                    'Baseline': gpl,
                    'Deviation': flag,
                    'Parameter_Type': para_type,
                    'remark': remark
                })
                self.gpl_completed_mo_para.append(F'{self.node}.{ldn}.{para}')
            else:
                self.a_usid.custom_log.log.exception(F'{self.node}.{ldn}.{para} -- has already been audited.')

        value, flag = None, False
        if self.site.fdn_exists(fdn=ldn):
            if para in self.site.mos.get(ldn, {}).keys():
                value = self.site.get_fdn_parameter(fdn=ldn, para=para)
            else: value, remark = 'NF', 'Parameter not found'
        else: value, remark = None, 'MO not found'
        if remark == 'NA': flag = 'NA'
        elif self.compare_current_and_gs_value(value=value, gpl=gpl): flag = 'NO'
        else: flag = 'YES'
        add_mo_para()

    def set_node_site_and_para_for_dcgk(self, node):
        self.node = node
        self.site = self.a_usid.sites[self.node]
        self.me = self.site.me

    def run(self):
        if self.node in self.a_usid.nr_node:
            self.nr_parameter_audit()
        if self.node in self.a_usid.lte_node:
            self.lte_parameter_audit()
        if len(self.gpl_list) > 0:
            self.a_usid.df_gpl = pd.concat([self.a_usid.df_gpl, pd.DataFrame(self.gpl_list)],
                                           axis=0, ignore_index=True)

    def run_all_parameters_audit(self) -> None:
        self.add_all_parameters_audit()
        df = pd.DataFrame(self.gpl_list)
        audit_report_complete_site(df=df, node=self.node, base_dir=self.a_usid.base_dir)

    @staticmethod
    def get_end_moc(mo: str) -> str: return mo.split(',')[-1].split('=')[0]

    @staticmethod
    def get_moc_id(moc: str) -> str: return moc[0].lower() + moc[1:] + 'Id'

    @staticmethod
    def null_flag(*, val: object) -> bool: return str(val) in ['None', 'null', 'empty', '', '""', '[]', '{}']

    @staticmethod
    def non_null_flag(*, val: object) -> bool: return str(val) not in ['None', 'null', 'empty', '', '""', '[]', '{}']

    def cmedit_cli_norm_value(self, val):
        """
        Special Character --- *()[]\+<>= and space
        Special characters are any characters other than the supported characters.
        These characters must be wrapped in quotes to be accepted in the scope name or attribute value part of the command.
        *()[]\+<>= and space - Special C
        :rtype: str
        """
        if type(val) in [int, bool]: val = str(val).lower()
        if type(val) == dict and val.get('attributes', {}).get('xc:operation', '') == 'delete':
            return '<empty>'
        elif type(val) == list and len(val) == 0:
            return "[]"
        elif type(val) == dict and len(val) == 0:
            return "{}"
        elif type(val) in [dict, list] and len(val) == 0:
            return '<empty>'
        elif type(val) not in [dict, list] and len(val) == 0:
            return '<empty>'
        elif type(val) == dict:
            return '{' + ', '.join([F"{key}={self.cmedit_cli_norm_value(val.get(key))}" for key in val]) + '}'
        elif type(val) == list:
            return '[' + ', '.join([self.cmedit_cli_norm_value(_) for _ in val]) + ']'
        elif val in ['null', 'empty']:
            return F'<{val}>'
        elif len([_ for _ in ['{', '[', '('] if str(val).startswith(_)]) > 0:
            return val
        elif re.match('(.*)\s\((.*)\)$', val):
            return re.match('(.*)\s\((.*)\)$', val).group(2)
        elif re.match('(.*),(.*)=(.*)$', val) and 'ManagedElement=' not in val:
            return F'"{self.me},{val}"'
        elif re.match('(.*),(.*)=(.*)$', val) and 'SubNetwork=' not in val and 'ManagedElement=' in val:
            return F'"{self.me},{re.match(".*ManagedElement=([^,]*),(.*)$", val).group(2)}"'
        elif len([_ for _ in ['*', '(', ')', '[', ']', '\\', '+', '<', '>', '=', ' ', ',', ':'] if _ in str(val)]) > 0:
            return F'"{val}"'
        else:
            return val

    def nr_parameter_audit(self):
        self.tech = 'NR'
        if self.node not in self.a_usid.nr_node: return
        skip_moc_list = ['NRCellDU', 'NRCellCU',
                         'EUtranFreqRelation', 'EUtranCellRelation',
                         'NRFreqRelation', 'NRCellRelation']
        df_tmp = self.a_usid.db['MOC'].copy(deep=True)
        df_tmp = df_tmp.loc[(df_tmp.tech == self.tech)]
        for r in df_tmp.loc[((~df_tmp.mo.isin(skip_moc_list)) & (df_tmp.mo.str.contains('=')))].itertuples():
            self.add_mo_para_to_para_list(
                ldn=r.__getattribute__('mo'),
                para=r.__getattribute__('parameter'),
                gpl=r.__getattribute__('value'),
                para_type=r.__getattribute__('para_type')
            )
        # NRCellDU
        for ldn in sorted([_ for _ in self.site.fdns if re.match(F".*GNBDUFunction=1,NRCellDU=([^,]*)$", _)]):
            for r in df_tmp.loc[(df_tmp.mo.isin(['NRCellDU']))].itertuples():
                self.add_mo_para_to_para_list(
                    ldn=ldn,
                    para=r.__getattribute__('parameter'),
                    gpl=r.__getattribute__('value'),
                    para_type=r.__getattribute__('para_type')
                )
        # NRCellCU
        for ldn in sorted([_ for _ in self.site.fdns if re.match(F".*GNBCUCPFunction=1,NRCellCU=([^,]*)$", _)]):
            cell = ldn.split('=')[-1]
            remark_dict = {'Sib2': None, 'Sib4': None, 'Sib5': None, }
            if len(self.a_usid.df_cell.loc[(self.a_usid.df_cell.CU == cell)].index) > 0:
                if self.a_usid.df_cell.loc[(self.a_usid.df_cell.CU == cell), 'sib2'].iloc[0] is False:
                    remark_dict['Sib2'] = 'NR-NR Intra Freq Relations Doesnot Exist'
                if self.a_usid.df_cell.loc[(self.a_usid.df_cell.CU == cell), 'sib4'].iloc[0] is False:
                    remark_dict['Sib4'] = 'NR-NR Inter Freq Relations Doesnot Exist'
                if self.a_usid.df_cell.loc[(self.a_usid.df_cell.CU == cell), 'sib5'].iloc[0] is False:
                    remark_dict['Sib5'] = 'NR-LTE Freq Relations Doesnot Exist'
            else:
                remark_dict = {
                    'Sib2': 'Wrong Cell Configuration(localcellid)',
                    'Sib4': 'Wrong Cell Configuration(localcellid)',
                    'Sib5': 'Wrong Cell Configuration(localcellid)'
                }
            for r in df_tmp.loc[(df_tmp.mo.isin(['NRCellCU']))].itertuples():
                if r.__getattribute__('parameter') not in ['transmitSib2', 'transmitSib4', 'transmitSib5']:
                    self.add_mo_para_to_para_list(
                        ldn=ldn,
                        para=r.__getattribute__('parameter'),
                        gpl=r.__getattribute__('value'),
                        para_type=r.__getattribute__('para_type')
                    )
                else:
                    self.add_mo_para_to_para_list(
                        ldn=ldn,
                        para=r.__getattribute__('parameter'),
                        gpl=r.__getattribute__('value'),
                        para_type=r.__getattribute__('para_type'),
                        remark=remark_dict.get(r.__getattribute__('parameter')[-4:])
                    )
        para_type = 'LMS'
        # NRCellCU,NRFreqRelation,ueMCNrFreqRelProfileRef,mcpcPCellNrFreqRelProfileRef
        # NRCellCU,NRCellRelation,isHoAllowed
        for moc in ['NRFreqRelation', 'NRCellRelation']:
            for ldn in sorted([_ for _ in self.site.fdns if re.match(F".*GNBCUCPFunction=1,NRCellCU=[^,]*,{moc}=([^,]*)$", _)]):
                for r in df_tmp.loc[(df_tmp.mo.isin([moc]))].itertuples():
                    self.add_mo_para_to_para_list(
                        ldn=ldn,
                        para=r.__getattribute__('parameter'),
                        gpl=r.__getattribute__('value'),
                        para_type=r.__getattribute__('para_type')
                    )
        # UeMCEUtranFreqRelProfile, EUtranFreqRelation
        tmp_list = ['UeMCEUtranFreqRelProfileUeCfg_blindRwrAllowed', 'UeMCEUtranFreqRelProfileUeCfg_connModeAllowedPCell',
                    'UeMCEUtranFreqRelProfileUeCfg_connModePrioPCell']
        tmp_list2 = [
            'allowedMeasBandwidth', 'anrMeasOn', 'cellReselectionPriority', 'eUtranFallbackPrioEc', 'pMaxEUtra', 'presenceAntennaPort1',
            'qRxLevMin', 'tReselectionEUtra', 'threshXHighP', 'threshXLowP', 'voicePrio',
            'mcpcPCellEUtranFreqRelProfileRef', 'trStSaEUtranFreqRelProfileRef', 'ueMCEUtranFreqRelProfileRef'
        ]
        for r in self.a_usid.db['EUtranFreqRelation'].itertuples():
            ldn = r.__getattribute__('ueMCEUtranFreqRelProfileRef') + ',UeMCEUtranFreqRelProfileUeCfg=Base'
            tmp_dict = {mo_para.split('_')[-1]: r.__getattribute__(mo_para) for mo_para in tmp_list}
            for para in tmp_dict.keys():
                self.add_mo_para_to_para_list(ldn=ldn, para=para, gpl=tmp_dict.get(para), para_type=para_type)
            tmp_dict = {mo_para.split('_')[-1]: r.__getattribute__(mo_para) for mo_para in tmp_list2}
            id = r.__getattribute__('eUtranFreqRelationId')
            for ldn in sorted([_ for _ in self.site.fdns if re.match(F".*GNBCUCPFunction=1,NRCellCU=([^,]*),EUtranFreqRelation={id}$", _)]):
                for para in tmp_dict.keys():
                    self.add_mo_para_to_para_list(ldn=ldn, para=para, gpl=tmp_dict.get(para), para_type=para_type)
        # NRCellCU,EUtranCellRelation,isHoAllowed
        for ldn in sorted([_ for _ in self.site.fdns if re.match(F".*GNBCUCPFunction=1,NRCellCU=[^,]*,EUtranCellRelation=([^,]*)$", _)]):
            for r in df_tmp.loc[(df_tmp.mo.isin(['EUtranCellRelation']))].itertuples():
                self.add_mo_para_to_para_list(
                    ldn=ldn,
                    para=r.__getattribute__('parameter'),
                    gpl=r.__getattribute__('value'),
                    para_type=r.__getattribute__('para_type')
                )

        # For all Other MOCs
        for r in df_tmp.loc[((~df_tmp.mo.isin(skip_moc_list)) & (~df_tmp.mo.str.contains('=')))].itertuples():
            for ldn in sorted([_ for _ in self.site.fdns if re.match(F".*{r.__getattribute__('mo')}=([^,]*)$", _)]):
                self.add_mo_para_to_para_list(
                    ldn=ldn,
                    para=r.__getattribute__('parameter'),
                    gpl=r.__getattribute__('value'),
                    para_type=r.__getattribute__('para_type')
                )

    def lte_parameter_audit(self):
        self.tech = 'LTE'
        if self.node not in self.a_usid.lte_node: return
        df_tmp = self.a_usid.db['MOC'].copy(deep=True)
        df_tmp = df_tmp.loc[(df_tmp.tech == self.tech)]

        skip_moc_list = ['UePolicyOptimization', 'EUtranCellFDD', 'EUtranCellTDD',
                         'UeMeasControl', 'ReportConfigB1NR', 'GUtranFreqRelation']
        for r in df_tmp.loc[((~df_tmp.mo.isin(skip_moc_list)) & (df_tmp.mo.str.contains('=')))].itertuples():
            self.add_mo_para_to_para_list(
                ldn=r.__getattribute__('mo'),
                para=r.__getattribute__('parameter'),
                gpl=r.__getattribute__('value'),
                para_type=r.__getattribute__('para_type')
            )
        # For all Other MOs
        for r in df_tmp.loc[(~(df_tmp.mo.str.contains('=')))].itertuples():
            for ldn in sorted([_ for _ in self.site.fdns if
                               re.match(F".*ENodeBFunction=1.*,{r.__getattribute__('mo')}=([^,]*)$", _)]):
                self.add_mo_para_to_para_list(
                    ldn=ldn,
                    para=r.__getattribute__('parameter'),
                    gpl=r.__getattribute__('value'),
                    para_type=r.__getattribute__('para_type')
                )

    def add_all_parameters_audit(self):
        for ldn in self.site.fdns:
            if ldn in ['me_me']: continue
            for para in self.site.mos[ldn]:
                self.add_mo_para_to_para_list(ldn=ldn, para=para, gpl=None, para_type=None, remark='NA')
