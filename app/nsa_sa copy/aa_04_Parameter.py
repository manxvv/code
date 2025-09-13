import copy
import numpy as np
from Script import Script


class aa_04_Parameter(Script):
    def create_rpc_msg(self):
        # if self.node in self.usid.nr_node: self.nr_parameter_update()
        if self.node in self.usid.lte_node: self.lte_parameter_update()

    def nr_parameter_update(self):
        for r in self.usid.db['MOC'].itertuples():
            if '=' not in r.__getattribute__('mo'): continue
            if (self.site.get_fdn_parameter(fdn=F'{self.site.me},{r.__getattribute__("mo")}', para=r.__getattribute__('parameter')) !=
                    r.__getattribute__('value')):
                tmp_dict = {r.__getattribute__('parameter'): r.__getattribute__('value')}
                # tmp_dict[r.__getattribute__('parameter')] = r.__getattribute__('value')
                mo_para = F'{r.__getattribute__("mo")}--{r.__getattribute__("value")}'
                self.mo_dict[mo_para] = {'managedElementId': self.node}
                self.mo_dict[mo_para].update(self.create_mo_dict_from_mo(mo=r.__getattribute__('mo'), para_dict=tmp_dict))
            else: print(r.__getattribute__('value'))

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
                tmp_dict = {_.split('_')[-1]: r.__getattribute__(_) for _ in tmp_list}
                tmp_dict |= {'attributes': {'xc:operation': 'update'}, 'ueMCEUtranFreqRelProfileUeCfgId': 'Base'}
                self.mo_dict['UeMCEUtranFreqRelProfile']['GNBCUCPFunction']['UeMC']['UeMCEUtranFreqRelProfile'].append({
                    'ueMCEUtranFreqRelProfileId': mo_id, 'UeMCEUtranFreqRelProfileUeCfg': copy.deepcopy(tmp_dict)})

        # if len(tmp_dict) > 0:
        #     self.mo_dict[mo] = {'managedElementId': self.node}
        #     self.mo_dict[mo].update(self.create_mo_dict_from_mo(mo=mo, para_dict=tmp_dict))
        # NRCellCU
        # tmp_dict = {}
        # for r in self.usid.db['MOC'].loc[self.usid.db['MOC'].mo == 'NRCellCU'].itertuples():
        #     tmp_dict[r.__getattribute__('parameter')] = r.__getattribute__('value')
        # for cell in self.site.cu_cell:
        #     tmp_mo_dict = {}
        #     mo = F'{self.site.me},GNBCUCPFunction=1,NRCellCU={cell}'
        #     for r in tmp_dict.keys():
        #         if (self.site.get_fdn_parameter(fdn=F'{mo}', para=r) != tmp_dict.get(r)):
        #             tmp_mo_dict[r] = tmp_dict.get(r)
        #     if len(tmp_mo_dict) > 0:
        #         tmp_mo_dict |= {'nRCellCUId': cell, 'attributes': {'xc:operation': 'update'}}
        #         self.mo_dict[mo] = {'managedElementId': self.node, 'GNBCUCPFunction': {
        #             'gNBCUCPFunctionId': '1', 'NRCellCU': copy.deepcopy(tmp_mo_dict)}}


        # NRCellCU
        tmp_dict = {}
        for r in self.usid.db['MOC'].loc[self.usid.db['MOC'].mo == 'NRCellCU'].itertuples():
            tmp_dict[r.__getattribute__('parameter')] = r.__getattribute__('value')
        for cell in self.site.cu_cell:
            mo = F'{self.site.me},GNBCUCPFunction=1,NRCellCU={cell}'
            for r in tmp_dict.keys():
                self.mo_dict[F'{mo}{r}'] = {'managedElementId': self.node, 'GNBCUCPFunction': {
                    'gNBCUCPFunctionId': '1', 'NRCellCU': {
                        'nRCellCUId': cell, 'attributes': {'xc:operation': 'update'}, r: tmp_dict[r]}
                }}
        # NRCellDU
        tmp_dict = {}
        for r in self.usid.db['MOC'].loc[self.usid.db['MOC'].mo == 'NRCellDU'].itertuples():
            tmp_dict[r.__getattribute__('parameter')] = r.__getattribute__('value')
        for cell in self.site.cu_cell:
            mo = F'{self.site.me},GNBDUFunction=1,NRCellDU={cell}'
            for r in tmp_dict.keys():
                self.mo_dict[F'{mo}{r}'] = {'managedElementId': self.node, 'GNBDUFunction': {
                    'gNBDUFunctionId': '1', 'NRCellDU': {
                        'nRCellDUId': cell, 'attributes': {'xc:operation': 'update'}, r: tmp_dict[r]}
                }}

    def lte_parameter_update(self):
        if self.node not in self.usid.lte_node: return
        self.mo_dict['lte'] = {
            'managedElementId': self.node,
            'ENodeBFunction': {
                'eNodeBFunctionId': '1', 'EUtranCellFDD': [], 'EUtranCellTDD': [],
                'UePolicyOptimization': {'attributes': {'xc:operation': 'update'}, 'uePolicyOptimizationId': '1', 'zzzTemporary1': '1'},
                'AnrFunction': {'anrFunctionId': '1', 'AnrFunctionNR': {
                    'attributes': {'xc:operation': 'update'}, 'anrFunctionNRId': '1', 'anrStateNR': 'ACTIVATED', 'gNodebIdLength': '26'}},
            },
            'SystemFunctions': {'systemFunctionsId': '1', 'Lm': {'lmId': '1', 'FeatureState': []}},
        }
        # FeatureState
        for r in ['CXC4012578', 'CXC4012385', 'CXC4012371', 'CXC4010620']:
            self.mo_dict['lte']['SystemFunctions']['Lm']['FeatureState'].append({'attributes': {'xc:operation': 'update'},
                                                                                 'featureStateId': r, 'featureState': 'ACTIVATED'})
        for r in ['CXC4012324', 'CXC4012580']:
            self.mo_dict['lte']['SystemFunctions']['Lm']['FeatureState'].append({'attributes': {'xc:operation': 'update'},
                                                                                 'featureStateId': r, 'featureState': 'DEACTIVATED'})
        for cell in self.site.fdd_cell:
            self.mo_dict['lte']['ENodeBFunction']['EUtranCellFDD'].append({
                'attributes': {'xc:operation': 'update'}, 'eUtranCellFDDId': cell,
                'sib1AltSchInfo': 'false',
                'mappingInfo': {'mappingInfoSIB24': '1 (MAPPED_SI_1)'},
                'changeNotification': {
                    'changeNotificationSIB1': 'true', 'changeNotificationSIB13': 'true', 'changeNotificationSIB15': 'true',
                    'changeNotificationSIB16': 'true', 'changeNotificationSIB2': 'true', 'changeNotificationSIB24': 'true',
                    'changeNotificationSIB3': 'true', 'changeNotificationSIB4': 'true', 'changeNotificationSIB5': 'true',
                    'changeNotificationSIB6': 'true', 'changeNotificationSIB7': 'true', 'changeNotificationSIB8': 'true'
                },
                'UeMeasControl': {
                    'ueMeasControlId': '1',
                    'waitForStartNRMeas': '6000', 'waitForResumeNRMeas': '6000', 'nrB1MobilityTimerLessTtt': '600', 'sMeasure': '0',
                    'nrB1MeasEnabled': 'false', 'nrB1MeasAtEndcEnabled': 'true',
                    # '': '', '': '', '': '', '': '',
                    'ReportConfigB1NR': {'attributes': {'xc:operation': 'update'}, 'reportConfigB1NRId': '1', 'triggerQuantityB1NR': 'SS_RSRP',
                                         'b1ThresholdRsrp': '-107', 'hysteresisB1': '2', 'timeToTriggerB1': '640'}
                },


            })


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