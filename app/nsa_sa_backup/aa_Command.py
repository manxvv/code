import copy
import re
import os
from Script import Script
from datetime import datetime

class aa_Command(Script):
    def create_rpc_msg(self): pass
    def special_formate_scripts(self):
        date_str = datetime.now().strftime("%m%d%Y")
        all_nodes = ";".join(self.usid.nodes)
        status_command = ';'.join([
            F'CmFunction.(syncStatus)',
            F'NRSectorCarrier.(arfcnDL,arfcnUL,bSChannelBwDL,bSChannelBwUL,configuredMaxTxPower,operationalState)',
            F'NRCellDU.(administrativeState,cellState,operationalState,serviceState,ssbDuration,ssbFrequency,ssbOffset,ssbPeriodicity)',
            F'EUtranCellTDD.(administrativeState,cellSubscriptionCapacity,channelBandwidth,earfcn,operationalState)',
            F'EUtranCellFDD.(administrativeState,dlChannelBandwidth,earfcndl,earfcnul,operationalState,ulChannelBandwidth)',
            F'SectorCarrier.(SectorCarrierId,configuredMaxTxPower,operationalState,reservedBy,rfBranchRxRef,rfBranchTxRef)',
            F'SectorEquipmentFunction.(administrativeState,operationalState,availableHwOutputPower,reservedBy,rfBranchRef)',
            F'FieldReplaceableUnit.(administrativeState,operationalState,productData)',
            F'TermPointToAmf.(administrativeState,operationalState,defaultAmf,ipv4Address1,ipv4Address2,ipv6Address1,ipv6Address2,usedIpAddress)'
        ])
        self.s_dict['cli'] = [
            F'##########################- Pre Check -##########################',
            F'####---- NodeStatus ----####',
            F'pre_status_{self.usid.circle}_{self.usid.enm}_{date_str}.txt',
            F'',
            F'cmedit get {all_nodes} {status_command} --list',
            F'',
            F'####---- NodeAlarms ----####',
            F'pre_alarms_{self.usid.circle}_{self.usid.enm}_{date_str}.txt',
            F'',
            F'alarm get {all_nodes} --list',
            F'',
            F'####---- MO Dump ----####',
            F'pre_dump_{self.usid.circle}_{self.usid.enm}_{date_str}.txt',
            F'',
            F'cmedit get {all_nodes} {self.usid.log_mos} --dynamic',
            F'',
            F'##########################- Activity -##########################',
            F'####---- Activity ----####',
            F'Select Parallel operation/Skip to next operation during import of Bulk Files',
            F'1. Create pre CV ---  Use CLI Terminal',
            F'',
            F'cmedit action {all_nodes} BrmBackupManager=1 createBackup.(name="pre_NSA_SA_{date_str}")',
            F'',
            F'2. Load ---  01_5qiTable_BWP using Bulk import',
            F'3. Load ---  02_MOs_Create using Bulk import',
            F'4. Load ---  03_Lock_NR using Bulk import (If you have NR cells unlocked during pre-check)',
            F'5. Load ---  04_Parameter using Bulk import',
            F'      Run Below commands on CLI terminal',
            F'      ',
            F'      cmedit set {all_nodes} GNBDUFunction,NRCellCU transmitSib2=true --force',
            F'      cmedit set {all_nodes} GNBDUFunction,NRCellCU transmitSib4=true --force',
            F'      cmedit set {all_nodes} GNBDUFunction,NRCellCU transmitSib5=true --force',
            F'      ',
            F'      ',
            F'6. Load ---  05_UnLock_NR (If you have NR cells unlocked during pre-check)',
            F'7. Create post CV ---  Use CLI Terminal',
            F'',
            F'cmedit action {all_nodes} BrmBackupManager=1 createBackup.(name="post_NSA_SA_{date_str}")',
            F'',
            F'7. Restart the NR Nodes base on Circle/Market guidelines',
            F'8. Validate and Check Status using get commands',
            F'',
            F'##########################- Some Important get CLI Commands -##########################',
            F'cmedit get {all_nodes} GNBDUFunction,TermPointToAmf.(administrativeState,operationalState,ipv4Address1,ipv4Address2,ipv6Address1,ipv6Address2) -t',
            F'cmedit get {all_nodes} GNBDUFunction,NRCellDU.(administrativeState,operationalState,cellBarred,cellReservedForOperator) -t',
            F'cmedit get {all_nodes} GNBDUFunction,NRSectorCarrier.(administrativeState,operationalState) -t',
            F'cmedit get {all_nodes} ENodeBFunction,EUtranCellFDD.(administrativeState,operationalState,cellBarred,primaryPlmnReserved) -t',
            F'cmedit get {all_nodes} ENodeBFunction,EUtranCellTDD.(administrativeState,operationalState,cellBarred,primaryPlmnReserved) -t',
            F'cmedit get {all_nodes} ENodeBFunction,NbIotCell.(administrativeState,operationalState) -t',
            F'cmedit get {all_nodes} SectorCarrier.(operationalState,reservedBy,sectorFunctionRef) -t',
            F'cmedit get {all_nodes} SectorEquipmentFunction.(administrativeState,operationalState) -t',
            F'cmedit get {all_nodes} FieldReplaceableUnit.(administrativeState,operationalState,productData) -t',
            F'',
            F'',
            F'##########################- Post Check -##########################',
            F'####---- NodeStatus ----####',
            F'post_status_{self.usid.circle}_{self.usid.enm}.txt',
            F'',
            F'cmedit get {all_nodes} ',
            F'CmFunction.(syncStatus);',
            F'NRSectorCarrier.(arfcnDL,arfcnUL,bSChannelBwDL,bSChannelBwUL,configuredMaxTxPower,operationalState);',
            F'NRCellDU.(administrativeState,cellState,operationalState,serviceState,ssbDuration,ssbFrequency,ssbOffset,ssbPeriodicity);',
            F'EUtranCellTDD.(administrativeState,cellSubscriptionCapacity,channelBandwidth,earfcn,operationalState);',
            F'EUtranCellFDD.(administrativeState,dlChannelBandwidth,earfcndl,earfcnul,operationalState,ulChannelBandwidth);',
            F'SectorCarrier.(SectorCarrierId,configuredMaxTxPower,operationalState,reservedBy,rfBranchRxRef,rfBranchTxRef);',
            F'SectorEquipmentFunction.(administrativeState,operationalState,availableHwOutputPower,reservedBy,rfBranchRef);',
            F'FieldReplaceableUnit.(administrativeState,operationalState,productData);',
            F'TermPointToAmf.(administrativeState,operationalState,defaultAmf,ipv4Address1,ipv4Address2,ipv6Address1,ipv6Address2,usedIpAddress) --list',
            F'',
            F'',
            F'####---- NodeAlarms ----####',
            F'post_alarms_{self.usid.circle}_{self.usid.enm}_{date_str}.txt',
            F'',
            F'alarm get {all_nodes} --list',
            F'',
            F'####---- MO Dump ----####',
            F'post_dump_{self.usid.circle}_{self.usid.enm}_{date_str}.txt',
            F'',
            F'cmedit get {all_nodes} {self.usid.log_mos} --dynamic',
            F'',
            F'',

            F'##########################- Some Important Commands -##########################',
            F'##########################- Run it at your Own Risk -##########################',
            F'##########################- Donot Run if you dont understand any of these commands -##########################',
            F'####---- Lock All NR Cells ----####',
            F'cmedit set {all_nodes} GNBDUFunction,NRCellDU administrativeState=LOCKED --force',
            F'cmedit set {all_nodes} GNBDUFunction,NRSectorCarrier administrativeState=LOCKED --force',
            F'',
            F'####---- Unlock All NR Cells ----####',
            F'cmedit set {all_nodes} GNBDUFunction,NRSectorCarrier administrativeState=UNLOCKED --force',
            F'cmedit set {all_nodes} GNBDUFunction,NRCellDU administrativeState=UNLOCKED --force',
            F'',
            F'####---- set CU cell Parameters for transmitSib----####',
            F'cmedit set {all_nodes} GNBDUFunction,NRCellCU transmitSib2=true --force',
            F'cmedit set {all_nodes} GNBDUFunction,NRCellCU transmitSib4=true --force',
            F'cmedit set {all_nodes} GNBDUFunction,NRCellCU transmitSib5=true --force',
            F'',
            F'###############################################################################',
            F'###############################################################################',
            F'',
        ]

        self.write_script_file()

    def write_script_file(self):
        """ :rtype: None """
        if len(self.s_dict['cli']) > 0:
            merged_path = ['_'.join(self.__class__.__name__.split('_')[1:]) + F'_{self.usid.circle}_{self.usid.enm}.txt']
            if not os.path.exists(os.path.dirname(os.path.join(self.usid.base_dir, *merged_path))):
                os.makedirs(os.path.dirname(os.path.join(self.usid.base_dir, *merged_path)))
            with open(os.path.join(self.usid.base_dir, *merged_path), 'a+') as f:
                f.write('\n')
                f.write('\n'.join(self.s_dict['cli']))
            self.s_dict['cli'] = []
