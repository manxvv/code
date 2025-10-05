import os
from datetime import datetime
import pandas as pd
from AuditUSID import AuditUSID


def highlight_even_row(*, row) -> list:
    return ['background-color: #D2D3D3; border: 1px solid black;' if _ % 2 == 1 else
            'border: 1px solid black;' for _ in range(len(row))]


def audit_report_color_rows(*, row) -> list:
    if row['Deviation'] in ['True', 'TRUE', True, 'NO', 'NA', 'N/A']:
        return ['' for _ in row]
    else:
        return ['background-color: red; color: white;' for _ in row]


def audit_report_complete_site(*, df: pd.DataFrame, node: str, base_dir) -> None:
    col_list = ['Date'] + df.columns.tolist()
    df['Date'] = datetime.now().strftime('%m-%d-%Y')
    df = df[col_list]
    fine_name = os.path.join(base_dir, 'Node_Reports', F'{node}.xlsx')
    os.makedirs(os.path.dirname(fine_name), exist_ok=True)
    audit_file = pd.ExcelWriter(fine_name, engine='openpyxl')
    if len(df.index) > 0:
        df_style = df.style.apply(lambda x: highlight_even_row(row=x))
        df_style = df_style.apply(lambda x: audit_report_color_rows(row=x), axis=1)
        df_style.to_excel(excel_writer=audit_file, sheet_name=node, index=False)
        audit_file.sheets[node].auto_filter.ref = audit_file.sheets[node].calculate_dimension()
        audit_file.sheets[node].auto_filter.enable = True
    audit_file.close()


class AuditReport:
    def __init__(self, *, a_usid: AuditUSID):
        self.a_usid = a_usid
        self.audit_report()

    def audit_report(self,):
        current_time = datetime.now().strftime('%m%d%Y_%H%M%S')
        self.audit_file = pd.ExcelWriter(os.path.join(
            self.a_usid.base_dir, F'AuditReport_{self.a_usid.circle}_{current_time}.xlsx'), engine='openpyxl')
        df_temp = self.a_usid.df_gpl.copy(deep=True)
        col_list = ['Date'] + df_temp.columns.tolist()
        df_temp['Date'] = datetime.now().strftime('%m-%d-%Y')
        df_temp = df_temp[col_list]
        if len(df_temp.index) > 0:
            df_style = df_temp.style.apply(lambda x: highlight_even_row(row=x))
            df_style = df_style.apply(lambda x: audit_report_color_rows(row=x), axis=1)
            df_style.to_excel(excel_writer=self.audit_file, sheet_name='Audit', index=False)
            self.audit_file.sheets['Audit'].auto_filter.ref = self.audit_file.sheets['Audit'].calculate_dimension()
            self.audit_file.sheets['Audit'].auto_filter.enable = True
        # Feature
        df_temp = self.a_usid.df_feature.copy(deep=True)
        if len(df_temp.index) > 0:
            df_style = df_temp.style.apply(lambda x: highlight_even_row(row=x))
            df_style.to_excel(excel_writer=self.audit_file, sheet_name='Feature', index=False)
            self.audit_file.sheets['Feature'].auto_filter.ref = self.audit_file.sheets['Feature'].calculate_dimension()
            self.audit_file.sheets['Feature'].auto_filter.enable = True
        # AMF
        df_temp = self.a_usid.df_amf.copy(deep=True)
        if len(df_temp.index) > 0:
            df_style = df_temp.style.apply(lambda x: highlight_even_row(row=x))
            df_style.to_excel(excel_writer=self.audit_file, sheet_name='AMF', index=False)
            self.audit_file.sheets['AMF'].auto_filter.ref = self.audit_file.sheets['AMF'].calculate_dimension()
            self.audit_file.sheets['AMF'].auto_filter.enable = True
        self.audit_file.close()
