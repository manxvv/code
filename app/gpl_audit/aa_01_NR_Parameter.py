import copy
import numpy as np
from Audit import Audit
import re


class aa_01_NR_Parameter(Audit):
    def create_rpc_msg(self):
        self.tech = 'NR'
        if self.node not in self.audit_usid.nr_node: return
        skip_moc_list = ['NRCellDU', 'NRCellCU', 'EUtranFreqRelation', 'NRFreqRelation',
                         'NRCellRelation', 'NRCellRelation']
        df_tmp = self.audit_usid.db['MOC'].copy(deep=True)
        # print(len(df_tmp.index))
        df_tmp = df_tmp.loc[(df_tmp.tech == self.tech)]
        # print(len(self.audit_usid.db['MOC'].index))
        # print(len(df_tmp.index))
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
            if len(self.audit_usid.df_cell.loc[(self.audit_usid.df_cell.CU == cell)].index) > 0:
                if self.audit_usid.df_cell.loc[(self.audit_usid.df_cell.CU == cell), 'sib2'].iloc[0] is False:
                    remark_dict['Sib2'] = 'Intra Freq Relations Doesnot Exist'
                if self.audit_usid.df_cell.loc[(self.audit_usid.df_cell.CU == cell), 'sib4'].iloc[0] is False:
                    remark_dict['Sib4'] = 'Intra Freq Relations Doesnot Exist'
                if self.audit_usid.df_cell.loc[(self.audit_usid.df_cell.CU == cell), 'sib5'].iloc[0] is False:
                    remark_dict['Sib5'] = 'Intra Freq Relations Doesnot Exist'
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
        for ldn in sorted([_ for _ in self.site.fdns if re.match(F".*GNBCUCPFunction=1,NRCellCU=[^,]*,NRFreqRelation=([^,]*)$", _)]):
            for r in df_tmp.loc[(df_tmp.mo.isin(['NRFreqRelation']))].itertuples():
                self.add_mo_para_to_para_list(
                    ldn=ldn,
                    para=r.__getattribute__('parameter'),
                    gpl=r.__getattribute__('value'),
                    para_type=r.__getattribute__('para_type')
                )
        # NRCellCU,NRCellRelation,isHoAllowed
        for ldn in sorted([_ for _ in self.site.fdns if re.match(F".*GNBCUCPFunction=1,NRCellCU=[^,]*,NRCellRelation=([^,]*)$", _)]):
            for r in df_tmp.loc[(df_tmp.mo.isin(['NRCellRelation']))].itertuples():
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
        for r in self.audit_usid.db['EUtranFreqRelation'].itertuples():
            ldn = r.__getattribute__('ueMCEUtranFreqRelProfileRef') + ',UeMCEUtranFreqRelProfileUeCfg=Base'
            tmp_dict = {mo_para.split('_')[-1]: r.__getattribute__(mo_para) for mo_para in tmp_list}
            for para in tmp_dict.keys():
                self.add_mo_para_to_para_list(ldn=ldn, para=para, gpl=tmp_dict.get(para), para_type=para_type)
            tmp_dict = {mo_para.split('_')[-1]: r.__getattribute__(mo_para) for mo_para in tmp_list2}
            for ldn in sorted([_ for _ in self.site.fdns if re.match(F".*GNBCUCPFunction=1,NRCellCU=[^,]*,EUtranFreqRelation=([^,]*)$", _)]):
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

    @staticmethod
    def create_mo_dict_from_mo(*, mo: str, para_dict: dict) -> dict:
        mo_dict = {}
        current_level = mo_dict
        my_list = mo.split(',')
        for index, t in enumerate(my_list):
            moc = [_.strip() for _ in t.split('=')]
            if moc[0] not in current_level:
                current_level[moc[0]] = {moc[0][0].lower() + moc[0][1:] + 'Id': moc[1]}
                if index == len(my_list) - 1:
                    current_level[moc[0]] |= {'attributes': {'xc:operation': 'update'}}
                    current_level[moc[0]] |= para_dict
            current_level = current_level[moc[0]]
        return mo_dict
