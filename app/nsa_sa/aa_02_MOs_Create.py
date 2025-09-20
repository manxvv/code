import copy
import re
from Script import Script


class aa_02_MOs_Create(Script):
    def create_rpc_msg(self):
        if self.node not in self.usid.nr_node: return

        # EUtranFreqRelation
        trStSa = list(set(['Default'] + [
            _.split('=')[-1] for _ in self.usid.db['EUtranFreqRelation']['trStSaEUtranFreqRelProfileRef'].tolist() if '=' in _]))
        ueMC = list(set(['Default'] + [
            _.split('=')[-1] for _ in self.usid.db['EUtranFreqRelation']['ueMCEUtranFreqRelProfileRef'].tolist() if '=' in _]))
        mcpcPCell = list(set(['Default', 'HO', 'NOHO'] + [
            _.split('=')[-1] for _ in self.usid.db['EUtranFreqRelation']['mcpcPCellEUtranFreqRelProfileRef'].tolist() if '=' in _]))

        self.mo_dict['mos_mos'] = {
            'managedElementId': self.node,
            'Transport': {'transportId': '1', 'SctpEndpoint': {}},
            'GNBCUCPFunction': {
                'gNBCUCPFunctionId': '1',
                'EndpointResource': {'endpointResourceId': '1', 'LocalSctpEndpoint': {}},
                'TermPointToAmf': [],

                'AnrFunction': {
                    'anrFunctionId': '1', 'AnrFunctionEUtran': {'attributes': {'xc:operation': 'create'}, 'anrFunctionEUtranId': '1'}
                },
                'TrafficSteering': {
                    'trafficSteeringId': '1',
                    'TrStSaEUtranFreqRelProfile': [{'attributes': {'xc:operation': 'create'}, 'trStSaEUtranFreqRelProfileId': _} for _ in trStSa]
                },
                'UeMC': {
                    'ueMCId': '1',
                    'UeMCCellProfile': {'attributes': {'xc:operation': 'create'}, 'ueMCCellProfileId': 'Default'},
                    'UeMCNrFreqRelProfile': {'attributes': {'xc:operation': 'create'}, 'ueMCNrFreqRelProfileId': 'Midband'},
                    'UeMCEUtranFreqRelProfile': [{'attributes': {'xc:operation': 'create'}, 'ueMCEUtranFreqRelProfileId': _} for _ in ueMC],
                },
                'Mcpc': {
                    'mcpcId': '1',
                    'McpcPCellProfile': {'attributes': {'xc:operation': 'create'}, 'mcpcPCellProfileId': 'MidBand',
                                         'McpcPCellProfileUeCfg': {'attributes': {'xc:operation': 'create'}, 'mcpcPCellProfileUeCfgId': 'VoNR',
                                                                   'ueConfGroupList': ['5'], 'ueGroupList': ['1'], 'rsrpCriticalEnabled': 'false'}},
                    'McpcPCellEUtranFreqRelProfile': [{'attributes': {'xc:operation': 'create'},
                                                       'mcpcPCellEUtranFreqRelProfileId': _} for _ in mcpcPCell],
                },
                'Mcfb': {
                    'attributes': {'xc:operation': 'create'}, 'mcfbId': '1',
                    'McfbCellProfile': {'attributes': {'xc:operation': 'create'}, 'mcfbCellProfileId': '1'}
                },
                'UeGroupSelection': {
                    'attributes': {'xc:operation': 'create'}, 'ueGroupSelectionId': '1', 'UeGroupSelectionProfile': [],
                    'UeServiceGroupDefinition': [], 'PrefUeGroupSelectionProfile': [], 'UeMobilityGroupDefinition': [],
                },
                'UeCC': {
                    'ueCCId': '1',
                    'RrcInactiveProfile': {'rrcInactiveProfileId': 'Default', 'RrcInactiveProfileUeCfg': [
                        {'attributes': {'xc:operation': 'create'}, 'rrcInactiveProfileUeCfgId': '5QI6', 'ueConfGroupList': ['66'],
                         'ueGroupList': ['66'], 'rrcInactiveStateSupport': 'true', 'periodicRnaUpdateTimer': '30', 'periodicRnaUpdateCount': '1'},
                        {'attributes': {'xc:operation': 'create'}, 'rrcInactiveProfileUeCfgId': '5QI7', 'ueConfGroupList': ['77'],
                         'ueGroupList': ['77'], 'rrcInactiveStateSupport': 'true', 'periodicRnaUpdateTimer': '30', 'periodicRnaUpdateCount': '1'},
                        {'attributes': {'xc:operation': 'create'}, 'rrcInactiveProfileUeCfgId': '5QI9', 'ueConfGroupList': ['99'],
                         'ueGroupList': ['99'], 'rrcInactiveStateSupport': 'true', 'periodicRnaUpdateTimer': '30', 'periodicRnaUpdateCount': '1'},
                    ]},
                    'InactivityProfile': {'inactivityProfileId': 'Default', 'InactivityProfileUeCfg': {
                        'attributes': {'xc:operation': 'create'}, 'inactivityProfileUeCfgId': 'VoNR',
                        'tInactivityTimer': '15', 'tInactivityTimerEndcSn': '10', 'tInactivityTimerNrdcSn': '10', 'ueGroupList': ['1']
                    }},
                },
                'EmCall': {'attributes': {'xc:operation': 'create'}, 'emCallId': '1', 'arpPrioEm5qi1List': ['1'], 'arpPrioEm5qi5List': ['1']},
                'EUtraNetwork': {'eUtraNetworkId': '1', 'EUtranFrequency': []},
                'NRCellCU': []
            },


            'GNBCUUPFunction': {
                'gNBCUUPFunctionId': '1',
                'GtpuSupervision': {
                    'attributes': {'xc:operation': 'create'}, 'gtpuSupervisionId': '1', 'gtpuErrorIndDscp': '40',
                    'GtpuSupervisionProfile': [
                        {'attributes': {'xc:operation': 'create'}, 'gtpuEchoDscp': '32', 'gtpuEchoEnabled': 'true',
                         'gtpuSupervisionProfileId': 'XN', 'interfaceList': '6 (XN)'},
                        {'attributes': {'xc:operation': 'create'}, 'gtpuEchoDscp': '32', 'gtpuEchoEnabled': 'true',
                         'gtpuSupervisionProfileId': 'NG', 'interfaceList': '4 (NG)'}]
                },
                'UeCC': {
                    'ueCCId': '1',
                    'DcDlCfg': {'attributes': {'xc:operation': 'create'}, 'dcDlCfgId': 'Default', 'dcDlAggAllowed': 'true'},
                    'UserPlaneProfile': {'attributes': {'xc:operation': 'create'}, 'userPlaneProfileId': 'Default'},
                }
            },
            'GNBDUFunction': {
                'gNBDUFunctionId': '1',
                'QosPriorityMapping': {
                    'attributes': {'xc:operation': 'create'}, 'qosPriorityMappingId': '1',
                    'PriorityDomainMapping': {'attributes': {'xc:operation': 'create'}, 'priorityDomainMappingId': '1', 'priorityDomain': '16'}},
                'UeCC': {
                    'ueCCId': '1',
                    'SrHandling': {'attributes': {'xc:operation': 'create'}, 'srHandlingId': '5QI_5'},
                    'RadioLinkControl': {'attributes': {'xc:operation': 'create'}, 'radioLinkControlId': '1', 'DrbRlc': {
                        'attributes': {'xc:operation': 'create'}, 'drbRlcId': 'Default', 'DrbRlcUeCfg': {
                            'attributes': {'xc:operation': 'create'}, 'drbRlcUeCfgId': 'VoNR', 'tReassemblyDl': '65', 'tReassemblyUl': '65',
                            'rlcSNLength': '12', 'ueConfGroupList': ['1'], 'ueGroupList': ['1']}}
                                         },
                    'DrxProfile': {'attributes': {'xc:operation': 'create'}, 'drxProfileId': 'Default', 'DrxProfileUeCfg': {
                        'attributes': {'xc:operation': 'create'}, 'drxProfileUeCfgId': 'VoNR', 'drxEnabled': 'true',
                        'drxInactivityTimer': 'INACTIVITYTIMER_5MS', 'drxLongCycle': 'LONGCYCLE_40MS',
                        'drxOnDurationTimer': 'ONDURATIONTIMER_5MS', 'drxRetransmissionTimerDl': '6',
                        'drxRetransmissionTimerUl': '6', 'ueGroupList': ['1']}
                                   },
                    'UeBb': {'ueBbId': '1', 'UeBbProfile': {'ueBbProfileId': 'Default', 'UeBbProfileUeCfg': {
                        'attributes': {'xc:operation': 'create'}, 'ueBbProfileUeCfgId': 'MBB', 'ueConfGroupList': ['1'], 'ueGroupList': ['66', '77'],
                        'bsrUeCfgRef': 'GNBDUFunction=1,UeCC=1,Bsr=1,BsrUeCfg=Base',
                        'linkAdaptationUeCfgRef': 'GNBDUFunction=1,UeCC=1,LinkAdaptation=1,LinkAdaptationUeCfg=Base',
                        'harqUeCfgRef': 'GNBDUFunction=1,UeCC=1,Harq=1,HarqUeCfg=Base',

                    }}},
                },
            },
        }

        # Transport, EndpointResource, LocalSctpEndpoint, SctpEndpoint
        tn_dict, a, b, c = self.site.get_sctp_local_sctp_dicts()
        if len(tn_dict) > 0:
            self.mo_dict['mos_mos']['Transport'] |= tn_dict['Transport']
            self.mo_dict['mos_mos']['GNBCUCPFunction']['EndpointResource'] |= tn_dict['GNBCUCPFunction']['EndpointResource']
        else: self.custom_log.log.exception(F'TN MOs need to be validated :  {self.node} -- {b} -- {c} -- {a} -- ')

        # TermPointToAmf
        tmp_list = ['termPointToAmfId', 'administrativeState', 'defaultAmf', 'pwsRestartHandling',
                    'ipv6Address1', 'ipv6Address2', 'ipv4Address1', 'ipv4Address2']
        for r in self.usid.db['TermPointToAmf'].itertuples():
            tmp_dict = {_: r.__getattribute__(_) for _ in tmp_list}
            if len(self.usid.df_amf.loc[(
                    (self.usid.df_amf.ipv6Address1 == tmp_dict['ipv6Address1']) & (self.usid.df_amf.ipv6Address2 == tmp_dict['ipv6Address2']) &
                    (self.usid.df_amf.ipv4Address1 == tmp_dict['ipv4Address1']) &
                    (self.usid.df_amf.ipv4Address2 == tmp_dict['ipv4Address2']))].index) == 0:
                tmp_dict |= {'attributes': {'xc:operation': 'create'}}
                self.mo_dict['mos_mos']['GNBCUCPFunction']['TermPointToAmf'].append(copy.deepcopy(tmp_dict))
            else:
                self.add_mo_para_to_para_list_and_compare(
                    mo=F'TermPointToAmf={tmp_dict["termPointToAmfId"]} -- IP({tmp_dict["ipv6Address2"]} {tmp_dict["ipv6Address2"]} '
                       F'{tmp_dict["ipv4Address1"]} {tmp_dict["ipv4Address1"]}',
                    para='amf_status', value='AlreadyExist', gpl='AlreadyExist', remark='Validate_AMF')

        # EUtranFrequency, EUtranFreqRelation
        tmp_list = ['eUtranFreqRelationId', 'allowedMeasBandwidth', 'anrMeasOn', 'cellReselectionPriority', 'eUtranFallbackPrioEc',
                    'pMaxEUtra', 'presenceAntennaPort1', 'qRxLevMin', 'tReselectionEUtra', 'threshXHighP', 'threshXLowP',
                    'voicePrio', 'eUtranFrequencyRef', 'mcpcPCellEUtranFreqRelProfileRef', 'trStSaEUtranFreqRelProfileRef',
                    'ueMCEUtranFreqRelProfileRef']
        for r in self.usid.db['EUtranFreqRelation']['eUtranFreqRelationId'].tolist():
            if not self.site.fdn_exists(fdn=F'GNBCUCPFunction=1,EUtraNetwork=1,EUtranFrequency={r}'):
                self.mo_dict['mos_mos']['GNBCUCPFunction']['EUtraNetwork']['EUtranFrequency'].append({
                    'attributes': {'xc:operation': 'create'}, 'arfcnValueEUtranDl': r, 'eUtranFrequencyId': r})

        tmp_mo_list = []
        for r in self.usid.db['EUtranFreqRelation'].itertuples():
            tmp_dict = {_: r.__getattribute__(_) for _ in tmp_list}
            tmp_dict |= {'attributes': {'xc:operation': 'create'}}
            tmp_mo_list.append(copy.deepcopy(tmp_dict))
        for r in self.site.cu_cell:
            self.mo_dict['mos_mos']['GNBCUCPFunction']['NRCellCU'].append({
                'attributes': {'xc:operation': 'update'}, 'nRCellCUId': r, 'EUtranFreqRelation': copy.deepcopy(tmp_mo_list)
            })

        # UeGroupSelection
        ue_dict = {
            'UeGroupSelectionProfile': [
                {'attributes': {'xc:operation': 'create'}, 'ueGroupSelectionProfileId': 'VoNR',
                 'selectionCriteria': '5qi==1', 'ueGroupId': '1', 'ueGroupPriority': '65535'},
                {'attributes': {'xc:operation': 'create'}, 'ueGroupSelectionProfileId': '5QI6',
                 'selectionCriteria': '5qi==6', 'ueGroupId': '66', 'ueGroupPriority': '65533'},
                {'attributes': {'xc:operation': 'create'}, 'ueGroupSelectionProfileId': 'qci6',
                 'selectionCriteria': 'qci==6', 'ueGroupId': '6', 'ueGroupPriority': '65534'},
                {'attributes': {'xc:operation': 'create'}, 'ueGroupSelectionProfileId': '5QI7',
                 'selectionCriteria': '5qi==7', 'ueGroupId': '77', 'ueGroupPriority': '999'},
                {'attributes': {'xc:operation': 'create'}, 'ueGroupSelectionProfileId': 'qci7',
                 'selectionCriteria': 'qci==7', 'ueGroupId': '7', 'ueGroupPriority': '1000'},
                {'attributes': {'xc:operation': 'create'}, 'ueGroupSelectionProfileId': '5QI9',
                 'selectionCriteria': '5qi==9', 'ueGroupId': '99', 'ueGroupPriority': '899'},
                {'attributes': {'xc:operation': 'create'}, 'ueGroupSelectionProfileId': 'qci9',
                 'selectionCriteria': 'qci==9', 'ueGroupId': '9', 'ueGroupPriority': '900'},
            ],
            'UeServiceGroupDefinition': [
                {'attributes': {'xc:operation': 'create'}, 'ueServiceGroupDefinitionId': 'VoNR',
                 'selectionCriteria': '5qi==1', 'ueServiceGroupId': '1', 'ueServiceGroupPriority': '65535'},
                {'attributes': {'xc:operation': 'create'}, 'ueServiceGroupDefinitionId': '5QI6',
                 'selectionCriteria': '5qi==6', 'ueServiceGroupId': '66', 'ueServiceGroupPriority': '65533'},
                {'attributes': {'xc:operation': 'create'}, 'ueServiceGroupDefinitionId': 'qci6',
                 'selectionCriteria': 'qci==6', 'ueServiceGroupId': '6', 'ueServiceGroupPriority': '65534'},
                {'attributes': {'xc:operation': 'create'}, 'ueServiceGroupDefinitionId': '5QI7',
                 'selectionCriteria': '5qi==7', 'ueServiceGroupId': '77', 'ueServiceGroupPriority': '999'},
                {'attributes': {'xc:operation': 'create'}, 'ueServiceGroupDefinitionId': 'qci7',
                 'selectionCriteria': 'qci==7', 'ueServiceGroupId': '7', 'ueServiceGroupPriority': '1000'},
                {'attributes': {'xc:operation': 'create'}, 'ueServiceGroupDefinitionId': '5QI9',
                 'selectionCriteria': '5qi==9', 'ueServiceGroupId': '99', 'ueServiceGroupPriority': '899'},
                {'attributes': {'xc:operation': 'create'}, 'ueServiceGroupDefinitionId': 'qci9',
                 'selectionCriteria': 'qci==9', 'ueServiceGroupId': '9', 'ueServiceGroupPriority': '900'},
            ],
            'PrefUeGroupSelectionProfile': [
                {'attributes': {'xc:operation': 'create'}, 'prefUeGroupSelectionProfileId': 'VoNR',
                 'selectionCriteria': '5qi==1', 'prefUeGroupId': '1', 'prefUeGroupPriority': '65535'},
                {'attributes': {'xc:operation': 'create'}, 'prefUeGroupSelectionProfileId': '5QI6',
                 'selectionCriteria': '5qi==6', 'prefUeGroupId': '66', 'prefUeGroupPriority': '65533'},
                {'attributes': {'xc:operation': 'create'}, 'prefUeGroupSelectionProfileId': 'qci6',
                 'selectionCriteria': 'qci==6', 'prefUeGroupId': '6', 'prefUeGroupPriority': '65534'},
                {'attributes': {'xc:operation': 'create'}, 'prefUeGroupSelectionProfileId': '5QI7',
                 'selectionCriteria': '5qi==7', 'prefUeGroupId': '77', 'prefUeGroupPriority': '999'},
                {'attributes': {'xc:operation': 'create'}, 'prefUeGroupSelectionProfileId': 'qci7',
                 'selectionCriteria': 'qci==7', 'prefUeGroupId': '7', 'prefUeGroupPriority': '1000'},
                {'attributes': {'xc:operation': 'create'}, 'prefUeGroupSelectionProfileId': '5QI9',
                 'selectionCriteria': '5qi==9', 'prefUeGroupId': '99', 'prefUeGroupPriority': '899'},
                {'attributes': {'xc:operation': 'create'}, 'prefUeGroupSelectionProfileId': 'qci9',
                 'selectionCriteria': 'qci==9', 'prefUeGroupId': '9', 'prefUeGroupPriority': '900'},
            ],
            'UeMobilityGroupDefinition': [
                {'attributes': {'xc:operation': 'create'}, 'ueMobilityGroupDefinitionId': 'VoNR',
                 'selectionCriteria': '5qi==1', 'ueMobilityGroupId': '1', 'ueMobilityGroupPriority': '65535'},
                {'attributes': {'xc:operation': 'create'}, 'ueMobilityGroupDefinitionId': '5QI6',
                 'selectionCriteria': '5qi==6', 'ueMobilityGroupId': '66', 'ueMobilityGroupPriority': '65533'},
                {'attributes': {'xc:operation': 'create'}, 'ueMobilityGroupDefinitionId': 'qci6',
                 'selectionCriteria': 'qci==6', 'ueMobilityGroupId': '6', 'ueMobilityGroupPriority': '65534'},
                {'attributes': {'xc:operation': 'create'}, 'ueMobilityGroupDefinitionId': '5QI7',
                 'selectionCriteria': '5qi==7', 'ueMobilityGroupId': '77', 'ueMobilityGroupPriority': '999'},
                {'attributes': {'xc:operation': 'create'}, 'ueMobilityGroupDefinitionId': 'qci7',
                 'selectionCriteria': 'qci==7', 'ueMobilityGroupId': '7', 'ueMobilityGroupPriority': '1000'},
                {'attributes': {'xc:operation': 'create'}, 'ueMobilityGroupDefinitionId': '5QI9',
                 'selectionCriteria': '5qi==9', 'ueMobilityGroupId': '99', 'ueMobilityGroupPriority': '899'},
                {'attributes': {'xc:operation': 'create'}, 'ueMobilityGroupDefinitionId': 'qci9',
                 'selectionCriteria': 'qci==9', 'ueMobilityGroupId': '9', 'ueMobilityGroupPriority': '900'},
            ],
        }
        tmp_list = list(ue_dict.keys())
        for r in tmp_list:
            ue_dict[F'{r}_mos'] = [_ for _ in self.site.fdns if re.match(F'GNBCUCPFunction=[^,]*,UeGroupSelection=[^,]*,{r}=[^,]*$', _)]
        for r in tmp_list:
            for child_mo in ue_dict[r]:
                mos_exists = [_ for _ in ue_dict.get(F'{r}_mos') if
                              self.site.get_fdn_parameter(fdn=_, para='selectionCriteria') == child_mo.get('selectionCriteria')]
                if len(mos_exists) > 0:
                    ue_dict.update({'attributes': {'xc:operation': 'update'}, F'{r[0].lower()}{r[1:]}Id': mos_exists[0].split('=')[-1]})
                    self.mo_dict['mos_mos']['GNBCUCPFunction']['UeGroupSelection'][r].append(copy.deepcopy(child_mo))
                else:
                    self.mo_dict['mos_mos']['GNBCUCPFunction']['UeGroupSelection'][r].append(copy.deepcopy(child_mo))
