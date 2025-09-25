from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting import Rule
from openpyxl.styles import PatternFill, Font
from openpyxl.worksheet.table import Table, TableStyleInfo
import os
import re
import pandas as pd


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

def save_logic_dataframe(self, *, current_time: str):
    data = {'Site': self.df_site, 'Cell': self.df_cell, 'AMF': self.df_amf, 'Feature': self.df_feature}
    with ExcelWriter(os.path.join(self.base_dir, F'Logic_{current_time}.xlsx')) as writer:
        self.df_site.reset_index().to_excel(writer, sheet_name='Site', index=True)
        self.df_cell.reset_index().to_excel(writer, sheet_name='Cell', index=True)

def save_audit_dataframe(self, *, current_time: str) -> None:
    df = self.df_gpl.copy()
    with ExcelWriter(os.path.join(self.base_dir, F'AuditReport_{self.circle}_{current_time}.xlsx')) as writer:
        df.reset_index().to_excel(writer, sheet_name='AuditReport', index=True)
        self.df_feature.reset_index().to_excel(writer, sheet_name='Feature', index=True)
        self.df_amf.reset_index().to_excel(writer, sheet_name='AMF', index=True)

class GSAuditReport:
    def __init__(self, *, audit_usid, current_time):
        self.audit_usid = audit_usid
        self.audit_file = pd.ExcelWriter(os.path.join(
            self.audit_usid.base_dir, F'AuditReport_{self.audit_usid.circle}_{current_time}.xlsx'), engine='openpyxl')
        # AuditReport
        df_temp = self.audit_usid.df_gpl.copy(deep=True)
        if len(df_temp.index) > 0:
            self.audit_file = pd.ExcelWriter(os.path.join(
                self.audit_usid.base_dir, F'AuditReport_{self.audit_usid.circle}_{current_time}.xlsx'), engine='openpyxl')
            df_style = df_temp.style.apply(lambda x: highlight_even_row(row=x))
            df_style = df_style.apply(lambda x: audit_report_color_rows(row=x), axis=1)
            df_style.to_excel(excel_writer=self.audit_file, sheet_name='AuditReport', index=False)
            self.audit_file.sheets['AuditReport'].auto_filter.ref = self.audit_file.sheets['AuditReport'].calculate_dimension()
            self.audit_file.sheets['AuditReport'].auto_filter.enable = True
        # Feature
        df_temp = self.audit_usid.df_feature.copy(deep=True)
        if len(df_temp.index) > 0:
            df_style = df_temp.style.apply(lambda x: highlight_even_row(row=x))
            df_style = df_style.apply(lambda x: audit_report_color_rows(row=x), axis=1)
            df_style.to_excel(excel_writer=self.audit_file, sheet_name='Feature', index=False)
            self.audit_file.sheets['Feature'].auto_filter.ref = self.audit_file.sheets['Feature'].calculate_dimension()
            self.audit_file.sheets['Feature'].auto_filter.enable = True
        # AMF
        df_temp = self.audit_usid.df_amf.copy(deep=True)
        if len(df_temp.index) > 0:
            df_style = df_temp.style.apply(lambda x: highlight_even_row(row=x))
            df_style = df_style.apply(lambda x: audit_report_color_rows(row=x), axis=1)
            df_style.to_excel(excel_writer=self.audit_file, sheet_name='AMF', index=False)
            self.audit_file.sheets['AMF'].auto_filter.ref = self.audit_file.sheets['AMF'].calculate_dimension()
            self.audit_file.sheets['AMF'].auto_filter.enable = True
        self.audit_file.close()

    @staticmethod
    def report_create_formating(work_sheet, sheet_name):
        """
            This method fetches the worksheet dimensions and returns the dimensions plus a dictionary that contains a
            mapping of the sheet column names to their cell coordinates
        """
        dims = work_sheet.calculate_dimension()
        matched = re.match(r"([A-Z]+)[\d]+:([A-Z]+)[\d]+", dims)
        column_ref = ":".join([str_ + '1' for str_ in matched.groups()])
        col_coords = dict([(cell_.value, cell_.coordinate) for cell_ in work_sheet[column_ref][0]])

        # Add Red Colour for error flag
        dxf_error = DifferentialStyle(fill=PatternFill("solid", bgColor="FF0000"), font=Font(b=False, color="FFFFFF"))
        r_error = Rule(type="expression", dxf=dxf_error, stopIfTrue=True)
        r_error.formula = [F"${col_coords['GSValue']}=\"error\""]
        work_sheet.conditional_formatting.add(dims, r_error)

        # If 'flag' is False & Permission is Global or GlobalOptional, then it should be filled Red
        dxf_global = DifferentialStyle(fill=PatternFill("solid", bgColor="F47174"))
        r_global = Rule(type="expression", dxf=dxf_global, stopIfTrue=True)
        r_global.formula = [F"AND(OR(${col_coords['Permission']}=\"Global\", ${col_coords['Permission']}=\"GlobalOptional\", $"
                            F"{col_coords['Permission']}=\"GlobalOptional \"),${col_coords['flag']}=FALSE)"]
        work_sheet.conditional_formatting.add(dims, r_global)

        # If 'Flag' is False & Permission is Not Auditable, then it should be filled Grey
        dxf_not_auditable = DifferentialStyle(fill=PatternFill("solid", bgColor="B7825F"))
        r_not_auditable = Rule(type="expression", dxf=dxf_not_auditable, stopIfTrue=True)
        r_not_auditable.formula = [F"AND(${col_coords['Permission']}=\"Not Auditable\",${col_coords['flag']}=FALSE)"]
        work_sheet.conditional_formatting.add(dims, r_not_auditable)

        # If 'Flag' is False or True & Permission is Local, then it should be filled Light Blue
        dxf_local = DifferentialStyle(fill=PatternFill("solid", bgColor="93CAED"))
        r_local = Rule(type="expression", dxf=dxf_local, stopIfTrue=True)
        r_local.formula = [F"AND(${col_coords['Permission']}=\"Local\",${col_coords['flag']}=FALSE)"]
        work_sheet.conditional_formatting.add(dims, r_local)

        # If 'Flag' is False or True & Permission is Internal, then it should be filled Orange
        dxf_internal = DifferentialStyle(fill=PatternFill("solid", bgColor="F5CA7B"))
        r_internal = Rule(type="expression", dxf=dxf_internal, stopIfTrue=True)
        r_internal.formula = [F"AND(${col_coords['Permission']}=\"Internal\",${col_coords['flag']}=FALSE)"]
        work_sheet.conditional_formatting.add(dims, r_internal)

        """
        This method adds a table to the excel sheet. There should be no null column names to prevent when the table is created.
        This is to prevent the excel sheet from getting corrupted.
        """
        tab = Table(displayName=sheet_name + "_Table", name=sheet_name + "_Table", ref=dims)
        # TableStyleLight15
        style = TableStyleInfo(name="TableStyleMedium4", showFirstColumn=True, showLastColumn=True, showRowStripes=True, showColumnStripes=False)
        tab.tableStyleInfo = style
        work_sheet.add_table(tab)

    @staticmethod
    def excell_table_formating(work_sheet, sheet_name):
        tab = Table(displayName=sheet_name + "_Table", name=sheet_name + "_Table", ref=work_sheet.calculate_dimension())
        style = TableStyleInfo(name="TableStyleMedium4", showFirstColumn=True, showLastColumn=True, showRowStripes=True, showColumnStripes=False)
        tab.tableStyleInfo = style
        work_sheet.add_table(tab)