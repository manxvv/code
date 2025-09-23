from AuditUSID import AuditUSID
import os
import re
import json
from xml.dom.minidom import Document
import numpy as np
import pandas as pd


class Audit:
    def __init__(self, *, audit_usid: AuditUSID, node: str):
        """
            audit_usid : Main class with required for scripts creations
        """
        self.node = node
        self.audit_usid = audit_usid
        self.custom_log = self.audit_usid.custom_log
        self.mo_dict = {}
        self.s_dict = {'cli': [], 'cmedit': []}
        self.validate_existing_mo_parameter = True
        self.site = self.audit_usid.sites[self.node]
        self.me = self.site.me
        self.relative_path = {}
        self.set_node_site_and_para_for_dcgk(node)
        self.remark = '_'.join(self.__class__.__name__.split('_')[1:])
        self.tech = 'NR'

    @staticmethod
    def compare_current_and_gs_value(*, value, gpl) -> bool:
        if type(value) not in (dict, str, list): value = str(value)
        if type(value) is list and (sum([type(_) is dict for _ in value]) == len(value)) and \
                type(gpl) is list and (sum([type(_) is dict for _ in gpl]) == len(gpl)):
            return set([str(_) for _ in value]).difference(set([str(_) for _ in gpl])) == \
                set([str(_) for _ in gpl]).difference(set([str(_) for _ in value]))
        return value == gpl

    def add_mo_para_to_para_list(self, *, ldn: str, para: str, gpl, para_type: str = None, remark: str = None) -> None:
        def add_mo_para() -> None:
            self.audit_usid.gpl_list.append({
                'Node': self.node,
                'Technology': self.tech,
                'MO_Class': self.get_end_moc(ldn),
                'Parameter': para,
                'MO': ldn,
                'Current_Value': value,
                'Baseline': gpl,
                'Deviation': 'NO' if flag else 'YES',
                'Parameter_Type': para_type,
                'remark': remark
            })
        value, flag = None, False
        if self.site.fdn_exists(fdn=ldn):
            if para in self.site.mos.get(ldn, {}).keys():
                value = self.site.get_fdn_parameter(fdn=ldn, para=para)
            else:
                value, remark = 'N/F', 'Parameter not found'
            flag = self.compare_current_and_gs_value(value=value, gpl=gpl)
            add_mo_para()
        else:
            value, remark = None, 'MO not found'
            add_mo_para()
        #
        #
        # if not value: value = self.site.get_fdn_parameter(fdn=mo, para=para)
        # flag = self.compare_current_and_gs_value(value=value, gpl=gpl)
        # self.audit_usid.gpl_list.append({
        #     'Node': self.node,
        #     'MO_Class': self.get_end_moc(mo),
        #     'Parameter': para,
        #     'MO': mo,
        #     'Current_Value': value,
        #     'Baseline': gpl,
        #     'Deviation': 'NO' if flag else 'YES',
        #     'Parameter_Type': para_type,
        #     'remark': remark
        # })
        # return flag

    def set_node_site_and_para_for_dcgk(self, node):
        self.node = node
        self.mo_dict = {}
        self.site = self.audit_usid.sites[self.node]
        self.me = self.site.me
        self.s_dict = {'cli': [], 'cmedit': []}
        sc_name = '_'.join([self.node, self.audit_usid.circle, *self.__class__.__name__.split('_')[1:], '.txt'])
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
            if not os.path.exists(os.path.dirname(os.path.join(self.audit_usid.base_dir, *self.relative_path[sc]))):
                os.makedirs(os.path.dirname(os.path.join(self.audit_usid.base_dir, *self.relative_path[sc])))
            with open(os.path.join(self.audit_usid.base_dir, *self.relative_path[sc]), 'w') as f:
                f.write('\n'.join(self.s_dict[sc]))
            if sc == 'cli':
                merged_path = ['NA_SA_Script', '_'.join(self.__class__.__name__.split('_')[1:]) + F'_{self.audit_usid.circle}.txt']
                if len(self.s_dict[sc]) == 0: continue
                if not os.path.exists(os.path.dirname(os.path.join(self.audit_usid.base_dir, *merged_path))):
                    os.makedirs(os.path.dirname(os.path.join(self.audit_usid.base_dir, *merged_path)))
                with open(os.path.join(self.audit_usid.base_dir, *merged_path), 'a+') as f:
                    f.write('\n')
                    f.write('\n'.join(self.s_dict[sc]))
            self.s_dict[sc] = []

    def special_formate_scripts(self):
        pass

    def run(self):
        self.create_rpc_msg()
        # self.create_script_from_mo_dict()
        # self.write_script_file()
        # self.special_formate_scripts()


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

    def cmedit_cli_mo_form_dict(self, script_type='cmedit', mo_fdn='', adddict=None) -> list:
        """ :rtype: list """
        if 'attributes' not in adddict.keys(): return [F'#### Error on Dict Creation {mo_fdn}', '']
        script = []
        moid = adddict.get(self.get_moc_id(self.get_end_moc(mo_fdn)))
        ldn = mo_fdn
        if re.match('(.*,ManagedElement=[^,]*),(.*)', ldn):
            ldn = re.match('(.*,ManagedElement=[^,]*),(.*)', ldn).group(2)
        remove_para = ['attributes', str(self.get_moc_id(self.get_end_moc(mo_fdn)))]
        # Convert attributes to undate if mo exist
        if self.validate_existing_mo_parameter:
            if self.site.fdn_exists(fdn=ldn) and adddict['attributes']['xc:operation'] == 'create':
                adddict['attributes']['xc:operation'] = 'update'
            for para in adddict:
                if para in remove_para: continue
                self.add_mo_para_to_para_list_and_compare(mo=ldn, para=para, gpl=adddict[para])
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
        if len(mo_fdn) > 0 and mo_fdn.split(',')[-1].split('=')[0] not in self.audit_usid.log_mos:
            self.audit_usid.log_mos += F';{mo_fdn.split(",")[-1].split("=")[0]}.<w>'
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

    # def netconf_value_update(self, val):
    #     """ :rtype: str """
    #     if self.null_flag(val=val):
    #         return ''
    #     else:
    #         val = str(val).strip('"')
    #     if ',' in val and '=' in val:
    #         if 'ManagedElement=' in val:
    #             val = re.match('.*ManagedElement=[^,]*,(.*)', val).group(1)
    #         val = F'ManagedElement={self.node},{val}'
    #     elif re.match('.*\s\((.*)\)$', val):
    #         val = re.match('.*\s\((.*)\)$', val).group(1)
    #     return val
    #
    # def netconf_para_element(self, para, val):
    #     """ :rtype: object """
    #     val = self.netconf_value_update(val)
    #     if para in [None, 'None', 'null', 'empty', '', '""', [], {}] or val in [None, 'None', 'null', 'empty', '', '""', [], {}]: return None
    #     doc = Document()
    #     ele = doc.createElement(para)
    #     if val == 'XMLemptyELEMENT': return ele
    #     ele.appendChild(doc.createTextNode(val))
    #     return ele
    #
    # def netconf_mo_form_dict(self, adddict, moname='ManagedElement'):
    #     """ :rtype: Document """
    #     doc = Document()
    #     xml_mo = doc.createElement(moname)
    #     mo_attribute = self.mo_attr.get(moname)
    #     moname_id = self.get_moc_id(moname)
    #     del_flag = False
    #     if mo_attribute: xml_mo.setAttribute('xmlns', F'urn:com:ericsson:ecim:{mo_attribute}')
    #     if 'attributes' in adddict.keys():
    #         for attr in adddict['attributes'].keys():
    #             if adddict['attributes'][attr] in ['create', 'update']: continue
    #             xml_mo.setAttribute(attr, str(adddict['attributes'][attr]))
    #             if adddict['attributes'][attr] == 'delete':
    #                 del_flag = True
    #                 moname_id = self.get_moc_id(moname)
    #     for para in adddict.keys():
    #         if adddict[para] in [None, 'None', 'null', 'empty', '""', [], {}] or para == 'attributes':
    #             continue
    #         elif del_flag is True and moname_id != para:
    #             continue
    #         elif type(adddict[para]) == dict:
    #             xml_mo.appendChild(self.netconf_mo_form_dict(adddict[para], para))
    #         elif type(adddict[para]) == list:
    #             for val in adddict[para]:
    #                 if type(val) == dict:
    #                     xml_mo.appendChild(self.netconf_mo_form_dict(val, para))
    #                 else:
    #                     element = self.netconf_para_element(para, val)
    #                     if element is not None: xml_mo.appendChild(element)
    #         elif type(adddict[para]) in [int, str]:
    #             element = self.netconf_para_element(para, adddict[para])
    #             if element is not None: xml_mo.appendChild(element)
    #     return xml_mo
    #
    # def netconf_doc_form_dict(self, mo=None, mo_fdn='1', moc='ManagedElement'):
    #     """ :rtype: list """
    #     if mo in [None, 'None', '', [], {}]: return []
    #     doc = Document()
    #     doc.appendChild(self.netconf_mo_form_dict(
    #         {'attributes': {'message-id': str(mo_fdn), 'xmlns': 'urn:ietf:params:xml:ns:netconf:base:1.0'},
    #          'edit-config': {'target': {'running': 'XMLemptyELEMENT'},
    #                          'config': {'attributes': {'xmlns:xc': 'urn:ietf:params:xml:ns:netconf:base:1.0'}}}
    #          }, 'rpc'))
    #     doc.getElementsByTagName('config')[0].appendChild(self.netconf_mo_form_dict(mo, moc))
    #     # for para in ['loopback', 'cleartext']:
    #     #     for _ in doc.getElementsByTagName(para): _.firstChild.nodeValue = ''
    #     return [doc]
    #
    #
    # def netconf_hello_msg(self):
    #     """ :rtype: list """
    #     doc = Document()
    #     doc.appendChild(self.netconf_mo_form_dict(
    #         {'attributes': {'xmlns': 'urn:ietf:params:xml:ns:netconf:base:1.0'},
    #          'capabilities': {'capability': ['urn:ietf:params:netconf:base:1.0',
    #                                          'urn:com:ericsson:ebase:0.1.0', 'urn:com:ericsson:ebase:1.1.0']}}, 'hello')
    #     )
    #     lines = [doc.toprettyxml(encoding='UTF-8', indent='  ').decode('utf-8').strip()] + [']]>]]>']
    #     return lines
    #
    # def netconf_close_msg(self):
    #     """ :rtype: list """
    #     doc = Document()
    #     doc.appendChild(self.netconf_mo_form_dict({'attributes': {
    #         'message-id': 'Closing', 'xmlns': 'urn:ietf:params:xml:ns:netconf:base:1.0'}, 'close-session': 'XMLemptyELEMENT'}, 'rpc'))
    #     # for _ in doc.getElementsByTagName('close-session'): _.firstChild.nodeValue = ''
    #     lines = [doc.toprettyxml(encoding='UTF-8', indent='  ').decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', '').strip()] + \
    #             [']]>]]>', '']
    #     return lines
