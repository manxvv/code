import copy
import re
import os
from Script import Script
from datetime import datetime


class aa_Command(Script):
    def create_rpc_msg(self): pass
    def special_formate_scripts(self):
        date_str = datetime.now().strftime("%m%d%Y")
        all_nodes = ";".join(self.usid.df_site.node.unique())
        nr_nodes = ";".join(self.usid.df_site.loc[self.usid.df_site.nr].node.unique())
        lte_nodes = ";".join(self.usid.df_site.loc[self.usid.df_site.lte].node.unique())
        nr_bb_reset = '\n'.join(self.retart_commands_list())

        status_command = ';'.join([
            F'CmFunction.(syncStatus)',
            F'NRSectorCarrier.(arfcnDL,arfcnUL,bSChannelBwDL,bSChannelBwUL,configuredMaxTxPower,operationalState)',
            F'NRCellDU.(administrativeState,cellState,operationalState,serviceState,ssbDuration,ssbFrequency,ssbOffset,ssbPeriodicity)',
            F'EUtranCellTDD.(administrativeState,cellSubscriptionCapacity,channelBandwidth,earfcn,operationalState)',
            F'EUtranCellFDD.(administrativeState,dlChannelBandwidth,earfcndl,earfcnul,operationalState,ulChannelBandwidth)',
            F'SectorCarrier.(SectorCarrierId,configuredMaxTxPower,operationalState,reservedBy,rfBranchRxRef,rfBranchTxRef)',
            F'SectorEquipmentFunction.(administrativeState,operationalState,availableHwOutputPower,reservedBy,rfBranchRef)',
            F'FieldReplaceableUnit.(administrativeState,operationalState,productData)',
            F'TermPointToAmf.(administrativeState,operationalState,defaultAmf,ipv4Address1,ipv4Address2,ipv6Address1,ipv6Address2,usedIpAddress)',
        ])
        self.s_dict['cli'] = [F"""
##########################- Pre Check -##########################
####---- NodeStatus ----####
pre_status_{self.usid.circle}_{self.usid.enm}_{date_str}.txt
cmedit get {all_nodes} {status_command} --list

####---- NodeAlarms ----####
pre_alarms_{self.usid.circle}_{self.usid.enm}_{date_str}.txt
alarm get {all_nodes} --list

####---- MO Dump ----####
pre_dump_{self.usid.circle}_{self.usid.enm}_{date_str}.txt
cmedit export -n {all_nodes} filetype dynamic --filecompression gzip
cmedit export --status --job jobid
cmedit export --download --job jobid

##########################- Activity -##########################
####---- Activity ----####
Select Parallel operation/Skip to next operation during import of Bulk Files
1. Create pre CV ---  Use CLI Terminal
cmedit action {all_nodes} BrmBackupManager=1 createBackup.(name="pre_NSA_SA_{date_str}")

2. Load ---  01_5qiTable_BWP using Bulk import
3. Load ---  02_MOs_Create using Bulk import
4. Load ---  03_Lock_NR using Bulk import (If you have NR cells unlocked during pre-check)
5. Load ---  04_Parameter using Bulk import

Run Below commands on CLI terminal
cmedit set {nr_nodes} GNBCUCPFunction,NRCellCU,EUtranCellRelation isHoAllowed=true --force

6. Load ---  05_UnLock_NR (If you have NR cells unlocked during pre-check)
7. Create post CV ---  Use CLI Terminal
cmedit action {all_nodes} BrmBackupManager=1 createBackup.(name="post_NSA_SA_{date_str}")

7. Restart the NR Nodes base on Circle/Market guidelines

###############################################################################
#### Restart Command for NR Nodes ####
###############################################################################

{nr_bb_reset}

###############################################################################

8. Validate and Check Status using get commands

##########################- Some Important get CLI Commands -##########################
cmedit get {nr_nodes} GNBDUFunction,TermPointToAmf.(administrativeState,operationalState,ipv4Address1,ipv4Address2,ipv6Address1,ipv6Address2) -t
cmedit get {nr_nodes} GNBDUFunction,NRCellDU.(administrativeState,operationalState,cellBarred,cellReservedForOperator) -t
cmedit get {nr_nodes} GNBDUFunction,NRSectorCarrier.(administrativeState,operationalState) -t
cmedit get {lte_nodes} ENodeBFunction,EUtranCellFDD.(administrativeState,operationalState,cellBarred,primaryPlmnReserved) -t
cmedit get {lte_nodes} ENodeBFunction,EUtranCellTDD.(administrativeState,operationalState,cellBarred,primaryPlmnReserved) -t
cmedit get {lte_nodes} ENodeBFunction,NbIotCell.(administrativeState,operationalState) -t
cmedit get {lte_nodes} SectorCarrier.(operationalState,reservedBy,sectorFunctionRef) -t
cmedit get {all_nodes} SectorEquipmentFunction.(administrativeState,operationalState) -t
cmedit get {all_nodes} FieldReplaceableUnit.(administrativeState,operationalState,productData) -t

##########################- Post Check -##########################
####---- NodeStatus ----####
post_status_{self.usid.circle}_{self.usid.enm}.txt
cmedit get {all_nodes} {status_command} --list

####---- NodeAlarms ----####
post_alarms_{self.usid.circle}_{self.usid.enm}_{date_str}.txt
alarm get {all_nodes} --list

####---- MO Dump ----####
post_dump_{self.usid.circle}_{self.usid.enm}_{date_str}.txt
cmedit export -n {all_nodes} filetype dynamic --filecompression gzip
cmedit export --status --job jobid
cmedit export --download --job jobid

##########################- Some Important Commands -##########################
##########################- Run it at your Own Risk -##########################
##########################- Donot Run if you dont understand any of these commands -##########################
####---- Lock All NR Cells ----####
cmedit set {nr_nodes} GNBDUFunction,NRCellDU administrativeState=LOCKED --force
cmedit set {nr_nodes} GNBDUFunction,NRSectorCarrier administrativeState=LOCKED --force

####---- Unlock All NR Cells ----####
cmedit set {nr_nodes} GNBDUFunction,NRSectorCarrier administrativeState=UNLOCKED --force
cmedit set {nr_nodes} GNBDUFunction,NRCellDU administrativeState=UNLOCKED --force

####---- set NRCellCU cell Parameters for transmitSib----####
cmedit set {nr_nodes} GNBDUFunction,NRCellCU transmitSib2=true --force
cmedit set {nr_nodes} GNBDUFunction,NRCellCU transmitSib4=true --force
cmedit set {nr_nodes} GNBDUFunction,NRCellCU transmitSib5=true --force

###############################################################################
###############################################################################

        """]

        self.write_script_file()

    def write_script_file(self):
        """ :rtype: None """
        if len(self.s_dict['cli']) > 0:
            merged_path = os.path.join(self.usid.base_dir, F'00_Command_{self.usid.circle}_{self.usid.enm}.txt')
            if not os.path.exists(os.path.dirname(merged_path)): os.makedirs(os.path.dirname(merged_path))
            with open(merged_path, 'a+') as f:
                f.write('\n')
                f.write('\n'.join(self.s_dict['cli']))
            self.s_dict['cli'] = []

    def retart_commands_list(self):
        restart_commands_list = []
        for node in self.usid.df_site.loc[(self.usid.df_site.nr)].node.unique():
            self.set_node_site_and_para_for_dcgk(node=node)
            restart_commands_list.append(
                F'cmedit action {self.site.me},Equipment=1,FieldReplaceableUnit={self.site.bbu} restartunit.('
                F'restartrank=RESTART_COLD,restartreason=PLANNED_RECONFIGURATION,restartinfo=NSAtoSA) --force'
            )
        return restart_commands_list