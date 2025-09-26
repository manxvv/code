import os
from datetime import datetime
import pandas as pd
from . AuditUSID import AuditUSID


def highlight_even_row(*, row) -> list:
    return ['background-color: #D2D3D3; ' if _ % 2 == 1 else 'background-color: #FFFFFF' for _ in range(len(row))]
    #     border: 1px solid


def audit_report_color_rows(*, row) -> list:
    if row['Deviation'] in ['True', 'TRUE', True, 'NO']:
        return ['' for _ in row]
    else:
        return ['background-color: red; color: white; border: 2px solid green' for _ in row]
        # if row['GSValue'].startswith('GS_Error'):
        #     return ['background-color: red; color: white; border: 2px solid green' for _ in row]
        # elif row['Permission'].lower().startswith('global'):
        #     return ['background-color: coral' for _ in row]
        # elif row['Permission'].lower().startswith('local'):
        #     return ['background-color: cyan' for _ in row]
        # elif row['Permission'].lower().startswith('not auditable'):
        #     return ['background-color: gray' for _ in row]
        # else:
        #     return ['background-color: crimson' for _ in row]


class GSAuditReport:
    def __init__(self, *, audit_usid: AuditUSID):
        self.audit_usid = audit_usid
        current_time = datetime.now().strftime('%m%d%Y_%H%M%S')
        self.audit_file = pd.ExcelWriter(os.path.join(
            self.audit_usid.base_dir, F'AuditReport_{self.audit_usid.circle}_{current_time}.xlsx'), engine='openpyxl')

        # Report
        # df_temp = self.audit_usid.df_gpl.copy(deep=True)
        # if len(df_temp.index) > 0:
        #     self.audit_file = pd.ExcelWriter(os.path.join(
        #         self.audit_usid.base_dir, F'AuditReport_{self.audit_usid.circle}_{current_time}.xlsx'), engine='openpyxl')
        #     df_style = df_temp.style.apply(lambda x: highlight_even_row(row=x))
        #     df_style = df_style.apply(lambda x: audit_report_color_rows(row=x), axis=1)
        #     df_style.to_excel(excel_writer=self.audit_file, sheet_name='Audit', index=False)
        #     self.audit_file.sheets['Audit'].auto_filter.ref = self.audit_file.sheets['Audit'].calculate_dimension()
        #     self.audit_file.sheets['Audit'].auto_filter.enable = True
        # AuditReport
        df_temp = self.audit_usid.df_gpl.copy(deep=True)
        if len(df_temp.index) > 0:
            df_style = df_temp.style.apply(lambda x: highlight_even_row(row=x))
            df_style = df_style.apply(lambda x: audit_report_color_rows(row=x), axis=1)
            df_style.to_excel(excel_writer=self.audit_file, sheet_name='Audit', index=False)
            self.audit_file.sheets['Audit'].auto_filter.ref = self.audit_file.sheets['Audit'].calculate_dimension()
            self.audit_file.sheets['Audit'].auto_filter.enable = True
        # Feature
        df_temp = self.audit_usid.df_feature.copy(deep=True)
        if len(df_temp.index) > 0:
            df_style = df_temp.style.apply(lambda x: highlight_even_row(row=x))
            # df_style = df_style.apply(lambda x: audit_report_color_rows(row=x), axis=1)
            df_style.to_excel(excel_writer=self.audit_file, sheet_name='Feature', index=False)
            self.audit_file.sheets['Feature'].auto_filter.ref = self.audit_file.sheets['Feature'].calculate_dimension()
            self.audit_file.sheets['Feature'].auto_filter.enable = True
        # AMF
        df_temp = self.audit_usid.df_amf.copy(deep=True)
        if len(df_temp.index) > 0:
            df_style = df_temp.style.apply(lambda x: highlight_even_row(row=x))
            # df_style = df_style.apply(lambda x: audit_report_color_rows(row=x), axis=1)
            df_style.to_excel(excel_writer=self.audit_file, sheet_name='AMF', index=False)
            self.audit_file.sheets['AMF'].auto_filter.ref = self.audit_file.sheets['AMF'].calculate_dimension()
            self.audit_file.sheets['AMF'].auto_filter.enable = True
        self.audit_file.close()
