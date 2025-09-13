from Script import Script
import copy


class aa_01_5qiTable_BWP(Script):
    def create_rpc_msg(self):
        if self.node not in self.usid.nr_node: return
        # 5qi Tables ---
        self.mo_dict['5qi'] = {
            'managedElementId': self.node,
            'GNBDUFunction': {'gNBDUFunctionId': '1', 'DU5qiTable': {
            'attributes': {'xc:operation': 'create'}, 'dU5qiTableId': '1', 'default5qiTable': 'true', 'DU5qi': []}},
            'GNBCUCPFunction': {'gNBCUCPFunctionId': '1', 'CUCP5qiTable': {
            'attributes': {'xc:operation': 'create'}, 'cUCP5qiTableId': '1', 'default5qiTable': 'true', 'CUCP5qi': []}},
            'GNBCUUPFunction': {'gNBCUUPFunctionId': '1', 'CUUP5qiTable': {
            'attributes': {'xc:operation': 'create'}, 'cUUP5qiTableId': '1', 'default5qiTable': 'true', 'CUUP5qi': []}},
        }
        for mo_type in ['DU', 'CUCP', 'CUUP']:
            tmp_list = self.usid.db[F'{mo_type}5qi'].columns.tolist()
            for r in self.usid.db[F'{mo_type}5qi'].itertuples():
                tmp_dict = {_: r.__getattribute__(_) for _ in tmp_list}
                tmp_dict |= {'attributes': {'xc:operation': 'create'}}
                self.mo_dict['5qi'][F'GNB{mo_type}Function'][F'{mo_type}5qiTable'][F'{mo_type}5qi'].append(copy.deepcopy(tmp_dict))

        # GNBDUFunction -- BWP & BWPSet & sNSSAIList
        self.mo_dict['GNBDUFunction_BWP'] = {
            'managedElementId': self.node,
            'GNBDUFunction': {
                'gNBDUFunctionId': '1',
                'BWP': [
                    {'attributes': {'xc:operation': 'create'}, 'bWPId': 'Init_DL_100', 'bwpContext': '0 (DOWNLINK)',
                     'numberOfRBs': '273', 'isInitialBwp': 'true', },
                    {'attributes': {'xc:operation': 'create'}, 'bWPId': 'Init_UL_100', 'bwpContext': '1 (UPLINK)',
                     'numberOfRBs': '273', 'isInitialBwp': 'true', },
                    {'attributes': {'xc:operation': 'create'}, 'bWPId': 'DenseSS_DL_100', 'bwpContext': '0 (DOWNLINK)',
                     'numberOfRBs': '273', 'isInitialBwp': 'false', },
                    {'attributes': {'xc:operation': 'create'}, 'bWPId': 'DenseSS_UL_100', 'bwpContext': '1 (UPLINK)',
                     'numberOfRBs': '273', 'isInitialBwp': 'false', },
                    {'attributes': {'xc:operation': 'create'}, 'bWPId': 'SparseSS_DL_100', 'bwpContext': '0 (DOWNLINK)',
                     'numberOfRBs': '273', 'isInitialBwp': 'false', },
                    {'attributes': {'xc:operation': 'create'}, 'bWPId': 'SparseSS_UL_100', 'bwpContext': '1 (UPLINK)',
                     'numberOfRBs': '273', 'isInitialBwp': 'false', },
                ],
                'BWPSet': {
                    'attributes': {'xc:operation': 'create'}, 'bWPSetId': '100',
                    'allBWPRegularRef': ['GNBDUFunction=1,BWP=DenseSS_DL_100', 'GNBDUFunction=1,BWP=DenseSS_UL_100',
                                         'GNBDUFunction=1,BWP=SparseSS_DL_100', 'GNBDUFunction=1,BWP=SparseSS_UL_100'],
                    'startBWPDlRef': 'GNBDUFunction=1,BWP=DenseSS_DL_100', 'startBWPUlRef': 'GNBDUFunction=1,BWP=DenseSS_UL_100',
                    'DynPowerOpt': [
                        {'attributes': {'xc:operation': 'create'}, 'dynPowerOptId': '1', 'downDlThreshold': '200', 'downUlThreshold': '200',
                         'upDlThreshold': '300', 'upUlThreshold': '300'},
                        {'attributes': {'xc:operation': 'create'}, 'dynPowerOptId': 'VoNR', 'downDlThreshold': '10', 'downUlThreshold': '10',
                         'upDlThreshold': '30', 'upUlThreshold': '30'}
                    ],
                    'BWPSetUeCfg': [
                        {'attributes': {'xc:operation': 'create'}, 'bWPSetUeCfgId': '1',
                         'BWPSetCfg': [
                             {'attributes': {'xc:operation': 'create'}, 'bWPSetCfgId': '0', 'bWPDlRef': 'GNBDUFunction=1,BWP=DenseSS_DL_100',
                              'bWPUlRef': 'GNBDUFunction=1,BWP=DenseSS_UL_100'},
                             {'attributes': {'xc:operation': 'create'}, 'bWPSetCfgId': '1', 'bWPDlRef': 'GNBDUFunction=1,BWP=SparseSS_DL_100',
                              'bWPUlRef': 'GNBDUFunction=1,BWP=SparseSS_UL_100', 'dynPowerOptRef': 'GNBDUFunction=1,BWPSet=100,DynPowerOpt=1'}]
                         },
                        {'attributes': {'xc:operation': 'create'}, 'bWPSetUeCfgId': 'VoNR', 'ueConfGroupList': ['1'],
                         'bwpSwitchingFilterRelaxation': 'false',
                         'BWPSetCfg': [
                             {'attributes': {'xc:operation': 'create'}, 'bWPSetCfgId': '0', 'bWPDlRef': 'GNBDUFunction=1,BWP=DenseSS_DL_100',
                              'bWPUlRef': 'GNBDUFunction=1,BWP=DenseSS_UL_100'},
                             {'attributes': {'xc:operation': 'create'}, 'bWPSetCfgId': '1', 'bWPDlRef': 'GNBDUFunction=1,BWP=SparseSS_DL_100',
                              'bWPUlRef': 'GNBDUFunction=1,BWP=SparseSS_UL_100', 'dynPowerOptRef': 'GNBDUFunction=1,BWPSet=100,DynPowerOpt=VoNR'}]
                         },
                    ],
                },
                'NRCellDU': [],
            },
        }

        for cell in self.site.du_cell:
            self.mo_dict['GNBDUFunction_BWP']['GNBDUFunction']['NRCellDU'].append({
                'attributes': {'xc:operation': 'update'}, 'nRCellDUId': cell,
                'sNSSAIList': {'sd': '1', 'sst': '1'},
                'bWPRef': ['GNBDUFunction=1,BWP=Init_DL_100', 'GNBDUFunction=1,BWP=Init_UL_100'],
                'bWPSetRef': 'GNBDUFunction=1,BWPSet=100'
            })
