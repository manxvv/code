import copy
import numpy as np
from Audit import Audit
import re


class aa_02_LTE_Parameter(Audit):
    def create_rpc_msg(self):
        self.tech = 'LTE'
        if self.node not in self.audit_usid.lte_node: return
        df_tmp = self.audit_usid.db['MOC'].copy(deep=True)
        df_tmp = df_tmp.loc[(df_tmp.tech == self.tech)]

        skip_moc_list = ['UePolicyOptimization', 'EUtranCellFDD', 'EUtranCellTDD',
                         'UeMeasControl', 'ReportConfigB1NR', 'GUtranFreqRelation']
        for r in df_tmp.loc[((~df_tmp.mo.isin(skip_moc_list)) & (df_tmp.mo.str.contains('=')))].itertuples():
            self.add_mo_para_to_para_list(
                ldn=r.__getattribute__('mo'),
                para=r.__getattribute__('parameter'),
                gpl=r.__getattribute__('value'),
                para_type=r.__getattribute__('para_type')
            )
        # For all Other MOs
        for r in df_tmp.loc[(~(df_tmp.mo.str.contains('=')))].itertuples():
            for ldn in sorted([_ for _ in self.site.fdns if
                               re.match(F".*ENodeBFunction=1.*,{r.__getattribute__('mo')}=([^,]*)$", _)]):
                self.add_mo_para_to_para_list(
                    ldn=ldn,
                    para=r.__getattribute__('parameter'),
                    gpl=r.__getattribute__('value'),
                    para_type=r.__getattribute__('para_type')
                )
