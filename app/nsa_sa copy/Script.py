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
        self.site = self.usid.sites[self.node]
        self.me = ''
        self.relative_path = {}
        self.set_node_site_and_para_for_dcgk(node)

        # File Name and Path

        # sc_name = '_'.join([self.node, self.__class__.__name__, self.usid.circle])
        # self.relative_path = {
        #     'cli': ['Nodes', self.node, 'bulk_import_' + sc_name + '.txt'],
        #     'cmedit': ['Nodes', self.node, 'command_line_' + sc_name + '.txt']
        # }

    def set_node_site_and_para_for_dcgk(self, node):
        self.node = node
        self.mo_dict = {}
        self.site = self.usid.sites[self.node]
        self.me = self.site.me
        # self.df_enb_cell = self.usid.df_enb_cell.copy().loc[(self.usid.df_enb_cell.postsite == self.node)]
        # self.df_gnb_cell = self.usid.df_gnb_cell.copy().loc[(self.usid.df_gnb_cell.postsite == self.node)]
        # End

        # File Name and Path
        self.s_dict = {'cli': [], 'cmedit': []}
        sc_name = '_'.join([self.node, self.usid.circle, *self.__class__.__name__.split('_')[1:], '.txt'])
        self.relative_path = {
            'cli': ['Nodes', self.node, 'import_' + sc_name],
            'cmedit': ['Nodes', self.node, 'command_' + sc_name]
        }


    def create_rpc_msg(self):
        pass

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

    # [None, 'None', '', '""', 'XX', 'nan', np.nan, [], {}]

    def netconf_value_update(self, val):
        """ :rtype: str """
        if self.null_flag(val=val):
            return ''
        else:
            val = str(val).strip('"')
        if ',' in val and '=' in val:
            if 'ManagedElement=' in val:
                val = re.match('.*ManagedElement=[^,]*,(.*)', val).group(1)
            val = F'ManagedElement={self.node},{val}'
        elif re.match('.*\s\((.*)\)$', val):
            val = re.match('.*\s\((.*)\)$', val).group(1)
        return val

    def netconf_para_element(self, para, val):
        """ :rtype: object """
        val = self.netconf_value_update(val)
        if para in [None, 'None', 'null', 'empty', '', '""', [], {}] or val in [None, 'None', 'null', 'empty', '', '""', [], {}]: return None
        doc = Document()
        ele = doc.createElement(para)
        if val == 'XMLemptyELEMENT': return ele
        ele.appendChild(doc.createTextNode(val))
        return ele

    def netconf_mo_form_dict(self, adddict, moname='ManagedElement'):
        """ :rtype: Document """
        doc = Document()
        xml_mo = doc.createElement(moname)
        mo_attribute = self.mo_attr.get(moname)
        moname_id = self.get_moc_id(moname)
        del_flag = False
        if mo_attribute: xml_mo.setAttribute('xmlns', F'urn:com:ericsson:ecim:{mo_attribute}')
        if 'attributes' in adddict.keys():
            for attr in adddict['attributes'].keys():
                if adddict['attributes'][attr] in ['create', 'update']: continue
                xml_mo.setAttribute(attr, str(adddict['attributes'][attr]))
                if adddict['attributes'][attr] == 'delete':
                    del_flag = True
                    moname_id = self.get_moc_id(moname)
        for para in adddict.keys():
            if adddict[para] in [None, 'None', 'null', 'empty', '""', [], {}] or para == 'attributes':
                continue
            elif del_flag is True and moname_id != para:
                continue
            elif type(adddict[para]) == dict:
                xml_mo.appendChild(self.netconf_mo_form_dict(adddict[para], para))
            elif type(adddict[para]) == list:
                for val in adddict[para]:
                    if type(val) == dict:
                        xml_mo.appendChild(self.netconf_mo_form_dict(val, para))
                    else:
                        element = self.netconf_para_element(para, val)
                        if element is not None: xml_mo.appendChild(element)
            elif type(adddict[para]) in [int, str]:
                element = self.netconf_para_element(para, adddict[para])
                if element is not None: xml_mo.appendChild(element)
        return xml_mo

    def netconf_doc_form_dict(self, mo=None, mo_fdn='1', moc='ManagedElement'):
        """ :rtype: list """
        if mo in [None, 'None', '', [], {}]: return []
        doc = Document()
        doc.appendChild(self.netconf_mo_form_dict(
            {'attributes': {'message-id': str(mo_fdn), 'xmlns': 'urn:ietf:params:xml:ns:netconf:base:1.0'},
             'edit-config': {'target': {'running': 'XMLemptyELEMENT'},
                             'config': {'attributes': {'xmlns:xc': 'urn:ietf:params:xml:ns:netconf:base:1.0'}}}
             }, 'rpc'))
        doc.getElementsByTagName('config')[0].appendChild(self.netconf_mo_form_dict(mo, moc))
        # for para in ['loopback', 'cleartext']:
        #     for _ in doc.getElementsByTagName(para): _.firstChild.nodeValue = ''
        return [doc]

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

    def cmedit_cli_mo_form_dict(self, script_type='cmedit', mo_fdn='', adddict=None):
        """ :rtype: list """
        script = []
        if 'attributes' not in adddict.keys():
            return [F'#### Error on Dict Creation {mo_fdn}', '']
        s_type = adddict.get('attributes').get('xc:operation')
        mo_id = self.get_moc_id(self.get_end_moc(mo_fdn))
        mo_id_val = adddict[mo_id]
        del adddict['attributes']
        del adddict[mo_id]
        tmp_list1 = []
        for key in adddict:
            if adddict[key] in [None, 'None', '', [], {}]:
                tmp_list1 += [key]
        for key in tmp_list1: del adddict[key]
        if s_type == 'update' and len(adddict) == 0:
            pass
        elif script_type == 'cmedit':
            script_str = ''
            if s_type == 'create':
                script_str = F'cmedit create {mo_fdn} {mo_id}:{mo_id_val}'
                for key in adddict:
                    if str(key).lower() == str(mo_id).lower() or adddict[key] in [None, 'None', '', [], {}]:
                        continue
                    script_str += F'; {key}:{self.cmedit_cli_norm_value(adddict.get(key))}'
            elif s_type == 'update':
                script_str = F'cmedit set {mo_fdn} '
                for key in adddict:
                    if str(key).lower() == str(mo_id).lower() or adddict[key] in [None, 'None', '', [], {}]:
                        continue
                    script_str += F'{key}:{self.cmedit_cli_norm_value(adddict.get(key))}; '
                if script_str[-2:] == '; ':
                    script_str = script_str[:-2] + ' --force'
            elif s_type == 'delete':
                script_str = F'cmedit delete {mo_fdn} -ALL --force'
            script += [script_str]
        elif script_type == 'cli':
            if s_type == 'create':
                script += [F'create', F'FDN : {mo_fdn}', F'{mo_id} : {mo_id_val}']
                for key in adddict:
                    if str(key).lower() == str(mo_id).lower() or adddict[key] in [None, 'None', '', [], {}]:
                        continue
                    script += [F'{key} : {self.cmedit_cli_norm_value(adddict.get(key))}']
            elif s_type == 'update':
                script += [F'set', F'FDN : {mo_fdn}']
                for key in adddict:
                    if str(key).lower() == str(mo_id).lower() or adddict[key] in [None, 'None', '', [], {}]:
                        continue
                    script += [F'{key} : {self.cmedit_cli_norm_value(adddict.get(key))}']
            elif s_type == 'delete':
                script += ['delete', F'FDN : {mo_fdn}']
            script += ['']
        return script

    def cmedit_list_form_dict(self, script_type='cmedit', mo_fdn=None, mo=None):
        """ :rtype: list """
        if mo is [None, 'None', '', {}, []] or mo_fdn in [None, 'None', '', {}, []]: return []
        if mo.get('managedElementId') is not None: mo_fdn = F'{self.me}'
        script = []
        if len(mo_fdn) > 0 and mo_fdn.split(',')[-1].split('=')[0] not in self.usid.dump_list:
            self.usid.dump_list.append(mo_fdn.split(',')[-1].split('=')[0])
        if mo.get('attributes') is not None:
            if self.site.fdn_exists(fdn=mo_fdn) and mo['attributes']['xc:operation'] == 'create':
                mo['attributes']['xc:operation'] = 'update'
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

    def get_end_moc(self, mo: str) -> str:
        return mo.split(',')[-1].split('=')[0]

    def get_moc_id(self, moc: str) -> str:
        return moc[0].lower() + moc[1:] + 'Id'

    def lower_first_char(self, para: str) -> str:
        return para[0].lower() + para[1:]

    def get_db_attributes(self, moc: str) -> dict:
        qs = self.MoDetail.objects.filter((Q(mo__software=self.usid.client.software) & Q(mo__moc=moc) & Q(mo__motype=self.motype) & Q(flag=True))
                                          & (Q(bbversion='') | Q(bbversion__contains=self.bbversion))).order_by('parameter').distinct().values('parameter', 'value')
        return {_.get('parameter'): json.loads(_.get('value')) for _ in qs}

    def get_mo_related_attributes(self, mo) -> dict:
        qs = getattr(mo, 'modetail_set').filter((Q(flag=True)) & (Q(bbversion='') | Q(bbversion__contains=self.bbversion))).order_by('parameter').distinct().values('parameter', 'value')
        ret_dict = {self.lower_first_char(_.get('parameter')): json.loads(_.get('value')) for _ in qs}
        ret_dict |= {self.get_moc_id(mo.moc): mo.moid}
        return ret_dict

    def get_db_dict_with_cr_for_mo_moid(self, *, moc: str, moid: str = '') -> dict:
        mos = self.MoName.objects.filter(moc=moc, software=self.usid.client.software, motype=self.motype)
        for mo in mos:
            if mo.moid == moid:
                break
        ret_dict = self.get_mo_related_attributes(mo) if 'mo' in locals() else {}
        ret_dict |= {'attributes': {'xc:operation': 'create'}, self.get_moc_id(moc): moid}
        return ret_dict

    def get_mo_attributes(self, *, moc: str, moid: str = '') -> dict:
        mos = self.MoName.objects.filter(moc=moc, software=self.usid.client.software, motype=self.motype)
        for mo in mos:
            if mo.moid == moid:
                break
        ret_dict = self.get_mo_related_attributes(mo) if 'mo' in locals() else {}
        ret_dict |= {self.get_moc_id(moc): moid}
        return ret_dict

    def update_db_attr_with_mo_data(self, moc, site, mo) -> dict:
        ret_dict = self.get_mo_attributes(moc=moc)
        mo_data = site.site_extract_data(mo=mo) if site and mo in site.mo_list else {}
        ret_dict |= {_: mo_data.get(_, ret_dict[_]) for _ in ret_dict}
        return ret_dict

    def get_mo_dict_for_moc_node_fdn(self, moc, node=None, mo=None) -> dict:
        """ :rtype: dict """
        ret_dict = self.get_mo_attributes(moc=moc)
        if F'site_{node}' in self.usid.sites and mo in self.usid.sites.get(F'site_{node}').mo_list:
            mo_data = self.usid.sites.get(F'site_{node}').site_extract_data(mo=mo)
            ret_dict |= {_: mo_data.get(_, ret_dict[_]) for _ in ret_dict}
        return ret_dict

    def log_append_child_tags(self, moc, rel_tag, parent_mo='', node=None):
        ret_mos = {moc: []}
        if parent_mo in [None, 'None', '', 'XX', 'nan', np.nan, '""', [], {}]:
            ret_mos[moc].extend(self.db_append_child_list(moc, rel_tag))
        else:
            site = self.usid.sites.get(F'site_{node}', None)
            mos = site.find_mo_ending_with_parent_str(moc=moc, parent=parent_mo) if site else []
            if len(mos) > 0:
                for mo in mos:
                    mo_attrs_db = {self.get_moc_id(moc): '1'}
                    mo_attrs_db |= self.get_db_attributes(self.get_end_moc(mo))
                    mo_attrs_site = site.get_mo_attr_str(mo)
                    for para in mo_attrs_db:
                        mo_attrs_db[para] = mo_attrs_site.get(para, mo_attrs_db[para])
                    # Add to support cli and cmedit for Para Scripts
                    mo_attrs_db['attributes'] = {'xc:operation': 'update' if moc in self.systemCreated_list else 'create'}
                    for child in self.MoRelation.objects.filter(parent=moc, tag=rel_tag, software=self.usid.client.software):
                        mo_attrs_db |= self.log_append_child_tags(child.child, rel_tag, mo, node)
                    ret_mos[moc].append(mo_attrs_db.copy())
            else:
                ret_mos[moc].extend(self.db_append_child_list(moc, rel_tag))
        return ret_mos

    def append_child_tags_dict(self, mo, rel_tag):
        """ :rtype: dict """
        parent_mo_dict = self.get_mo_related_attributes(mo)
        parent_mo_dict['attributes'] = {'xc:operation': 'update' if mo.moc in self.systemCreated_list else 'create'}
        for child_mos in self.MoRelation.objects.filter(parent=mo.moc, tag=rel_tag, software=self.usid.client.software):
            parent_mo_dict[child_mos.child] = []
            for child in self.MoName.objects.filter(moc=child_mos.child, software=self.usid.client.software, motype=self.motype):
                if child.moid in [None, 'None', '', 'XX', 'nan', np.nan, '""', [], {}]:
                    continue
                if child.modetail_set.filter((Q(flag=True)) & (Q(bbversion='') | Q(bbversion__contains=self.bbversion))).exists():
                    parent_mo_dict[child.moc].append(self.append_child_tags_dict(child, rel_tag))
        return parent_mo_dict

    def db_append_child_list(self, moc, rel_tag):
        """ :rtype: list """
        ret_mos = []
        mos = self.MoName.objects.filter(moc=moc, software=self.usid.client.software, motype=self.motype)
        if mos.exists():
            for mo in mos:
                if mo.moid in [None, 'None', '', 'XX', 'nan', np.nan, '""', [], {}]:
                    continue
                else:
                    ret_mos.append(self.append_child_tags_dict(mo, rel_tag=rel_tag).copy())
        return ret_mos

    def get_mo_dict_for_id_tag(self, moc, moid, prev_site=None, parent=''):
        """ :rtype: dict """
        if prev_site not in [None, 'None', '', [], {}]:
            site = self.usid.sites.get(F'site_{prev_site}')
            mo = site.find_mo_ending_with_parent_str_with_id(parent=parent, moc=moc, moid=moid)
            if len(mo) > 0:
                tmp_dict = self.update_db_attr_with_mo_data(moc, site, mo[0])
            else:
                tmp_dict = self.get_mo_attributes(moc=moc, moid=moid)
        else:
            tmp_dict = self.get_mo_attributes(moc=moc, moid=moid)
        tmp_dict |= {self.get_moc_id(moc): moid}
        return tmp_dict

    def mo_para_db_dict(self, mo, site):
        """ :rtype: dict """
        mo_attrs_db = {self.get_moc_id(self.get_end_moc(mo)): '1'}
        mo_attrs_db.update(self.get_db_attributes(self.get_end_moc(mo)))
        mo_attrs_site = site.get_mo_attr_str(mo)
        for para in mo_attrs_db: mo_attrs_db[para] = mo_attrs_site.get(para, mo_attrs_db[para])
        return mo_attrs_db

    def netconf_hello_msg(self):
        """ :rtype: list """
        doc = Document()
        doc.appendChild(self.netconf_mo_form_dict(
            {'attributes': {'xmlns': 'urn:ietf:params:xml:ns:netconf:base:1.0'},
             'capabilities': {'capability': ['urn:ietf:params:netconf:base:1.0',
                                             'urn:com:ericsson:ebase:0.1.0', 'urn:com:ericsson:ebase:1.1.0']}}, 'hello')
        )
        lines = [doc.toprettyxml(encoding='UTF-8', indent='  ').decode('utf-8').strip()] + [']]>]]>']
        return lines

    def netconf_close_msg(self):
        """ :rtype: list """
        doc = Document()
        doc.appendChild(self.netconf_mo_form_dict({'attributes': {
            'message-id': 'Closing', 'xmlns': 'urn:ietf:params:xml:ns:netconf:base:1.0'}, 'close-session': 'XMLemptyELEMENT'}, 'rpc'))
        # for _ in doc.getElementsByTagName('close-session'): _.firstChild.nodeValue = ''
        lines = [doc.toprettyxml(encoding='UTF-8', indent='  ').decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', '').strip()] + \
                [']]>]]>', '']
        return lines

    def validate_mo_exist_on_site_with_no_eq_change(self, *, fdn: str) -> bool:
        return True if self.dcg_flag and fdn in self.site.mo_list else False

    def get_mo_dict_from_moc_node_fdn_moid(self, moc: str, node: str = None, mo_fdn: str = None, moid: str = None) -> dict:
        tmp_dict = self.get_mo_dict_for_moc_node_fdn(moc, node, mo_fdn)
        if not self.null_flag(val=moid):
            tmp_dict |= {self.get_moc_id(moc): moid}
        elif self.get_moc_id(moc) not in tmp_dict.keys():
            tmp_dict |= {self.get_moc_id(moc): '1'}
        if not self.validate_mo_exist_on_site_with_no_eq_change(fdn=mo_fdn):
            tmp_dict['attributes'] = {'xc:operation': 'create'}
        return tmp_dict
