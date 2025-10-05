from USID import USID
import os
import re
import json
from xml.dom.minidom import Document
import numpy as np
import pandas as pd

# from django.db.models import Q
# from scripter.models import MoAttribute, MoRelation, MoName, MoDetail


# import sys
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mScripter.settings")
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class Script:
    def __init__(self, *, usid: USID, node: str):
        """
            usid : Main class with required for scripts creations
        """
        self.node = node
        self.usid = usid
        self.custom_log = self.usid.custom_log
        self.mo_dict = {}
        self.s_dict = {'cli': [], 'cmedit': []}
        self.validate_existing_mo_parameter = True
        self.site = self.usid.sites[self.node]
        self.me = self.site.me
        self.site_dict = self.usid.df_site.loc[(self.usid.df_site.node == self.node)].squeeze().to_dict()
        self.relative_path = {}
        self.set_node_site_and_para_for_dcgk(node)
        self.remark = '_'.join(self.__class__.__name__.split('_')[1:])

    @staticmethod
    def compare_current_and_gs_value(*, value, gpl) -> bool:
        if type(value) not in (dict, str, list): value = str(value)
        if type(value) is list and (sum([type(_) is dict for _ in value]) == len(value)) and \
                type(gpl) is list and (sum([type(_) is dict for _ in gpl]) == len(gpl)):
            return set([str(_) for _ in value]).difference(set([str(_) for _ in gpl])) == \
                set([str(_) for _ in gpl]).difference(set([str(_) for _ in value]))
        return value == gpl

    def add_mo_para_to_para_list_and_compare(self, *, mo: str, para: str, value=None, gpl, remark: str = None) -> bool:
        if not value: value = self.site.get_fdn_parameter(fdn=mo, para=para)
        flag = self.compare_current_and_gs_value(value=value, gpl=gpl)
        remark = self.remark if not remark else remark
        self.usid.gpl_list.append({'node': self.node, 'mo': mo, 'para': para,  'value': value, 'gpl': gpl, 'flag': flag, 'remark': remark})
        return flag

    def set_node_site_and_para_for_dcgk(self, node):
        self.node = node
        self.mo_dict = {}
        self.site = self.usid.sites[self.node]
        self.me = self.site.me
        self.site_dict = self.usid.df_site.loc[(self.usid.df_site.node == self.node)].squeeze().to_dict()
        self.s_dict = {'cli': [], 'cmedit': []}
        sc_name = '_'.join([self.node, self.usid.circle, *self.__class__.__name__.split('_')[1:], '.txt'])
        self.relative_path = {
            'cli': ['Nodes', self.node, 'bulk_' + sc_name],
            'cmedit': ['Nodes', self.node, 'cli_' + sc_name]
        }

    def create_rpc_msg(self): pass

    def create_script_from_mo_dict(self):
        for mo_fdn in self.mo_dict:
            self.s_dict['cli'].extend(self.cmedit_list_form_dict('cli', mo_fdn, self.mo_dict.get(mo_fdn, {})))
            self.s_dict['cmedit'].extend(self.cmedit_list_form_dict('cmedit', mo_fdn, self.mo_dict.get(mo_fdn, {})))

    def write_script_file(self):
        """ :rtype: None """
        for sc in ['cli', 'cmedit']:
            if len(self.s_dict[sc]) == 0: continue
            if not os.path.exists(os.path.dirname(os.path.join(self.usid.base_dir, *self.relative_path[sc]))):
                os.makedirs(os.path.dirname(os.path.join(self.usid.base_dir, *self.relative_path[sc])))
            with open(os.path.join(self.usid.base_dir, *self.relative_path[sc]), 'w') as f:
                f.write('\n'.join(self.s_dict[sc]))
            if sc == 'cli':
                merged_path = ['NA_SA_Script', '_'.join(self.__class__.__name__.split('_')[1:]) + F'_{self.usid.circle}.txt']
                if len(self.s_dict[sc]) == 0: continue
                if not os.path.exists(os.path.dirname(os.path.join(self.usid.base_dir, *merged_path))):
                    os.makedirs(os.path.dirname(os.path.join(self.usid.base_dir, *merged_path)))
                with open(os.path.join(self.usid.base_dir, *merged_path), 'a+') as f:
                    f.write('\n')
                    f.write('\n'.join(self.s_dict[sc]))
            self.s_dict[sc] = []

    def special_formate_scripts(self):
        pass

    def run(self):
        self.create_rpc_msg()
        self.create_script_from_mo_dict()
        self.write_script_file()
        self.special_formate_scripts()

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

    def cmedit_cli_mo_form_dict(self, script_type='cmedit', mo_fdn='', adddict=None) -> list:
        """ :rtype: list """
        if 'attributes' not in adddict.keys(): return [F'#### Error on Dict Creation {mo_fdn}', '']
        script = []
        mocId = self.get_moc_id(self.get_end_moc(mo_fdn))
        moid = adddict.get(self.get_moc_id(self.get_end_moc(mo_fdn)))
        ldn = mo_fdn
        if re.match('(.*,ManagedElement=[^,]*),(.*)', mo_fdn):
            ldn = re.match('(.*,ManagedElement=[^,]*),(.*)', mo_fdn).group(2)
        remove_para = ['attributes', str(self.get_moc_id(self.get_end_moc(mo_fdn)))]
        # Convert attributes to undate if mo exist
        if self.validate_existing_mo_parameter:
            if self.site.fdn_exists(fdn=ldn) and adddict['attributes']['xc:operation'] == 'create':
                adddict['attributes']['xc:operation'] = 'update'
            for para in adddict:
                if para in remove_para: continue
                if adddict[para] in [None, 'None', '', [], {}]: remove_para.append(para)
                elif self.add_mo_para_to_para_list_and_compare(mo=ldn, para=para, gpl=adddict[para]):
                    remove_para.append(para)
        else:
            remove_para += [para for para in adddict if para not in remove_para and adddict[para] in [None, 'None', '', [], {}]]
        operation = adddict.get('attributes', {}).get('xc:operation')
        if operation == 'delete': remove_para = adddict.keys()
        elif operation == 'update': operation = 'set'
        for para in remove_para: adddict.pop(para, None)
        if operation is None or (operation == 'set' and len(adddict) == 0): return []
        elif script_type == 'cmedit':
            if operation == 'delete': script = [F'cmedit delete {mo_fdn} -ALL --force']
            elif operation in ['create', 'set']:
                script = [F'cmedit {operation} {mo_fdn} ' + F'{self.get_moc_id(self.get_end_moc(mo_fdn))}:{moid}' if operation == 'create' else '']
                if operation == 'create' and len(adddict) > 0: script[0] = script[0] + '; '
                script[0] = script[0] + '; '.join([F'{key}:{self.cmedit_cli_norm_value(adddict.get(key))}' for key in adddict])
                if len(adddict) > 0: script[0] = script[0] + ' --force'
                for key in adddict:
                    script += [F'{key}:{self.cmedit_cli_norm_value(adddict.get(key))}']
        elif script_type == 'cli':
            script.extend([operation, F'FDN : {mo_fdn}'])
            if operation == 'create':
                script.extend([F'{self.get_moc_id(self.get_end_moc(mo_fdn))} : {moid}'])
            script.extend([F'{key} : {self.cmedit_cli_norm_value(adddict.get(key))}' for key in adddict])
            script.append('')
        return script

    def cmedit_list_form_dict(self, script_type='cmedit', mo_fdn=None, mo=None):
        """ :rtype: list """
        if mo is [None, 'None', '', {}, []] or mo_fdn in [None, 'None', '', {}, []]: return []
        if mo.get('managedElementId') is not None: mo_fdn = F'{self.me}'
        script = []
        if len(mo_fdn) > 0 and mo_fdn.split(',')[-1].split('=')[0] not in self.usid.log_mos:
            self.usid.log_mos += F';{mo_fdn.split(",")[-1].split("=")[0]}.<w>'
        if mo.get('attributes') is not None:
            tmp_dict = dict((k, v) for k, v in mo.items() if k[0].islower())
            script.extend(self.cmedit_cli_mo_form_dict(script_type, mo_fdn, tmp_dict))
        for para in mo.keys():
            if para[0].isupper():
                if type(mo[para]) == list:
                    for child_mo in mo[para]:
                        script.extend(self.cmedit_list_form_dict(script_type, F'{mo_fdn},{para}={child_mo.get(self.get_moc_id(para))}', child_mo))
                if type(mo[para]) == dict:
                    script.extend(self.cmedit_list_form_dict(script_type, F'{mo_fdn},{para}={mo[para].get(self.get_moc_id(para))}', mo[para]))
        return script

    @staticmethod
    def get_end_moc(mo: str) -> str: return mo.split(',')[-1].split('=')[0]

    @staticmethod
    def get_moc_id(moc: str) -> str: return moc[0].lower() + moc[1:] + 'Id'

    def check_if_node_is_nr_node_and_ready_for_scripting(self) -> bool:
        """ :rtype: bool """
        flag = False
        return flag
