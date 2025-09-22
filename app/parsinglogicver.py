import pandas as pd
import os
import re
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import json

from openpyxl.styles import Alignment
import pandas as pd
from io import StringIO
import os
import re
from datetime import datetime
import numpy as np
class Calculator:
    
    def __init__(self):
        pass
        
        
    def alarm(self,raw_data):
        alarms = raw_data.strip().split("\n\n")

        records = []
        for alarm in alarms:
            record = {}
            for line in alarm.split("\n"):
                if " : " in line:
                    key, value = line.split(" : ", 1)
                    record[key.strip()] = value.strip()
            records.append(record)
            
        df_alarms = pd.DataFrame(records)
        
        return df_alarms
    
    
    def sync(self,raw_data):
        
        
        sync_raw_data = raw_data[raw_data.find("NodeId"):]
            
        df_sync = pd.read_csv(StringIO(sync_raw_data), sep="\t")
        
        
        return df_sync
    
    
    def file_name_maker(self,fileeee):
        
        flist = ["EUtranCellFDDId","EUtranCellTDDId","FieldReplaceableUnitId","NRCellDUId","NRSectorCarrierId","SectorCarrierId","SectorEquipmentFunctionId","syncStatus","Total number of alarms fetched for the given query"]
        
        
        for onefilename in flist:
            if(onefilename in fileeee):
                return onefilename.replace("Id","")
        
    
    def highlight_active(val):
        color = "lightgreen" if "ENABLED" in str(val) else "white"
        return f"background-color: {color}"

    def count_states(self, df, celltype,status):
        
        subset = df[df["CellType"] == celltype]
        # print("subset",subset,"subsetsubsetsubset")
        enabled = (subset["operationalState"] == "ENABLED").sum()
        disabled = (subset["operationalState"] == "DISABLED").sum()
        
        if(enabled+disabled == 0):
            return "NA"
        else:
            if(status):
                return f"{enabled}"
            else:
                return f"{enabled+disabled}"
    
    
    
    def amf_count_states(self, celltype, df, status):
        if(len(df) > 0):
                
            subset = df[df["NodeId"] == celltype]
                
            enabled = (subset["operationalState"] == "ENABLED").sum()
            disabled = (subset["operationalState"] == "DISABLED").sum()
            
            if(enabled+disabled == 0):
                return "NA"
            else:
                if(status):
                    return f"{enabled}"
                else:
                    return f"{enabled+disabled}"
        else:
            return "NA"
    
    def count_alarms(self, df, celltype):
        
        if("presentSeverity" in df.columns):
                
            enabled = (df["presentSeverity"] == celltype).sum()
            return f"{enabled}"

        else:
            return "0"
    


    def startCalc(self,file_list,calc,get_db_connection,username):
                
        path = os.getcwd()
        list_of_sheet = []
        list_of_sheet_same_col = []
        list_of_sheet_name = []
        
        alarms_data = pd.DataFrame([])
        syncStatus_data = pd.DataFrame([])
        
        
        for i in file_list:
            
            name_only = os.path.splitext(os.path.basename(i))[0]
            
            fname = ""
            df_list = []
            with open(os.path.join(path,i)) as file:
                
                file_data = file.read()
                fname = self.file_name_maker(file_data)
                
                
                if("Total number of alarms fetched for the given query" in file_data):
                    
                    alarms_data = self.alarm(file_data)
                    
                    
                if("syncStatus" in file_data):
                    
                    syncStatus_data = self.sync(file_data)
                    
                else:
                    
                    start_point = "NodeId"
                    stop_point = "instance"
                    read_enabled = False
                    
                    raw_text = ""
                    
                    raw_text_list = []
                    for j, line in enumerate(file_data.splitlines(), start=1):
                        start_matches = re.findall(start_point, line)
                        stop_matches = re.findall(stop_point, line)
                        
                        
                        if start_matches:
                            read_enabled = True
                        
                        if stop_matches:
                            read_enabled = False
                            raw_text_list.append(raw_text)
                            raw_text = ""
                            
                        if(read_enabled):
                            raw_text = raw_text+"\n"+line
                            
                        
                
                
                    for raw_one_text in raw_text_list:
                        
                        df = pd.read_csv(StringIO(raw_one_text), sep="\t")
                        
                        df_list.append(df)
                    
            
            if len(df_list) > 0:
                merged_df = pd.concat(df_list, ignore_index=True)
                
                rename_map = {
                    "EutrancellFDD": {"col": "EUtranCellFDDId", "type": "FDD"},
                    "EutrancellTDD": {"col": "EUtranCellTDDId", "type": "TDD"},
                    "Nrcelldu": {"col": "NRCellDUId", "type": "NR"}
                }

                merged_df = pd.concat(df_list, ignore_index=True)
                
                merged_df.rename(columns={"NetworkElement":"NodeId","MeContext":"NodeId"})

                
                if name_only in rename_map:
                    merged_df = merged_df.rename(columns={rename_map[name_only]["col"]: "CellName"})
                    merged_df["CellType"] = rename_map[name_only]["type"]
                    
                    list_of_sheet_same_col.append(merged_df)
                    
                    

                list_of_sheet.append(merged_df)
                
                
                list_of_sheet_name.append(fname)
           
        sheet_same_col = pd.concat(list_of_sheet_same_col, ignore_index=True)
        
        
        final_sheet_cell = sheet_same_col[["NodeId",'CellName',"administrativeState","operationalState","CellType"]]
        list_of_sheet.insert(0, final_sheet_cell)
        list_of_sheet_name.insert(0, "CellStatus")
        
        
        
        FINAL_STATUS_df = final_sheet_cell
        
        summary_rows = []
        
        
        
        


        # print(",".join(summary_df["NodeId"].to_list()),"resultresultresultresult")
        # for node, node_df in FINAL_STATUS_df.groupby("NodeId"):
        #     print("Node:", node)
        #     for celltype, ct_df in node_df.groupby("CellType"):
        #         print("   CellType:", celltype)
        #         print(ct_df, "\n")
                
                
        list_of_sheet.insert(0, summary_df)
        list_of_sheet_name.insert(0, "NodeStatus")
        
        
        conn = get_db_connection()
        conn.execute("INSERT INTO file_content (username, node_id,file_list) VALUES (?, ?, ?)", (username, ",".join(summary_df["NodeId"].to_list()),", ".join(file_list)))
        conn.commit()
                
                
        file_name = calc+datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + "_cells_data.xlsx"
        with pd.ExcelWriter(os.path.join("downloads",file_name), engine="xlsxwriter") as writer:
            
            for i, df in enumerate(list_of_sheet, start=1):
                name_only = list_of_sheet_name[i-1]
                
                sheet_name = f"{name_only}"   # You can also use custom names
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                workbook  = writer.book
                worksheet = writer.sheets[sheet_name]

                enableformat1 = workbook.add_format({'bg_color': 'gray'})

                disableformat1 = workbook.add_format({'bg_color': 'red'})
                
                # col_idx = df.columns.get_loc("operationalState")
                start_row = 1 
                stop_row = len(df)
                
                
                for liei in ["operationalState","operationalState_pre","operationalState_post","administrativeState_pre","administrativeState_post","Syncstatus"]:
                        
                    if liei in df.columns:

                        col_idx = df.columns.get_loc(liei)
                        worksheet.conditional_format(start_row, col_idx, stop_row, col_idx, {
                            'type': 'text',
                            'criteria': 'containing',
                            'value': 'ENABLED',
                            'format': disableformat1
                        })
                        worksheet.conditional_format(start_row, col_idx, stop_row, col_idx, {
                            'type': 'text',
                            'criteria': 'containing',
                            'value': 'DISABLED',
                            'format': enableformat1
                        })
                
                
                        worksheet.conditional_format(start_row, col_idx, stop_row, col_idx, {
                            'type': 'text',
                            'criteria': 'containing',
                            'value': 'UNLOCKED',
                            'format': disableformat1
                        })
                        worksheet.conditional_format(start_row, col_idx, stop_row, col_idx, {
                            'type': 'text',
                            'criteria': 'containing',
                            'value': 'LOCKED',
                            'format': enableformat1
                        })
                        
                        
                        worksheet.conditional_format(start_row, col_idx, stop_row, col_idx, {
                            'type': 'text',
                            'criteria': 'containing',
                            'value': 'SYNCHRONIZED',
                            'format': enableformat1
                        })
                        
                        
                        worksheet.conditional_format(start_row, col_idx, stop_row, col_idx, {
                            'type': 'text',
                            'criteria': 'containing',
                            'value': 'NOT SYNCHRONIZED',
                            'format': disableformat1
                        })
            

        return os.path.join("downloads",file_name)
    
    
    def alarm_check(self,files):
                    
                    
        path = os.getcwd()

                
        list_of_sheet = []
        list_of_sheet_same_col = []
        list_of_sheet_name = []
        for i in files:
            
            
            name_only = os.path.splitext(os.path.basename(i))[0]
            df_list = []
            with open(os.path.join(path,i)) as file:
                file_data = file.read()
                start_point = "presentSeverity"
                stop_point = "Total number"
                read_enabled = False
                
                raw_text = ""
                
                raw_text_list = []
                for j, line in enumerate(file_data.splitlines(), start=1):
                    start_matches = re.findall(start_point, line)
                    stop_matches = re.findall(stop_point, line)
                    
                    
                    if start_matches:
                        read_enabled = True
                    
                    if stop_matches:
                        read_enabled = False
                        raw_text_list.append(raw_text)
                        raw_text = ""
                        
                    if(read_enabled):
                        raw_text = raw_text+"\n"+line
                        
                    
            
                for raw_one_text in raw_text_list:    
                
                
                    df = pd.read_csv(StringIO(raw_one_text), sep="\t")
                    
                    
                    # for i in df.iterrows():
                    #     print(i["NodeName"],"sadmnasjdnasndsajdkjasdnsajkdjkas")
                     
                    
                    # filtered_data = df[
                    #     ~df["presentSeverity"].str.contains("Cell UserLabel", na=False) &
                    #     ~df["presentSeverity"].str.contains("EUtranCell", na=False)
                    # ]
                    
                    df_list.append(df)
                    
                    
                 
            # print(df_list,"df_listdf_listdf_listdf_list")
            merged_df = pd.concat(df_list, ignore_index=True)
            
            rename_map = {
                "EutrancellFDD": {"col": "EUtranCellFDDId", "type": "FDD"},
                "EutrancellTDD": {"col": "EUtranCellTDDId", "type": "TDD"},
                "FieldReplaceableUnit": {"col": "FieldReplaceableUnitId", "type": "NR"}
            }
            
            # print(df_list,"df_listdf_listdf_listdf_list")

            merged_df = pd.concat(df_list, ignore_index=True)

            # print(name_only, "name_only")
            
            
            if name_only in rename_map:
                merged_df = merged_df.rename(columns={rename_map[name_only]["col"]: "CellName"})
                merged_df["CellType"] = rename_map[name_only]["type"]
                # print(name_only, "processed")
                
                list_of_sheet_same_col.append(merged_df)
                
            
                

            # print(merged_df.columns)

            list_of_sheet.append(merged_df)
            list_of_sheet_name.append(name_only)
            
            
            
        # print(len(list_of_sheet),"list_of_sheetlist_of_sheet")
        file_name = "alarmsss"+datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + "_cells_data.xlsx"
        with pd.ExcelWriter(os.path.join("downloads",file_name), engine="xlsxwriter") as writer:
            
            for i, df in enumerate(list_of_sheet, start=1):
                name_only = list_of_sheet_name[i-1]
                
                sheet_name = f"{name_only}"   # You can also use custom names
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                workbook  = writer.book
                worksheet = writer.sheets[sheet_name]

                enableformat1 = workbook.add_format({'bg_color': 'gray'})

                disableformat1 = workbook.add_format({'bg_color': 'red'})
                
                # print(df.columns,"df.columnsdf.columns")
                # col_idx = df.columns.get_loc("operationalState")
                # start_row = 1 
                # stop_row = len(df)
                # worksheet.conditional_format(start_row, col_idx, stop_row, col_idx, {
                #     'type': 'text',
                #     'criteria': 'containing',
                #     'value': 'ENABLED',
                #     'format': disableformat1
                # })
                # worksheet.conditional_format(start_row, col_idx, stop_row, col_idx, {
                #     'type': 'text',
                #     'criteria': 'containing',
                #     'value': 'DISABLED',
                #     'format': enableformat1
                # })
            
        

        return os.path.join("downloads",file_name)
    
    
    
    

    
    def startdiffCalc(self,pre_files,post_files):
        # print(pre_files,post_files,"pre_files,post_filespre_files,post_files")
                

        pre_df = pd.read_excel(pre_files,sheet_name="CellStatus")
        post_df = pd.read_excel(post_files,sheet_name="CellStatus")
        
        
        
        
        pre_df["merged_data"] = pre_df["NodeId"].astype(str) + "_" + pre_df["CellType"].astype(str) + "_" + pre_df["CellName"].astype(str)
        post_df["merged_data"] = post_df["NodeId"].astype(str) + "_" + post_df["CellType"].astype(str) + "_" + post_df["CellName"].astype(str)
        # pre_df["operationalStatePre"] = pre_df["operationalState"]
        # post_df["operationalStatePost"] = post_df["operationalState"]
        # pre_df["administrativeStatePre"] = pre_df["administrativeState"]
        # post_df["administrativeStatePost"] = post_df["administrativeState"]
        
        
        # print(pre_df["merged_data"].to_string())
        # print(post_df["merged_data"].to_string())
        
        
        
        # print(pre_df.keys())
        # print(post_df.keys())
        
        
        merged = pre_df.merge(post_df, on=["merged_data"], how="outer",indicator=True,suffixes=("_pre", "_post"))
        # print(merged[["operationalState_post","operationalState_post","_merge"]])
        
        # filtered_data = merged[(merged["operationalState_pre"] != merged["operationalState_post"]) | (merged["_merge"] != "both")]
        
                
        # print(filtered_data)
        
        filtered_data = merged
        filtered_data["status"] = np.where(
            filtered_data["_merge"] == "both", 
            np.where(
                filtered_data["operationalState_pre"] != filtered_data["operationalState_post"], 
                "Status Changes", 
                "No Status Changes"
            ),
            np.where(
                filtered_data["_merge"] == "left_only", 
                "Missing in post check", 
                "Missing in pre check"
            )
        )
        
        
        
        filtered_data["NodeId"] = filtered_data["NodeId_pre"].combine_first(filtered_data["NodeId_post"])
        filtered_data["CellType"] = filtered_data["CellType_pre"].combine_first(filtered_data["CellType_post"])
        filtered_data["CellName"] = filtered_data["CellName_pre"].combine_first(filtered_data["CellName_post"])

        filtered_data = filtered_data[["NodeId","CellType","CellName","operationalState_pre","administrativeState_pre","operationalState_post","administrativeState_post","status"]]
        
        

        with pd.ExcelWriter(post_files, engine="openpyxl", mode="a", if_sheet_exists="new") as writer:
            filtered_data.to_excel(writer, sheet_name="FinalStatus", index=False)
            
        
        
        all_sheets = pd.read_excel(post_files, sheet_name=None)
            
        list_of_sheet_name = list(all_sheets.keys())   # sheet names
        list_of_sheet = list(all_sheets.values())
        
        
        if "Final_Status" in list_of_sheet_name:
            idx = list_of_sheet_name.index("Final_Status")
            # pop out the sheet
            fs_name = list_of_sheet_name.pop(idx)
            fs_df = list_of_sheet.pop(idx)
            # insert at position 0
            list_of_sheet_name.insert(0, fs_name)
            list_of_sheet.insert(0, fs_df)
        
        
            
            
        
    
    def alarm_checker(self,file_parsed,file_sitess):


        # print(self.alarm_data)
        # print(self.file_parsed)
        
        
        
        sites_data = pd.read_excel(file_sitess)
        
        all_sheets = pd.read_excel(file_parsed, sheet_name=None)
        list_of_sheet_name = list(all_sheets.keys())
        print(list_of_sheet_name,"pd.read_excel(file_parsed)")
        df = pd.DataFrame([])
        amfdf = pd.DataFrame([])
        syncStatus_data = pd.DataFrame([])
        
        print(df,amfdf,syncStatus_data,list_of_sheet_name,"list_of_sheet_namelist_of_sheet_namelist_of_sheet_name")

        if("CellStatus" in list_of_sheet_name):
            df = pd.read_excel(file_parsed, sheet_name="CellStatus")
            
            
        
        if("TermPointToAmf" in list_of_sheet_name):
            amfdf = pd.read_excel(file_parsed, sheet_name="TermPointToAmf")
            
            
        if("CmFunction" in list_of_sheet_name):
            syncStatus_data = pd.read_excel(self.file_parsed, sheet_name="CmFunction")
       

        # print(amfdf,"amfdfamfdfamfdfamfdf")
        
            
        summary_rows = []
        for node, group in df.groupby("NodeId"):
            
            # print(node,group)
            
            
        
            node_alarms = pd.DataFrame([])
            
            
            if "NodeName" in self.alarm_data.columns:
                node_alarms = self.alarm_data[self.alarm_data["NodeName"] == node]
            
            
            # print(self.alarm_data[self.alarm_data["NodeName"] == node],"NodeNameNodeName")
            
            row = {
                "NodeId": node,
                "Syncstatus": "N/A",  
                "TermPointToAmfEnabled": self.amf_count_states(node , amfdf, True),
                "TermPointToAmfTotal": self.amf_count_states(node , amfdf, False),
                "FDDCellEnabled": self.count_states(group, "FDD",True),
                "FDDCellTotal": self.count_states(group, "FDD",False),
                "TDDCellEnabled": self.count_states(group, "TDD",True),
                "TDDCellTotal": self.count_states(group, "TDD",False),
                "NRCellEnabled": self.count_states(group, "NR",True),
                "NRCellTotal": self.count_states(group, "NR",False),
                # placeholders for other metrics
                "Critical": self.count_alarms(node_alarms,"CRITICAL"),
                "Major": self.count_alarms(node_alarms,"MAJOR"),
                "Total": len(node_alarms),
            }
            summary_rows.append(row)

        summary_df = pd.DataFrame(summary_rows)

        
        
        print(self.alarm_data,"sites_datasites_data",sites_data,"summary_dfsummary_df")
        
        
        if("NodeName" in self.alarm_data.columns):
            self.alarm_data = self.alarm_data[self.alarm_data["NodeName"].isin(sites_data["Node"])]
        
        
        
        if("NodeId" in syncStatus_data.columns):
            print(summary_df,"summary_dfsummary_df")
            summary_df["Syncstatus"] = summary_df["NodeId"].map(
                syncStatus_data.set_index("NodeId")["syncStatus"]
            ).fillna("NA")
        
        summary_df.fillna("NA", inplace=True)
        print(summary_df,"summary_dfsummary_dfsummary_df")
        with pd.ExcelWriter(self.file_parsed, engine="openpyxl", mode="a") as writer:
            summary_df.to_excel(writer, sheet_name="NodeStatus", index=False)
            self.alarm_data.to_excel(writer, sheet_name="AlarmStatus", index=False)

        
        
    def remove_extra_col(self,file_parsed):
        
        
        xls = pd.ExcelFile(file_parsed)
        
        sheet_dfs = {}
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            fin = df.columns.to_list()
            for colll in ["SubNetwork","ManagedElement","GNBDUFunction","ENodeBFunction","Equipment"]:
                if(colll in df.columns):
                    fin.remove(colll)
            
            df = df[fin]
                    

            sheet_dfs[sheet] = df

        # Overwrite the same file
        with pd.ExcelWriter(file_parsed, engine="xlsxwriter") as writer:
            for sheet_name, df in sheet_dfs.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        
    
    def re_arrange_node_status(self, filename):
        
        
        all_sheets = pd.read_excel(filename, sheet_name=None)
            
        list_of_sheet_name = list(all_sheets.keys())
        
        if("NodeStatus" in list_of_sheet_name):
            
            new_row = {
                'NodeId': 0,
                'Syncstatus': 0,
                'TermPointToAmfEnabled': 0,
                'TermPointToAmfTotal': 0,
                'FDDCellEnabled': 0,
                'FDDCellTotal': 0,
                'TDDCellEnabled': 0,
                'TDDCellTotal': 0,
                'NRCellEnabled': 0,
                'NRCellTotal': 0,
                'Critical': 0,
                'Major': 0,
                'Total': 0
            }
            
            
            node_status_df = pd.read_excel(filename, sheet_name="NodeStatus")

            # create a blank row based on existing columns
            blank_row = {col: "" for col in node_status_df.columns}

            # put blank row at the top
            new_df = pd.concat(
                [pd.DataFrame([blank_row]), node_status_df],
                ignore_index=True
            )

            print(new_df, "new_dfnew_dfnew_dfnew_dfnew_df")
            
            
            wb = load_workbook(filename)
            ws = wb["NodeStatus"]
             # new text for merged cell

            # Merge first column’s second & third rows (A2:A3)
            # ws.merge_cells(start_row=1, start_column=1, end_row=2, end_column=1)
            # ws.merge_cells(start_row=1, start_column=2, end_row=2, end_column=2)
            # ws['A1'] = "NodeId" 
            # ws['B1'] = "Syncstatus" 
            
            
            new_df.fillna("NA", inplace=True)
            with pd.ExcelWriter(filename, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                
                new_df.to_excel(writer, sheet_name="NodeStatus", index=False)

            
            
            wb = load_workbook(filename)
            ws = wb["NodeStatus"]
             # new text for merged cell

            ws.merge_cells('A1:A2'); ws['A1'] = "NodeId"
            ws.merge_cells('B1:B2'); ws['B1'] = "SyncState"

            ws.merge_cells('C1:D1'); ws['C1'] = "TermPointToAmf"
            ws.merge_cells('E1:F1'); ws['E1'] = "FDD Cell Count"
            ws.merge_cells('G1:H1'); ws['G1'] = "TDD Cell Count"
            ws.merge_cells('I1:J1'); ws['I1'] = "NR Cell Count"
            ws.merge_cells('K1:M1'); ws['K1'] = "Alarm Count"

            # row2 subheaders
            ws['C2'] = "Enabled"; ws['D2'] = "Total"
            ws['E2'] = "Enabled"; ws['F2'] = "Total"
            ws['G2'] = "Enabled"; ws['H2'] = "Total"
            ws['I2'] = "Enabled"; ws['J2'] = "Total"
            ws['K2'] = "CRITICAL"; ws['L2'] = "MAJOR"
            ws['M2'] = "Total"

            # optional: center align headers
            for row in ws.iter_rows(min_row=1, max_row=2,
                                    min_col=1, max_col=13):  # adjust max_col
                for cell in row:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
 
            yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
            for row in ws.iter_rows(min_row=1, max_row=2):  # row 1 and row 2
                for cell in row:
                    cell.fill = yellow_fill

            
            green = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")
            red = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
            grey = PatternFill(start_color="C0C0C0", end_color="C0C0C0", fill_type="solid")

            for row in ws.iter_rows(min_row=3):  # skip the two header rows
                node_id = row[0].value
                sync_state = row[1].value

                # SyncState colour
                if sync_state == "SYNCHRONIZED":
                    row[1].fill = green
                else:
                    row[1].fill = red

                # Enabled/Total sets
                for enabled_col, total_col in [(2,3), (4,5), (6,7), (8,9)]:  # adjust for your layout
                    enabled = row[enabled_col].value
                    total = row[total_col].value

                    if enabled == "NA" or total == "NA":
                        row[enabled_col].fill = grey
                        row[total_col].fill = grey
                    elif enabled == total:
                        row[enabled_col].fill = green
                        row[total_col].fill = green
                    else:
                        row[enabled_col].fill = red
                        row[total_col].fill = red

                # Alarm Count
                
                print(row[10].value,"rowrowrowrowrow")
                critical = row[10].value  # adjust indices
                major = row[11].value
                
                if critical > 0:
                    row[10].fill = red
                if major > 0:
                    row[11].fill = red
                    
                if critical == 0:
                    row[10].fill = green
                if major == 0:
                    row[11].fill = green
                    
                    
            wb.save(filename)

        
        
    def coloring_formatting(self, filename):
        
        
        # print(filename,"filename")
        
        
        # Load existing workbook
        wb = load_workbook(filename)
        fill_enabled  = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")  # red
        fill_disabled = PatternFill(start_color="808080", end_color="808080", fill_type="solid")  # gray
        fill_unlocked = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")  # red
        fill_locked   = PatternFill(start_color="808080", end_color="808080", fill_type="solid")  # gray
        green  = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")  # red
        gray = PatternFill(start_color="808080", end_color="808080", fill_type="solid")  # gray
        red = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")  # red
        white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")  # red
        reddish = PatternFill(start_color="EF6767", end_color="EF6767", fill_type="solid")  # red
        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")


        
        # lock + disable = "gray"
        
        
        # unlock + disable = "red"
        
        
        

        # Loop through all sheets
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            # print("Formatting:", sheet)

            # find headers row (assuming first row is header)
            headers = {cell.value: idx for idx, cell in enumerate(ws[1], start=1)}
            
            for col in ["operationalState","operationalState_pre","operationalState_post","administrativeState",
                        "administrativeState_pre","administrativeState_post","syncStatus"]:
                if col in headers:
                    col_idx = headers[col]
                    for row in range(2, ws.max_row + 1):  # skip header row
                        cell = ws.cell(row=row, column=col_idx)
                        if cell.value == "ENABLED":
                            cell.fill = fill_enabled
                        elif cell.value == "DISABLED":
                            cell.fill = fill_disabled
                        elif cell.value == "UNLOCKED":
                            cell.fill = fill_unlocked
                        elif cell.value == "LOCKED":
                            cell.fill = fill_locked
                        elif cell.value == "SYNCHRONIZED":
                            cell.fill = green
                        elif cell.value == "UNSYNCHRONIZED":
                            cell.fill = red
                        elif cell.value == "TOPOLOGY":
                            cell.fill = red
            
            
            
            if "operationalState" in headers and "administrativeState" in headers:
                os_col_idx = headers["operationalState"]
                as_col_idx = headers["administrativeState"]
                pre_os_col_idx = headers["operationalState_pre"] if "operationalState_pre" in headers else None
                pre_as_col_idx = headers["administrativeState_pre"] if "administrativeState_pre" in headers else None
                post_os_col_idx = headers["operationalState_post"] if "operationalState_post" in headers else None
                post_as_col_idx = headers["administrativeState_post"] if "administrativeState_post" in headers else None
                
                
                for row in range(2, ws.max_row + 1):  
                    os_cell = ws.cell(row=row, column=os_col_idx)
                    as_cell = ws.cell(row=row, column=as_col_idx)
                    
                        
                    if os_cell.value == "ENABLED":
                        os_cell.fill = green
                        as_cell.fill = green
                    elif (os_cell.value == "DISABLED" and as_cell.value == "UNLOCKED"):
                        os_cell.fill = red
                        as_cell.fill = red
                    
                    elif (os_cell.value == "DISABLED" and as_cell.value == "LOCKED"):
                        os_cell.fill = gray
                        as_cell.fill = gray
                        
                    print(os_cell.value,"amit os_cell.value")
                    print(as_cell.value,"amit as_cell.value")
                    
                    if(pre_os_col_idx and pre_as_col_idx):
                        pre_os_cell = ws.cell(row=row, column=pre_os_col_idx)
                        pre_as_cell = ws.cell(row=row, column=pre_as_col_idx)
                        
                        print(pre_os_cell.value,"amit pre_os_cell.value")
                        print(pre_as_cell.value,"amit pre_as_cell.value")
                        
                        if pre_os_cell.value == "ENABLED":
                            pre_os_cell.fill = green
                            pre_as_cell.fill = green
                            
                            
                        elif pre_os_cell.value == "DISABLED" and pre_as_cell.value == "UNLOCKED":
                            pre_os_cell.fill = red
                            pre_as_cell.fill = red
                            
                        elif pre_os_cell.value == "DISABLED" and pre_as_cell.value == "LOCKED":
                            pre_os_cell.fill = gray
                            pre_as_cell.fill = gray
                    
                        
                    if(post_os_col_idx and post_as_col_idx):
                        post_os_cell = ws.cell(row=row, column=post_os_col_idx)
                        post_as_cell = ws.cell(row=row, column=post_as_col_idx)
                        print(post_os_cell.value,"amit post_os_cell.value")
                        print(post_as_cell.value,"amit post_as_cell.value")
                        
                        if post_os_cell.value == "ENABLED":
                            post_os_cell.fill = green
                            post_as_cell.fill = green
                            
                            
                        elif post_os_cell.value == "DISABLED" and post_as_cell.value == "UNLOCKED":
                            post_os_cell.fill = red
                            post_as_cell.fill = red
                            
                        elif post_os_cell.value == "DISABLED" and post_as_cell.value == "LOCKED":
                            post_os_cell.fill = gray
                            post_as_cell.fill = gray
                    
                       
                 
            if "status" in headers:
                print(headers,"headersheadersheadersheaders")
                
                status_col_idx = headers["status"]
                operationalState_post_col_idx = headers["operationalState_post"]
                for row in range(2, ws.max_row + 1):  
                    status_cell = ws.cell(row=row, column=status_col_idx)
                    operationalState_post_cell = ws.cell(row=row, column=operationalState_post_col_idx)
                    # print(operationalState_post_cell.value,status_cell.value == "Status Changes")
                    if status_cell.value == "Status Changes" and operationalState_post_cell.value == "DISABLED":
                        for col in range(1, ws.max_column + 1):
                            ws.cell(row=row, column=col).fill = red
                    elif status_cell.value == "No Status Changes":
                        for col in range(1, ws.max_column + 1):
                            ws.cell(row=row, column=col).fill = white
                            
                    elif status_cell.value == "Missing in post check":
                        for col in range(1, ws.max_column + 1):
                            ws.cell(row=row, column=col).fill = reddish
                            
                    elif status_cell.value == "Missing in pre check":
                        for col in range(1, ws.max_column + 1):
                            ws.cell(row=row, column=col).fill = reddish

        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            
            # Apply yellow fill to header row (row 1)
            for cell in ws[1]:
                cell.fill = yellow_fill
                
            ws.auto_filter.ref = ws.dimensions
        
        wb.save(filename)
        
        

        

    def str_to_json(self,text):
        s = text
        
        match = re.match(r"(\w+)\s*:\s*{(.+)}", s.strip())
        if not match:
            raise ValueError("String format not recognized")

        outer_key, inner = match.groups()

        # Replace key=value → "key": "value"
        inner = re.sub(r"(\w+)=([^,}]+)", r'"\1": "\2"', inner)

        # Build final JSON string
        json_str = f'{{ "{outer_key}": {{ {inner} }} }}'

        return json.loads(json_str)

        
        
    
        
    def filtering_header(self, filename,file_sitess):
        
        print(filename)
        xls = pd.ExcelFile(filename)
        sites_data = pd.read_excel(file_sitess)
        sites_data["NodeId"] = sites_data["Node"]

        updated_sheets = {}

        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            
            
            if "NodeId" not in df.columns and "Node" in df.columns:
                df["NodeId"] = df["Node"]
            if "NodeId" not in df.columns and "NodeName" in df.columns:
                df["NodeId"] = df["NodeName"]


            
            df_filtered = df[df["NodeId"].isin(sites_data["NodeId"])]
            
            print(df_filtered,sites_data["NodeId"],"df_filtereddf_filtereddf_filtered")

            updated_sheets[sheet] = df_filtered
        with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
            for sheet_name, data in updated_sheets.items():
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                
        
        
    
    
    
    def renaming_header(self, filename):
        xls = pd.ExcelFile(filename)
        
        rename_map = {
            "EUtranCellFDD": {"col": "EUtranCellFDD", "type": "FDD"},
            "EUtranCellTDD": {"col": "EUtranCellTDD", "type": "TDD"},
            "NRCellDU": {"col": "NRCellDU", "type": "NR"}
        }
        
        
        # Read all sheets first
        sheet_dfs = {}
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            
            df = df.rename(columns={"NetworkElement":"NodeId","MeContext":"NodeId"})

            if sheet in rename_map:
                df = df.rename(columns={rename_map[sheet]["col"]: "CellName"})
                df = df.rename(columns={"MeContext": "NodeId"})
                df["CellType"] = rename_map[sheet]["type"]

            sheet_dfs[sheet] = df

        
        
        with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
            
            for sheet_name, df in sheet_dfs.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            # 
                

    def rearrangecol(self,file_name):
        
        xls = pd.ExcelFile(file_name)
        
        # Read all sheets first
        sheet_dfs = {}
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            sheet_dfs[sheet] = df

        listof = ["FinalStatus" , "NodeStatus", "CellStatus", "AlarmStatus", "TermPointToAmf",  "NRCellDU", "EUtranCellFDD", "EUtranCellTDD"]
        
        
        for i in sheet_dfs.keys():
            if( i not in listof):
                listof.append(i)
        
        
        with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:
            
            for one_sheet in listof:
                # print(sheet_dfs.keys(),"sheet_dfssheet_dfs")
                if(one_sheet in sheet_dfs.keys()):
                    sheet_dfs[one_sheet].to_excel(writer, sheet_name=one_sheet, index=False)
    
    
    def merge_row_tdd_fdd_nr(self, file_name):
        
        xls = pd.ExcelFile(file_name)
        
        rename_map = ["EUtranCellFDD","EUtranCellTDD","NRCellDU"]

        # Read all sheets first
        sheet_dfs = {}
        
        df_list = []
        
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            
            if sheet in rename_map:
                
                df_list.append(df[["NodeId","CellName","CellType","administrativeState","operationalState"]])

            
            sheet_dfs[sheet] = df
        if(len(df_list) > 0):
                
            df = pd.concat(df_list,ignore_index=True)    
            sheet_dfs["CellStatus"] = df

            # Overwrite the same file
            with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:
                for sheet_name, df in sheet_dfs.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

    
    # def txt_to_csv(self, file_name, p_type):
        
        
    #     final_file = os.path.join("downloads",p_type+datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + "_cells_data.xlsx")
        
    #     # print(file_name)
    #     with open(os.path.join(os.getcwd(),file_name)) as file:
    #         file_data = file.read()
    #         raw_text = ""
    #         raw_text_list = []
    #         fdn = False
    #         all_d = []
    #         file_d_list = {}
    #         mo_name = ""
            
            
    #         for j, line in enumerate(file_data.splitlines(), start=1):
                
                
    #             # print(all_d,"dashndkjashdkjsakdkjasdsadaskdnsa")
    #             print(line,all_d,"linelinelinelinelineall_dall_dall_dall_dall_dall_d")
    #             if("FDN" in line): 
    #                 if(mo_name not in file_d_list):
    #                     file_d_list[mo_name] = ", ".join(all_d).replace("FDN :","")
    #                 else:
    #                     file_d_list[mo_name] = file_d_list[mo_name] + "\n" + ", ".join(all_d).replace("FDN :","")
                    
    #                 all_d = []
    #                 all_d = line.split(",")
    #                 mo_name = all_d[-1].split("=")[0]
    #                 fdn = True
    #                 file_change = line
                
    #             else:
    #                 if(len(line.strip()) > 0):
                        
    #                     lcl_val = []
    #                     if("{" in line):
    #                         # print(line,"Dasjndkjasndkja")
    #                         val_self = self.str_to_json(line)
    #                         for oneHeadValkey,oneHeadValVal in val_self.items():
    #                             for koneHeadValkey,voneHeadValVal in oneHeadValVal.items():
    #                                 lcl_val.append(oneHeadValkey+"_"+koneHeadValkey+" : "+voneHeadValVal)
                                    
    #                         line_val = ", ".join(lcl_val)
    #                         all_d.append(", "+line_val)
                            
    #                     if("[" in line):
    #                         line_val = line.replace(",","_spcheckcomma_")
    #                         line_val = line_val.replace("=","_spcheckequal_")
    #                         all_d.append(line_val)
    #                     else:
    #                         all_d.append(line)
                    
                
    #             if(len(line.strip()) == 0 and fdn):
    #                 fdn = False
                
                
                
                
                
                
                
    #             if(fdn):
    #                 raw_text = raw_text+"\n"+line
                    
                    
    #             else:
    #                 raw_text_list.append(raw_text)
    #                 raw_text = ""
                

                
            
    #         with pd.ExcelWriter(final_file) as writer:
                
                
    #             for key, values in file_d_list.items():
    #                 if(key != "" and len(values.strip()) > 0):
    #                     data = {}
                        
                        
    #                     rows = []
                        
    #                     # print(values)
    #                     for line in values.split("\n"):
    #                         parsed = {}
    #                         for part in line.split(","):
    #                             if "=" in part:
    #                                 k, v = part.split("=", 1)
    #                                 parsed[k.strip()] = v.strip()
    #                             elif ":" in part:
    #                                 # print(part,"partpartpartpartpartpartpart")
                                    
                                    
                                    
    #                                 k, v = part.split(":", 1)
    #                                 parsed[k.strip()] = v.strip().replace("_spcheckcomma_",", ").replace("_spcheckequal_","=")
    #                         rows.append(parsed)

    #                     df = pd.DataFrame(rows)
                        
                        
    #                     df.to_excel(writer, sheet_name=key, index=False)  
    #                     if("post" in file_name and key == "TermPointToAmf"):
    #                         print(df,len(rows),"keykeykeykey",key,"final_filefinal_filefinal_filefinal_filefinal_filefinal_file")
        
                
                
    #     if("post" in file_name):
    #         cedledmcl
    #         print(final_file,"final_filefinal_filefinal_filefinal_filefinal_filefinal_file")
    #     return final_file
    
    
    
    def txt_to_csv(self, file_name, p_type):
        # create output Excel path
        final_file = os.path.join(
            "downloads",
            p_type + datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + "_cells_data.xlsx"
        )

        with open(os.path.join(os.getcwd(), file_name)) as file:
            file_data = file.read()

            raw_text = ""
            raw_text_list = []
            fdn = False
            all_d = []
            file_d_list = {}
            mo_name = ""

            for j, line in enumerate(file_data.splitlines(), start=1):

                if "FDN" in line:
                    # flush previous block (if any)
                    if all_d and mo_name:
                        if mo_name not in file_d_list:
                            file_d_list[mo_name] = ", ".join(all_d).replace("FDN :", "")
                        else:
                            file_d_list[mo_name] += "\n" + ", ".join(all_d).replace("FDN :", "")

                    # start new block
                    all_d = line.split(",")
                    mo_name = all_d[-1].split("=")[0]
                    fdn = True

                else:
                    if len(line.strip()) > 0:
                        lcl_val = []
                        if "{" in line:
                            val_self = self.str_to_json(line)
                            for oneHeadValkey, oneHeadValVal in val_self.items():
                                for koneHeadValkey, voneHeadValVal in oneHeadValVal.items():
                                    lcl_val.append(
                                        oneHeadValkey + "_" + koneHeadValkey + " : " + voneHeadValVal
                                    )
                            line_val = ", ".join(lcl_val)
                            all_d.append(", " + line_val)

                        if "[" in line:
                            line_val = line.replace(",", "_spcheckcomma_")
                            line_val = line_val.replace("=", "_spcheckequal_")
                            all_d.append(line_val)
                        else:
                            all_d.append(line)

                if len(line.strip()) == 0 and fdn:
                    fdn = False

                if fdn:
                    raw_text = raw_text + "\n" + line
                else:
                    raw_text_list.append(raw_text)
                    raw_text = ""

            # 🔴 flush the final block at end of file
            if all_d and mo_name:
                if mo_name not in file_d_list:
                    file_d_list[mo_name] = ", ".join(all_d).replace("FDN :", "")
                else:
                    file_d_list[mo_name] += "\n" + ", ".join(all_d).replace("FDN :", "")

            # write Excel
            with pd.ExcelWriter(final_file) as writer:
                for key, values in file_d_list.items():
                    if key and len(values.strip()) > 0:
                        rows = []
                        for line in values.split("\n"):
                            parsed = {}
                            for part in line.split(","):
                                if "=" in part:
                                    k, v = part.split("=", 1)
                                    parsed[k.strip()] = v.strip()
                                elif ":" in part:
                                    k, v = part.split(":", 1)
                                    parsed[k.strip()] = v.strip().replace(
                                        "_spcheckcomma_", ", "
                                    ).replace("_spcheckequal_", "=")
                            rows.append(parsed)

                        df = pd.DataFrame(rows)
                        df.to_excel(writer, sheet_name=key, index=False)
                        if "post" in file_name and key == "TermPointToAmf":
                            print(df, len(rows), "keykeykeykey", key, "final_filefinal_file")
                            
        if "post" in file_name:
            print(final_file, "final_filefinal_filefinal_file")

        return final_file

    
    
        
        
    
    def start_parser(self,files,p_type,file_sitess):
        
        alarm_check = False
        converted_file = []
        alarms_data = pd.DataFrame([])
        
        file_parsed = ""
        for one_file in files:
            # print(one_file)
            with open(os.path.join(os.getcwd(),one_file)) as file:
                file_data = file.read()
                if("FDN : " in file_data):
                    # print("FDN in filedat")
                    file_parsed = self.txt_to_csv(one_file,p_type)
                    self.file_parsed = file_parsed
                    
                    self.renaming_header(file_parsed)
                    self.filtering_header(file_parsed,file_sitess)
                    
                    print()
                    self.merge_row_tdd_fdd_nr(file_parsed)
                    self.coloring_formatting(file_parsed)
                    
                    self.remove_extra_col(file_parsed)
                    # print("FDNX in filedat")
                    
                
                if("Total number of alarms fetched for the given query" in file_data):
                    
                    alarms_data = self.alarm(file_data)
                    alarm_check = True
                    self.alarm_data = alarms_data
                    
                    
            
                    
            # print(alarms_data,"alarms_data")
            
        if(alarm_check):
            self.alarm_checker(file_parsed,file_sitess)
        
        
        
        return self.file_parsed
            
        