import copy
import numpy as np
from Script import Script
import re


class aa_04_Parameter(Script):
    def create_rpc_msg(self):
        self.nr_parameter_update()
        self.lte_parameter_update()

    def nr_parameter_update(self):
        if not self.site_dict['nr']: return
        df_tmp = self.usid.db['MOC'].copy(deep=True)
        df_tmp = df_tmp.loc[(df_tmp.tech.isin(['NR']))]
        # Logically Implemented for feature
        if len(self.site.get_fdd_cell() + self.site.get_tdd_cell()) > 0:
            mo, = 'SystemFunctions=1,Lm=1,FeatureState=CXC4012503',
            para, gpl = 'featureState', 'ACTIVATED'
            self.mo_dict[F'{mo}_{para}-{gpl}'] = {'managedElementId': self.node}
            self.mo_dict[F'{mo}_{para}-{gpl}'].update(self.create_mo_dict_from_mo(mo=mo, para_dict={para: gpl}))

        # Para setting for complete MOs
        for r in df_tmp.loc[(df_tmp.mo.str.contains('='))].itertuples():
            mo, para, gpl = r.__getattribute__('mo'), r.__getattribute__('parameter'), r.__getattribute__('value')
            self.mo_dict[F'{mo}_{para}-{gpl}'] = {'managedElementId': self.node}
            self.mo_dict[F'{mo}_{para}-{gpl}'].update(self.create_mo_dict_from_mo(mo=mo, para_dict={para: gpl}))

        # UeMCEUtranFreqRelProfile
        self.mo_dict['UeMCEUtranFreqRelProfile'] = {'managedElementId': self.node, 'GNBCUCPFunction': {
            'gNBCUCPFunctionId': '1', 'UeMC': {'ueMCId': '1', 'UeMCEUtranFreqRelProfile': []}}}
        mo_ids = []
        tmp_list = ['UeMCEUtranFreqRelProfileUeCfg_blindRwrAllowed', 'UeMCEUtranFreqRelProfileUeCfg_connModeAllowedPCell',
                    'UeMCEUtranFreqRelProfileUeCfg_connModePrioPCell']
        for r in self.usid.db['EUtranFreqRelation'].itertuples():
            mo_id = r.__getattribute__('ueMCEUtranFreqRelProfileRef').split('=')[-1]
            if mo_id not in mo_ids:
                mo_ids += [mo_id]
                tmp_dict = {mo_para.split('_')[-1]: r.__getattribute__(mo_para) for mo_para in tmp_list}
                if len(tmp_dict.keys()) > 0:
                    tmp_dict |= {'attributes': {'xc:operation': 'update'}, 'ueMCEUtranFreqRelProfileUeCfgId': 'Base'}
                    self.mo_dict['UeMCEUtranFreqRelProfile']['GNBCUCPFunction']['UeMC']['UeMCEUtranFreqRelProfile'].append({
                        'ueMCEUtranFreqRelProfileId': mo_id, 'UeMCEUtranFreqRelProfileUeCfg': copy.deepcopy(tmp_dict)})

        # NRCellDU
        tmp_dict = {}
        for r in df_tmp.loc[(df_tmp.mo.isin(['NRCellDU']))].itertuples():
            tmp_dict[r.__getattribute__('parameter')] = r.__getattribute__('value')
        for cell in self.site.get_du_cell():
            mo = F'GNBDUFunction=1,NRCellDU={cell}'
            for r in tmp_dict.keys():
                self.mo_dict[F'{mo}{r}'] = {
                    'managedElementId': self.node,
                    'GNBDUFunction': {
                        'gNBDUFunctionId': '1',
                        'NRCellDU': {
                            'attributes': {'xc:operation': 'update'}, 'nRCellDUId': cell,
                            r: tmp_dict[r]
                        }
                    }
                }
        # NRCellCU
        tmp_dict = {}
        for r in df_tmp.loc[(df_tmp.mo.isin(['NRCellCU']))].itertuples():
            if r.__getattribute__('parameter') in ['transmitSib2', 'transmitSib4', 'transmitSib5']: continue
            tmp_dict[r.__getattribute__('parameter')] = r.__getattribute__('value')
        for cell in self.site.get_cu_cell():
            mo = F'GNBCUCPFunction=1,NRCellCU={cell}'
            for r in tmp_dict.keys():
                self.mo_dict[F'{mo}{r}'] = {'managedElementId': self.node, 'GNBCUCPFunction': {
                    'gNBCUCPFunctionId': '1', 'NRCellCU': {'nRCellCUId': cell, 'attributes': {'xc:operation': 'update'}, r: tmp_dict[r]}}}
            if self.usid.df_cell.loc[(self.usid.df_cell.cu == cell), 'sib2'].iloc[0]:
                self.mo_dict[F'{mo}--transmitSib2'] = {'managedElementId': self.node, 'GNBCUCPFunction': {
                    'gNBCUCPFunctionId': '1', 'NRCellCU': {'nRCellCUId': cell, 'attributes': {'xc:operation': 'update'}, 'transmitSib2': 'true'}}}
            if self.usid.df_cell.loc[(self.usid.df_cell.cu == cell), 'sib4'].iloc[0]:
                self.mo_dict[F'{mo}--transmitSib4'] = {'managedElementId': self.node, 'GNBCUCPFunction': {
                    'gNBCUCPFunctionId': '1', 'NRCellCU': {'nRCellCUId': cell, 'attributes': {'xc:operation': 'update'}, 'transmitSib4': 'true'}}}
            if (self.usid.df_cell.loc[(self.usid.df_cell.cu == cell), 'sib5'].iloc[0] or
                    len(self.usid.db['EUtranFreqRelation'].index) > 0):
                self.mo_dict[F'{mo}--transmitSib5'] = {'managedElementId': self.node, 'GNBCUCPFunction': {
                    'gNBCUCPFunctionId': '1', 'NRCellCU': {'nRCellCUId': cell, 'attributes': {'xc:operation': 'update'}, 'transmitSib5': 'true'}}}

        # NRCellCU,NRFreqRelation,ueMCNrFreqRelProfileRef,mcpcPCellNrFreqRelProfileRef
        for cell in self.site.get_cu_cell():
            mo = F'GNBCUCPFunction=1,NRCellCU={cell}'
            tmp_list = []
            for s in sorted([_ for _ in self.site.fdns if re.match(F".*{mo},NRFreqRelation=([^,]*)$", _)]):
                tmp_list.append({
                    'attributes': {'xc:operation': 'update'}, 'nRFreqRelationId': s.split('=')[-1],
                    'ueMCNrFreqRelProfileRef': 'GNBCUCPFunction=1,UeMC=1,UeMCNrFreqRelProfile=Midband',
                    'mcpcPCellNrFreqRelProfileRef': 'GNBCUCPFunction=1,Mcpc=1,McpcPCellNrFreqRelProfile=Default',
                })
            if len(tmp_list) > 0:
                self.mo_dict[F'{mo},NRFreqRelation=all_mos-ueMCNrFreqRelProfileRef'] = {'managedElementId': self.node, 'GNBCUCPFunction': {
                    'gNBCUCPFunctionId': '1', 'NRCellCU': {'nRCellCUId': cell, 'NRFreqRelation': copy.deepcopy(tmp_list)}}}

        # NRCellCU,NRCellRelation,isHoAllowed
        for cell in self.site.get_cu_cell():
            mo = F'GNBCUCPFunction=1,NRCellCU={cell}'
            tmp_list = []
            for s in sorted([_ for _ in self.site.fdns if re.match(F".*{mo},NRCellRelation=([^,]*)$", _)]):
                tmp_list.append({'attributes': {'xc:operation': 'update'}, 'nRCellRelationId': s.split('=')[-1], 'isHoAllowed': 'true'})
            if len(tmp_list) > 0: continue
            self.mo_dict[F'{mo},NRCellRelation=all_mos-ueMCNrFreqRelProfileRef'] = {'managedElementId': self.node, 'GNBCUCPFunction': {
                'gNBCUCPFunctionId': '1', 'NRCellCU': {'nRCellCUId': cell, 'NRCellRelation': copy.deepcopy(tmp_list)}
            }}

        # NRCellCU,EUtranFreqRelation,anrMeasOn
        for cell in self.site.get_cu_cell():
            mo = F'GNBCUCPFunction=1,NRCellCU={cell}'
            tmp_list = []
            for s in sorted([_ for _ in self.site.fdns if re.match(F".*{mo},EUtranFreqRelation=([^,]*)$", _)]):
                tmp_list.append({'attributes': {'xc:operation': 'update'}, 'eUtranFreqRelationId': s.split('=')[-1], 'anrMeasOn': 'true'})
            if len(tmp_list) > 0: continue
            self.mo_dict[F'{mo},EUtranFreqRelation=all_mos-anrMeasOn'] = {'managedElementId': self.node, 'GNBCUCPFunction': {
                'gNBCUCPFunctionId': '1', 'NRCellCU': {'nRCellCUId': cell, 'EUtranFreqRelation': copy.deepcopy(tmp_list)}
            }}

        # NRCellCU,EUtranCellRelation,isHoAllowed
        for cell in self.site.get_cu_cell():
            mo = F'GNBCUCPFunction=1,NRCellCU={cell}'
            tmp_list = []
            for s in sorted([_ for _ in self.site.fdns if re.match(F".*{mo},EUtranCellRelation=([^,]*)$", _)]):
                tmp_list.append({'attributes': {'xc:operation': 'update'}, 'eUtranCellRelationId': s.split('=')[-1], 'isHoAllowed': 'true'})
            if len(tmp_list) > 0: continue
            self.mo_dict[F'{mo},EUtranCellRelation=all_mos-ueMCNrFreqRelProfileRef'] = {'managedElementId': self.node, 'GNBCUCPFunction': {
                'gNBCUCPFunctionId': '1', 'NRCellCU': {'nRCellCUId': cell, 'EUtranCellRelation': copy.deepcopy(tmp_list)}
            }}

    def lte_parameter_update(self):
        if not self.site_dict['lte']: return
        df_tmp = self.usid.db['MOC'].copy(deep=True)
        df_tmp = df_tmp.loc[(df_tmp.tech.isin(['LTE']))]
        # Para setting for complete MOs
        for r in df_tmp.loc[(df_tmp.mo.str.contains('='))].itertuples():
            mo, para, gpl = r.__getattribute__('mo'), r.__getattribute__('parameter'), r.__getattribute__('value')
            self.mo_dict[F'{mo}_{para}-{gpl}'] = {'managedElementId': self.node}
            self.mo_dict[F'{mo}_{para}-{gpl}'].update(self.create_mo_dict_from_mo(mo=mo, para_dict={para: gpl}))

        # NRCellCU,NRFreqRelation,ueMCNrFreqRelProfileRef,mcpcPCellNrFreqRelProfileRef
        for moc in ['EUtranCellFDD', 'EUtranCellTDD']:
            for s in sorted([_ for _ in self.site.fdns if
                             re.match(F".*ENodeBFunction=1,{moc}=([^,]*)$", _)]):
                for r in df_tmp.loc[(df_tmp.mo == moc)].itertuples():
                    mo, para, gpl = r.__getattribute__('mo'), r.__getattribute__('parameter'), r.__getattribute__('value')
                    self.mo_dict[F'{s}_{para}-{gpl}'] = {'managedElementId': self.node}
                    self.mo_dict[F'{s}_{para}-{gpl}'].update(self.create_mo_dict_from_mo(mo=s, para_dict={para: gpl}))
                # moc_child = 'UeMeasControl'
                mo_child = F'{s},UeMeasControl=1'
                for r in df_tmp.loc[(df_tmp.mo == 'UeMeasControl')].itertuples():
                    mo, para, gpl = r.__getattribute__('mo'), r.__getattribute__('parameter'), r.__getattribute__('value')
                    self.mo_dict[F'{mo_child}_{para}-{gpl}'] = {'managedElementId': self.node}
                    self.mo_dict[F'{mo_child}_{para}-{gpl}'].update(self.create_mo_dict_from_mo(mo=mo_child, para_dict={para: gpl}))
                mo_child = F'{s},UeMeasControl=1,ReportConfigB1NR=1'
                for r in df_tmp.loc[(df_tmp.mo == 'ReportConfigB1NR')].itertuples():
                    mo, para, gpl = r.__getattribute__('mo'), r.__getattribute__('parameter'), r.__getattribute__('value')
                    self.mo_dict[F'{mo_child}_{para}-{gpl}'] = {'managedElementId': self.node}
                    self.mo_dict[F'{mo_child}_{para}-{gpl}'].update(self.create_mo_dict_from_mo(mo=mo_child, para_dict={para: gpl}))
                for ss in sorted([_ for _ in self.site.fdns if
                                   re.match(F"{s},GUtranFreqRelation=([^,]*)$", _)]):
                    for r in df_tmp.loc[(df_tmp.mo == 'GUtranFreqRelation')].itertuples():
                        mo, para, gpl = r.__getattribute__('mo'), r.__getattribute__('parameter'), r.__getattribute__('value')
                        self.mo_dict[F'{ss}_{para}-{gpl}'] = {'managedElementId': self.node}
                        self.mo_dict[F'{ss}_{para}-{gpl}'].update(self.create_mo_dict_from_mo(mo=ss, para_dict={para: gpl}))

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

        #
        # for cell in self.site.get_cu_cell():
        #     mo = F'GNBCUCPFunction=1,NRCellCU={cell}'
        #     tmp_list = []
        #     for s in sorted([_ for _ in self.site.fdns if re.match(F".*{mo},NRFreqRelation=([^,]*)$", _)]):
        #         tmp_list.append({
        #             'attributes': {'xc:operation': 'update'}, 'nRFreqRelationId': s.split('=')[-1],
        #             'ueMCNrFreqRelProfileRef': 'GNBCUCPFunction=1,UeMC=1,UeMCNrFreqRelProfile=Midband',
        #             'mcpcPCellNrFreqRelProfileRef': 'GNBCUCPFunction=1,Mcpc=1,McpcPCellNrFreqRelProfile=Default',
        #         })
        #     if len(tmp_list) > 0:
        #         self.mo_dict[F'{mo},NRFreqRelation=all_mos-ueMCNrFreqRelProfileRef'] = {'managedElementId': self.node, 'GNBCUCPFunction': {
        #             'gNBCUCPFunctionId': '1', 'NRCellCU': {'nRCellCUId': cell, 'NRFreqRelation': copy.deepcopy(tmp_list)}}}
        #
        #
        #
        # self.mo_dict['lte'] = {
        #     'managedElementId': self.node,
        #     'SystemFunctions': {'systemFunctionsId': '1', 'Lm': {'lmId': '1', 'FeatureState': []}},
        #     'ENodeBFunction': {
        #         'attributes': {'xc:operation': 'update'}, 'eNodeBFunctionId': '1',
        #         'UePolicyOptimization': {'attributes': {'xc:operation': 'update'}, 'uePolicyOptimizationId': '1', 'zzzTemporary1': '3'},
        #         'AnrFunction': {
        #             'anrFunctionId': '1', 'attributes': {'xc:operation': 'update'},
        #             'AnrFunctionNR': {
        #                 'attributes': {'xc:operation': 'update'}, 'anrFunctionNRId': '1',
        #                 'anrStateNR': 'ACTIVATED', 'gNodebIdLength': '26'}},
        #         'EUtranCellFDD': [], 'EUtranCellTDD': [],
        #     },
        # }
        # # FeatureState
        # for r in ['CXC4012578', 'CXC4012385', 'CXC4012371', 'CXC4010620', 'CXC4012324', 'CXC4012218']:
        #     self.mo_dict['lte']['SystemFunctions']['Lm']['FeatureState'].append({
        #         'attributes': {'xc:operation': 'update'}, 'featureStateId': r, 'featureState': 'ACTIVATED'})
        # for r in ['CXC4012580']:
        #     self.mo_dict['lte']['SystemFunctions']['Lm']['FeatureState'].append({
        #         'attributes': {'xc:operation': 'update'}, 'featureStateId': r, 'featureState': 'DEACTIVATED'})
        # # EUtranCellFDD & EUtranCellTDD
        # cell_dict = {
        #     'sib1AltSchInfo': 'false', 'mappingInfo': {'mappingInfoSIB24': '1 (MAPPED_SI_1)'},
        #     'changeNotification': {
        #         'changeNotificationSIB1': 'true', 'changeNotificationSIB13': 'true', 'changeNotificationSIB15': 'true',
        #         'changeNotificationSIB16': 'true', 'changeNotificationSIB2': 'true', 'changeNotificationSIB24': 'true',
        #         'changeNotificationSIB3': 'true', 'changeNotificationSIB4': 'true', 'changeNotificationSIB5': 'true',
        #         'changeNotificationSIB6': 'true', 'changeNotificationSIB7': 'true', 'changeNotificationSIB8': 'true'
        #     },
        #     'UeMeasControl': {
        #         'attributes': {'xc:operation': 'update'}, 'ueMeasControlId': '1',
        #         'waitForStartNRMeas': '6000', 'waitForResumeNRMeas': '6000', 'nrB1MobilityTimerLessTtt': '600', 'sMeasure': '0',
        #         'nrB1MeasEnabled': 'true', 'nrB1MeasAtEndcEnabled': 'true',
        #         'ReportConfigB1NR': {
        #             'attributes': {'xc:operation': 'update'},
        #             'reportConfigB1NRId': '1',
        #             'triggerQuantityB1NR': 'SS_RSRP',
        #             'b1ThresholdRsrp': '-107',
        #             'hysteresisB1': '2',
        #             'timeToTriggerB1': '640'
        #         }
        #     },
        #     'GUtranFreqRelation': [],
        # }
        # rel_dict = {
        #     'anrMeasOn': 'true',
        #     'connectedModeMobilityPrio': '7',
        #     'cellReselectionPriority': '7',
        #     'qRxLevMin': '-110',
        #     'threshXHigh': '4',
        #     'pMaxNR': '33',
        # }
        # for s in sorted([_ for _ in self.site.fdns if re.match(F".*ENodeBFunction=1,EUtranCell.DD=([^,]*)$", _)]):
        #     moc = self.get_end_moc(mo=s)
        #     moid = self.get_moc_id(moc=moc)
        #     mo_dict = {'attributes': {'xc:operation': 'update'}, moid: s.split('=')[-1]}
        #     for k, v in cell_dict.items():
        #         tmp_dict = copy.deepcopy(mo_dict)
        #         tmp_dict[k] = v
        #         self.mo_dict['lte']['ENodeBFunction'][moc].append(copy.deepcopy(tmp_dict))
        #     mo_dict = {moid: s.split('=')[-1], 'GUtranFreqRelation': []}
        #     # tmp_dict = copy.deepcopy(cell_dict)
        #     # tmp_dict.update({moid: s.split('=')[-1]})
        #     moc_child = 'GUtranFreqRelation'
        #     for r in sorted([_ for _ in self.site.fdns if re.match(F".*{s},{moc_child}=([^,]*)$", _)]):
        #         moid_child = self.get_moc_id(moc=moc_child)
        #         mo_dict_child = {'attributes': {'xc:operation': 'update'}, moid_child: r.split('=')[-1]}
        #         for k, v in rel_dict.items():
        #             tmp_dict = copy.deepcopy(mo_dict_child)
        #             tmp_dict[k] = v
        #             mo_dict[moc_child].append(copy.deepcopy(tmp_dict))
        #     self.mo_dict['lte']['ENodeBFunction'][moc].append(copy.deepcopy(mo_dict))
        #
        # # for cell in self.site.get_fdd_cell():
        # #     mo = F'ENodeBFunction=1,EUtranCellFDD={cell}'
        # #     tmp_dict = {
        # #         'attributes': {'xc:operation': 'update'}, 'eUtranCellFDDId': cell,
        # #         'sib1AltSchInfo': 'false', 'mappingInfo': {'mappingInfoSIB24': '1 (MAPPED_SI_1)'},
        # #         'changeNotification': {
        # #             'changeNotificationSIB1': 'true', 'changeNotificationSIB13': 'true', 'changeNotificationSIB15': 'true',
        # #             'changeNotificationSIB16': 'true', 'changeNotificationSIB2': 'true', 'changeNotificationSIB24': 'true',
        # #             'changeNotificationSIB3': 'true', 'changeNotificationSIB4': 'true', 'changeNotificationSIB5': 'true',
        # #             'changeNotificationSIB6': 'true', 'changeNotificationSIB7': 'true', 'changeNotificationSIB8': 'true'
        # #         },
        # #         'UeMeasControl': {
        # #             'ueMeasControlId': '1', 'attributes': {'xc:operation': 'update'},
        # #             'waitForStartNRMeas': '6000', 'waitForResumeNRMeas': '6000', 'nrB1MobilityTimerLessTtt': '600', 'sMeasure': '0',
        # #             'nrB1MeasEnabled': 'true', 'nrB1MeasAtEndcEnabled': 'true',
        # #             'ReportConfigB1NR': {'attributes': {'xc:operation': 'update'}, 'reportConfigB1NRId': '1', 'triggerQuantityB1NR': 'SS_RSRP',
        # #                                  'b1ThresholdRsrp': '-107', 'hysteresisB1': '2', 'timeToTriggerB1': '640'}
        # #         },
        # #         'GUtranFreqRelation': [],
        # #     }
        # #     tmp_list = []
        # #     for s in sorted([_ for _ in self.site.fdns if re.match(F".*{mo},GUtranFreqRelation=([^,]*)$", _)]):
        # #         tmp_list.append({
        # #             'attributes': {'xc:operation': 'update'},
        # #             'gUtranFreqRelationId': s.split('=')[-1],
        # #             'anrMeasOn': 'true',
        # #             'connectedModeMobilityPrio': '7',
        # #             'cellReselectionPriority': '7',
        # #             'qRxLevMin': '-110',
        # #             'threshXHigh': '4',
        # #             'pMaxNR': '33',
        # #         })
        # #         tmp_list.append({'attributes': {'xc:operation': 'update'}, 'gUtranFreqRelationId': s.split('=')[-1], 'connectedModeMobilityPrio': '7'})
        # #         tmp_list.append({'attributes': {'xc:operation': 'update'}, 'gUtranFreqRelationId': s.split('=')[-1], 'cellReselectionPriority': '7'})
        # #         tmp_list.append({'attributes': {'xc:operation': 'update'}, 'gUtranFreqRelationId': s.split('=')[-1], 'qRxLevMin': '-110'})
        # #         tmp_list.append({'attributes': {'xc:operation': 'update'}, 'gUtranFreqRelationId': s.split('=')[-1], 'threshXHigh': '4'})
        # #         tmp_list.append({'attributes': {'xc:operation': 'update'}, 'gUtranFreqRelationId': s.split('=')[-1], 'pMaxNR': '33'})
        # #     if len(tmp_list) > 0: tmp_dict['GUtranFreqRelation'].extend(tmp_list)
        # #     self.mo_dict['lte']['ENodeBFunction']['EUtranCellFDD'].append(copy.deepcopy(tmp_dict))
        # #
        # # # EUtranCellTDD
        # # for cell in self.site.get_tdd_cell():
        # #     mo = F'ENodeBFunction=1,EUtranCellTDD={cell}'
        # #     tmp_dict = {
        # #         'attributes': {'xc:operation': 'update'}, 'eUtranCellTDDId': cell,
        # #         'sib1AltSchInfo': 'false',
        # #         'mappingInfo': {'mappingInfoSIB24': '1 (MAPPED_SI_1)'},
        # #         'changeNotification': {
        # #             'changeNotificationSIB1': 'true', 'changeNotificationSIB13': 'true', 'changeNotificationSIB15': 'true',
        # #             'changeNotificationSIB16': 'true', 'changeNotificationSIB2': 'true', 'changeNotificationSIB24': 'true',
        # #             'changeNotificationSIB3': 'true', 'changeNotificationSIB4': 'true', 'changeNotificationSIB5': 'true',
        # #             'changeNotificationSIB6': 'true', 'changeNotificationSIB7': 'true', 'changeNotificationSIB8': 'true'
        # #         },
        # #         'UeMeasControl': {
        # #             'ueMeasControlId': '1', 'attributes': {'xc:operation': 'update'},
        # #             'waitForStartNRMeas': '6000', 'waitForResumeNRMeas': '6000', 'nrB1MobilityTimerLessTtt': '600', 'sMeasure': '0',
        # #             'nrB1MeasEnabled': 'true', 'nrB1MeasAtEndcEnabled': 'true',
        # #             'ReportConfigB1NR': {'attributes': {'xc:operation': 'update'}, 'reportConfigB1NRId': '1', 'triggerQuantityB1NR': 'SS_RSRP',
        # #                                  'b1ThresholdRsrp': '-107', 'hysteresisB1': '2', 'timeToTriggerB1': '640'}
        # #         },
        # #         'GUtranFreqRelation': [],
        # #     }
        # #     tmp_list = []
        # #     for s in sorted([_ for _ in self.site.fdns if re.match(F".*{mo},GUtranFreqRelation=([^,]*)$", _)]):
        # #         tmp_list.append({
        # #             'attributes': {'xc:operation': 'update'},
        # #             'gUtranFreqRelationId': s.split('=')[-1],
        # #             'anrMeasOn': 'true',
        # #             'connectedModeMobilityPrio': '7',
        # #             'cellReselectionPriority': '7',
        # #             'qRxLevMin': '-110',
        # #             'threshXHigh': '4',
        # #             'pMaxNR': '33',
        # #         })
        # #     if len(tmp_list) > 0: tmp_dict['GUtranFreqRelation'].extend(tmp_list)
        # #     self.mo_dict['lte']['ENodeBFunction']['EUtranCellTDD'].append(copy.deepcopy(tmp_dict))
