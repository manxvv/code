import re

import pandas as pd

from AuditUSID import AuditUSID


class Audit:
    def __init__(self, *, audit_usid: AuditUSID, node: str):
        self.node = node
        self.audit_usid = audit_usid
        self.custom_log = self.audit_usid.custom_log
        self.site = self.audit_usid.sites[self.node]
        self.me = self.site.me
        self.set_node_site_and_para_for_dcgk(node)
        self.tech = 'NR'
        self.gpl_list = []

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
            self.gpl_list.append({
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
            self.audit_usid.gpl_completed_mo_para.append(F'{ldn}.{para}')

        value, flag = None, False
        if F'{ldn}.{para}' in self.audit_usid.gpl_completed_mo_para: return
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

    def set_node_site_and_para_for_dcgk(self, node):
        self.node = node
        self.site = self.audit_usid.sites[self.node]
        self.me = self.site.me

    def create_rpc_msg(self): pass

    def run(self):
        self.create_rpc_msg()
        self.audit_usid.df_gpl = pd.concat([self.audit_usid.df_gpl, pd.DataFrame(self.gpl_list)],
                                           axis=1, ignore_index=True)

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
