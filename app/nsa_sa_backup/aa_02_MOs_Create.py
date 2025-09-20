import copy
from Script import Script


class aa_02_MOs_Create(Script):
    def create_rpc_msg(self):
        if self.node not in self.usid.nr_node: return
        # ToDo Need to update SCTP and localIpAddress, Validate if existing
        self.mo_dict['mos'] = {
            'managedElementId': self.node,
            'Transport': {'transportId': '1', 'SctpEndpoint': {}},
            'GNBCUCPFunction': {
                'gNBCUCPFunctionId': '1',
                'EndpointResource': {'endpointResourceId': '1', 'LocalSctpEndpoint': {}},
                'TermPointToAmf': [],
                'EUtraNetwork': {'eUtraNetworkId': '1', 'EUtranFrequency': []},
            },

        }
        # Transport, EndpointResource, LocalSctpEndpoint, SctpEndpoint
        tn_dict, a, b, c = self.site.get_sctp_local_sctp_dicts()
        if len(tn_dict) > 0: self.mo_dict['mos'].update(tn_dict)
        else: self.custom_log.log.exception(F'TN MOs need to be validated :  {self.node} -- {b} -- {c} -- {a} -- ')
        # TermPointToAmf
        tmp_list = ['termPointToAmfId', 'ipv6Address1', 'ipv6Address2', 'ipv4Address1', 'ipv4Address2', 'administrativeState',
                    'defaultAmf', 'pwsRestartHandling']
        self.mo_dict['amf'] = {'managedElementId': self.node, 'GNBCUCPFunction': {'gNBCUCPFunctionId': '1', 'TermPointToAmf': []}}
        for r in self.usid.db['TermPointToAmf'].itertuples():
            tmp_dict = {_: r.__getattribute__(_) for _ in tmp_list}
            tmp_dict |= {'attributes': {'xc:operation': 'create'}}
            self.mo_dict['amf']['GNBCUCPFunction']['TermPointToAmf'].append(copy.deepcopy(tmp_dict))


        self.mo_dict['tn___neww'] = {
            'managedElementId': self.node,
            'Transport': {'transportId': '1', 'SctpEndpoint': {
                'attributes': {'xc:operation': 'create'},
                'sctpEndpointId': 'XN', 'dtlsSctpSecurityMode': '0 (DISABLED)', 'portNumber': '38422',
                'localIpAddress': 'Transport=1,Router=LTE_NR,InterfaceIPv6=NR,AddressIPv6=NR_S1U_OAM',
                'sctpProfile': 'Transport=1,SctpProfile=1'}},
            'GNBCUCPFunction': {
                'gNBCUCPFunctionId': '1',
                'EndpointResource': {
                    'endpointResourceId': '1',
                    'LocalSctpEndpoint': {
                        'attributes': {'xc:operation': 'create'}, 'localSctpEndpointId': '4', 'interfaceUsed': '6 (XN)',
                        'sctpEndpointRef': 'Transport=1,SctpEndpoint=XN'}
                },
                'TermPointToAmf': [],
                'EUtraNetwork': {'eUtraNetworkId': '1', 'EUtranFrequency': []},
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
                    'UserPlaneProfile': {
                        'attributes': {'xc:operation': 'create'}, 'userPlaneProfileId': 'Default',
                        'UserPlaneProfileUeCfg': {
                            'attributes': {'xc:operation': 'create'}, 'userPlaneProfileUeCfgId': 'Base', 'dcDlAggCgPrio': '2 (EQUAL_PRIO)',
                            'dcDlAggActTime': '1', 'dcDlAggExpiryTimer': '100', 'dlPdcpMcgInitialRate': '20', 'dlPdcpScgInitialRate': '100',
                        }
                    }
                }
            },
        }


        # GNBCUUPFunction, GtpuSupervision, DcDlCfg, UserPlaneProfileUeCfg
        self.mo_dict['CUUP_mos'] = {
            'managedElementId': self.node,
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
                    'UserPlaneProfile': {
                        'attributes': {'xc:operation': 'create'}, 'userPlaneProfileId': 'Default',
                        'UserPlaneProfileUeCfg': {
                            'attributes': {'xc:operation': 'create'}, 'userPlaneProfileUeCfgId': 'Base', 'dcDlAggCgPrio': '2 (EQUAL_PRIO)',
                            'dcDlAggActTime': '1', 'dcDlAggExpiryTimer': '100', 'dlPdcpMcgInitialRate': '20', 'dlPdcpScgInitialRate': '100',
                        }
                    }
                }
            },
        }

        # EUtranFreqRelation
        # {'attributes': {'xc:operation': 'create'}, 'mcpcPCellEUtranFreqRelProfileId': 'Default'},
        # {'attributes': {'xc:operation': 'create'}, 'mcpcPCellEUtranFreqRelProfileId': 'HO'},
        # {'attributes': {'xc:operation': 'create'}, 'mcpcPCellEUtranFreqRelProfileId': 'NOHO'}
        mcpcPCell = list(set(['Default', 'HO', 'NOHO'] + [
            _.split('=')[-1] for _ in self.usid.db['EUtranFreqRelation']['mcpcPCellEUtranFreqRelProfileRef'].tolist() if '=' in _]))
        trStSa = list(set(['Default'] + [
            _.split('=')[-1] for _ in self.usid.db['EUtranFreqRelation']['trStSaEUtranFreqRelProfileRef'].tolist() if '=' in _]))
        ueMC = list(set(['Default'] + [
            _.split('=')[-1] for _ in self.usid.db['EUtranFreqRelation']['ueMCEUtranFreqRelProfileRef'].tolist() if '=' in _]))

        self.mo_dict['EUtranFreqRelation'] = {
            'managedElementId': self.node,
            'GNBCUCPFunction': {
                'gNBCUCPFunctionId': '1',
                'EUtraNetwork': {'eUtraNetworkId': '1', 'EUtranFrequency': []},
                'Mcpc': {'mcpcId': '1', 'McpcPCellEUtranFreqRelProfile': [
                    {'attributes': {'xc:operation': 'create'}, 'mcpcPCellEUtranFreqRelProfileId': _} for _ in mcpcPCell],
                },
                'TrafficSteering': {'trafficSteeringId': '1', 'TrStSaEUtranFreqRelProfile': [
                    {'attributes': {'xc:operation': 'create'}, 'trStSaEUtranFreqRelProfileId': _} for _ in trStSa],
                },
                'UeMC': {'ueMCId': '1', 'UeMCEUtranFreqRelProfile': [
                    {'attributes': {'xc:operation': 'create'}, 'ueMCEUtranFreqRelProfileId': _} for _ in ueMC],
                },
                'NRCellCU': []
            }
        }
        # EUtranFrequency
        for r in self.usid.db['EUtranFreqRelation']['eUtranFreqRelationId'].tolist():
            if not self.site.fdn_exists(fdn=F'GNBCUCPFunction=1,EUtraNetwork=1,EUtranFrequency={r}'):
                self.mo_dict['EUtranFreqRelation']['GNBCUCPFunction']['EUtraNetwork']['EUtranFrequency'].append({
                    'attributes': {'xc:operation': 'create'}, 'arfcnValueEUtranDl': r, 'eUtranFrequencyId': r
                })
        # # McpcPCellEUtranFreqRelProfile
        # mo_ids = [_.split('=')[-1] for _ in self.usid.db['EUtranFreqRelation']['mcpcPCellEUtranFreqRelProfileRef'].tolist()] + ['HO', 'NOHO']
        # for r in list(set(mo_ids)):
        #     self.mo_dict['EUtranFreqRelation']['GNBCUCPFunction']['Mcpc']['McpcPCellEUtranFreqRelProfile'].append({
        #         'attributes': {'xc:operation': 'create'}, 'mcpcPCellEUtranFreqRelProfileId': r,
        #         # 'McpcPCellEUtranFreqRelProfileUeCfg': {
        #         #     'attributes': {'xc:operation': 'create'}, 'mcpcPCellEUtranFreqRelProfileUeCfgId': 'Base',
        #         #     'inhibitMeasForCellCandidate': 'true' if 'NOHO' in r else 'false',
        #         #     'rsrpCandidateB2Offsets': {'threshold1Offset': '0', 'threshold2EUtraOffset': '0'}}
        #     })
        # # UeMCEUtranFreqRelProfile
        # mo_ids = []
        # for r in self.usid.db['EUtranFreqRelation'].itertuples():
        #     mo_id = r.__getattribute__('ueMCEUtranFreqRelProfileRef').split('=')[-1]
        #     if mo_id not in mo_ids:
        #         mo_ids += [mo_id]
        #         self.mo_dict['EUtranFreqRelation']['GNBCUCPFunction']['UeMC']['UeMCEUtranFreqRelProfile'].append({
        #             'attributes': {'xc:operation': 'create'}, 'ueMCEUtranFreqRelProfileId': mo_id})

        # EUtranFreqRelation
        tmp_list = ['eUtranFreqRelationId', 'allowedMeasBandwidth', 'anrMeasOn', 'cellReselectionPriority',
                    'eUtranFallbackPrioEc', 'pMaxEUtra', 'presenceAntennaPort1', 'qRxLevMin',
                    'tReselectionEUtra', 'threshXHighP', 'threshXLowP', 'voicePrio', 'eUtranFrequencyRef',
                    'mcpcPCellEUtranFreqRelProfileRef', 'trStSaEUtranFreqRelProfileRef', 'ueMCEUtranFreqRelProfileRef']
        tmp_mo_list = []
        for r in self.usid.db['EUtranFreqRelation'].itertuples():
            tmp_dict = {_: r.__getattribute__(_) for _ in tmp_list}
            tmp_dict |= {'attributes': {'xc:operation': 'create'}}
            tmp_mo_list.append(copy.deepcopy(tmp_dict))
        # ToDo Update ceel actual list
        # cell_list = ['TN_5_EE_T1_OM_5_xxxxPLKO14_A', 'TN_5_EE_T1_OM_5_xxxxPLKO14_B']
        # cell_list = ['TN_5_EE_T1_OM_5_xxxxPLKO10_B', 'TN_5_EE_T1_OM_5_xxxxPLKO10_A']
        for r in self.site.cu_cell:
            self.mo_dict['EUtranFreqRelation']['GNBCUCPFunction']['NRCellCU'].append({
                'attributes': {'xc:operation': 'update'}, 'nRCellCUId': r, 'EUtranFreqRelation': copy.deepcopy(tmp_mo_list)
            })

        # GNBCUCPFunction, DcDlCfg, UserPlaneProfileUeCfg
        self.mo_dict['GNBCUCPFunction_mos'] = {
            'managedElementId': self.node,
            'GNBCUCPFunction': {
                'gNBCUCPFunctionId': '1',
                'AnrFunction': {'anrFunctionId': '1', 'AnrFunctionEUtran': {
                    'attributes': {'xc:operation': 'create'}, 'anrFunctionEUtranId': '1',
                    'AnrFunctionEUtranUeCfg': {'attributes': {'xc:operation': 'create'}, 'anrFunctionEUtranUeCfgId': '1'}
                }},
                'UeMC': {
                    'ueMCId': '1',
                    'UeMCNrFreqRelProfile': {'attributes': {'xc:operation': 'create'}, 'ueMCNrFreqRelProfileId': 'Midband'},
                    'UeMCCellProfile': {'attributes': {'xc:operation': 'create'}, 'ueMCCellProfileId': 'Default'},
                },
                'Mcpc': {'mcpcId': '1', 'McpcPCellProfile': [
                    {'attributes': {'xc:operation': 'create'}, 'mcpcPCellProfileId': 'MidBand',
                     'McpcPCellProfileUeCfg': [
                         {'attributes': {'xc:operation': 'create'}, 'mcpcPCellProfileUeCfgId': 'VoNR', 'mcpcQuantityList': '0 (RSRP)',
                          'ueConfGroupList': ['5'], 'ueGroupList': ['1'], 'rsrpSearchTimeRestriction': '-1', 'rsrpCriticalEnabled': 'false',
                          'rsrpCandidateA5': {'hysteresis': '10', 'threshold1': '-99', 'threshold2': '-101', 'timeToTrigger': '640'},
                          'rsrpCandidateB2': {'hysteresis': '10', 'threshold1': '-99', 'threshold2EUtra': '-113', 'timeToTrigger': '640'},
                          'rsrpSearchZone': {'hysteresis': '10', 'threshold': '-99', 'timeToTrigger': '320', 'timeToTriggerA1': '-1'},
                          'rsrpCritical': {'hysteresis': '10', 'threshold': '-111', 'timeToTrigger': '320', 'timeToTriggerA1': '-1'},
                          },
                     ]
                     }
                ]},
                'Mcfb': {
                    'attributes': {'xc:operation': 'create'}, 'mcfbId': '1',
                    'McfbCellProfile': {'attributes': {'xc:operation': 'create'}, 'mcfbCellProfileId': '1'}
                },
                'UeGroupSelection': {
                    'attributes': {'xc:operation': 'create'}, 'ueGroupSelectionId': '1',
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
                    # ToDo Need to add logic for count of MOs
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
                        'tInactivityTimer': '15', 'tInactivityTimerEndcSn': '10', 'tInactivityTimerNrdcSn': '10',
                    }},
                },
                'EmCall': {'attributes': {'xc:operation': 'create'}, 'emCallId': '1', 'arpPrioEm5qi1List': ['1'], 'arpPrioEm5qi5List': ['1']},
            },
        }
        # GNBDUFunction -- mos
        self.mo_dict['GNBCUUPFunction_mos'] = {
            'managedElementId': self.node,
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
                        'drxInactivityTimer': '5 (INACTIVITYTIMER_5MS)', 'drxLongCycle': '4 (LONGCYCLE_40MS)',
                        'drxOnDurationTimer': '36 (ONDURATIONTIMER_5MS)', 'drxRetransmissionTimerDl': '6',
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
