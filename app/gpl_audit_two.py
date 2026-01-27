import paramiko
import pymssql
import pandas as pd
import os
import time
import glob
import re

# ================== GLOBAL CONFIG ==================
ssh_host = "31.220.88.4"
ssh_user = "root"
ssh_pass = "cf2DgN8vhM4d"

user = "eric2"
data_path  = f"/data/web/{user}/"
xml_path   = f"{data_path}xml/"
output_dir = f"{data_path}output/"

local_zip_folder = "/root/ma/backend/code/uploads/enm_files_nokia_two/"

mssql_host = "31.220.88.4"
mssql_user = "sa"
mssql_pass = "Sarfraz@987"
mssql_db   = "mcom_india_cm"


# ===================================================================
# 🔵 FUNCTION 1 — ZIP Upload → Java JAR → SQL Procedures → Save CSV
# ===================================================================
def process_zip_and_run_procedures(local_zip_file):

    print("\n====== STARTING ZIP PROCESSING FUNCTION ======\n")

    # ---------------- SSH CONNECT ----------------
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, username=ssh_user, password=ssh_pass)

    # ---------------- CLEAN OLD FILES ----------------
    ssh.exec_command(f"rm -rf {output_dir}*")
    ssh.exec_command(f"rm -rf {xml_path}*")
    time.sleep(1)

    ssh.exec_command(f"mkdir -p {xml_path}")
    ssh.exec_command(f"mkdir -p {output_dir}")
    time.sleep(1)

    # ---------------- FIND LATEST ZIP ----------------
    # zip_files = glob.glob(os.path.join(local_zip_folder, "*.zip"))
    
    # if not zip_files:
    #     print("❌ NO ZIP FILE FOUND!")
    #     return False

    if not os.path.exists(local_zip_file):
        print(f"❌ SPECIFIED ZIP FILE NOT FOUND: {local_zip_file}")
        return False    

    latest_zip = local_zip_file

    remote_zip = f"{xml_path}input.zip"

    # ---------------- UPLOAD ZIP ----------------
    with ssh.open_sftp() as sftp:
        sftp.put(latest_zip, remote_zip)

    # ---------------- UNZIP ----------------
    stdin, stdout, stderr = ssh.exec_command(f"unzip -o {remote_zip} -d {xml_path}")
    print(stdout.read().decode())
    print(stderr.read().decode())
    print("🟢 Unzip completed.\n")

    # ---------------- RUN JAVA JAR ----------------
    java_cmd = f"java -jar /opt/jar/DataPlus_E_CM.jar {xml_path} {output_dir}"
    stdin, stdout, stderr = ssh.exec_command(java_cmd)

    print(stdout.read().decode())
    print(stderr.read().decode())
    print("🟢 Java JAR completed.\n")

    # ===================================================
    # STRICT STRUCTURE-SAFE CSV CLEANING
    # ===================================================

    print("🧹 Strict cleaning CSV files before MSSQL import...\n")

    sftp = ssh.open_sftp()
    local_tmp = "/tmp/gpt_clean/"
    os.makedirs(local_tmp, exist_ok=True)

    # Download CSV files
    for file in sftp.listdir(output_dir):
        if file.endswith(".csv"):
            sftp.get(output_dir + file, os.path.join(local_tmp, file))
    sftp.close()

    # Correct column name mapping
    COLUMN_FIX = {
        "Site_type": "Site_Type",
        "site_type": "Site_Type",
        "SITE_TYPE": "Site_Type",
        "son_enforced": "SON_Enforced",
        "parameter description": "Parameter Description",
        "associated feature name": "Associated Feature Name",
        "dump value": "dump value",
        "coun check": "Coun Check"
    }

    NUMERIC_COLS = [
        "SON_Enforced",
        "priority",
        "Percentage",
        "Total_Count",
        "Parameter_Value",
        "Correction",
        "dump value",
        "Check_sarfraz",
        "Coun Check"
    ]

    def force_numeric(val):
        """Returns safe float or None."""
        if pd.isna(val):
            return None

        val = str(val).strip()
        val = val.replace("%", "").replace(",", "")

        if val == "" or val in ["-", "none", "None", "nan"]:
            return None

        if re.search(r"[A-Za-z]", val):
            return None

        try:
            return float(val)
        except:
            return None

    # Clean CSV files
    for file in os.listdir(local_tmp):
        if not file.endswith(".csv"):
            continue

        fpath = os.path.join(local_tmp, file)
        df = pd.read_csv(fpath, dtype=str)

        # FIX COLUMN NAMES FIRST
        fixed_columns = {}
        for col in df.columns:
            key = col.strip()
            fixed_columns[col] = COLUMN_FIX.get(key, key)

        df.rename(columns=fixed_columns, inplace=True)

        # Clean numeric columns
        for col in df.columns:
            if col in NUMERIC_COLS:
                df[col] = df[col].apply(force_numeric)
            else:
                df[col] = df[col].replace(["nan", "None", "none", "---", "--", ""], None)

        df.to_csv(fpath, index=False)

    # Upload cleaned CSVs back
    sftp = ssh.open_sftp()
    for file in os.listdir(local_tmp):
        sftp.put(os.path.join(local_tmp, file), output_dir + file)
    sftp.close()

    print("🟢 CSV strict cleaning completed.\n")

    ssh.close()

    # ===================================================
    # RUN MSSQL PROCEDURES
    # ===================================================
    try:
        conn = pymssql.connect(
            server=mssql_host,
            user=mssql_user,
            password=mssql_pass,
            database=mssql_db
        )
        cursor = conn.cursor()

        print("⚙ Running MSSQL procedures...\n")

        cursor.execute("EXEC clean_data")
        print("🟢 Data cleaning procedure done.\n")
        cursor.execute("EXEC load_csv %s, %s", ("Yes", output_dir))
        print("🟢 CSV loading procedure done.\n")
        cursor.execute("EXEC Conditional_defination_main %s", ("sarfraz",))
        print("🟢 Condition definition procedure done.\n")
        cursor.execute("EXEC conditional_distname %s", ("sarfraz",))
        print("🟢 Conditional distname procedure done.\n")
        try:
            cursor.execute("EXEC paramter_audit %s", ("sarfraz",))
        except Exception as e:
            print("⚠ WARNING during paramter_audit execution:", e)
        print("🟢 Parameter audit procedure done.\n")

        conn.commit()

        # EXPORT FINAL TABLES
        output_path = "/root/ma/backend/code/uploads/gpt_audit_two_output/"
        os.makedirs(output_path, exist_ok=True)

        export_queries = {
            "Parameters_Discrepancies.csv":
                "SELECT * FROM [ison].[Parameters_Discrepancies]",

            "Parameters.csv":
                """
                SELECT MO_Class,Parameter_Name,Technology,[Parameter Description],
                       [Associated Feature Name],Parameter_Value,Condition_name,
                       [Type],Site_Type,SON_Enforced,data_type,[priority],
                       [Percentage],Meeting_Criteria,Total_Count
                FROM [set].[Parameters]
                WHERE total_count IS NOT NULL
                """
        }

        # for file, query in export_queries.items():
        #     df = pd.read_sql(query, conn)
        #     df.to_csv(os.path.join(output_path, file), index=False)
        #     print(f"📁 Saved → {file}")
        output_file = os.path.join(output_path, "exported_data.xlsx")

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet_name, query in export_queries.items():
                df = pd.read_sql(query, conn)
                
                # Excel sheet names cannot exceed 31 characters
                sheet_name = sheet_name[:31].replace(".csv", "")
                
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"📄 Sheet saved → {sheet_name}")


        conn.close()
        print("\n🎉 FULL ZIP + SQL PROCESS COMPLETED SUCCESSFULLY!\n")

    except Exception as e:
        print("❌ MSSQL ERROR:", e)

    return True


# ===================================================================
# 🔵 FUNCTION 2 — Upload Excel Sheets into MSSQL (Clean + Insert)
# ===================================================================
def upload_excel_sheets_to_mssql(excel_path):
    print("\n============================")
    print("📄 Reading Excel File:", excel_path)
    print("============================\n")

    # SHEET ORDER (as per your requirement)
    df_parameters = pd.read_excel(excel_path, sheet_name=0)   # Parameters
    df_condition  = pd.read_excel(excel_path, sheet_name=1)   # Condition_Defination

    # Normalize column names
    df_condition.columns  = df_condition.columns.str.strip().str.lower().str.replace(" ", "_")
    df_parameters.columns = df_parameters.columns.str.strip().str.lower().str.replace(" ", "_")

    print("🔍 SHEET-1 PARAMETERS HEADERS:", df_parameters.columns.tolist(), "\n")
    print("🔍 SHEET-2 CONDITION HEADERS:", df_condition.columns.tolist(), "\n")

    # Replace NaN with None
    df_condition  = df_condition.where(pd.notnull(df_condition), None)
    df_parameters = df_parameters.where(pd.notnull(df_parameters), None)

    # -------------------------------------------------------------------
    # SAFE STRING CLEANER
    # -------------------------------------------------------------------
    def clean_str(val):
        if val is None:
            return None
        if pd.isna(val):
            return None
        if isinstance(val, str):
            v = val.strip().lower()
            if v in ["nan", "none", "null", "-", ""]:
                return None
            return val.strip()
        return val

    # -------------------------------------------------------------------
    # FLOAT SAFE CLEANER (for float SQL columns)
    # -------------------------------------------------------------------
    def clean_float(val):
        try:
            if val is None:
                return None
            if isinstance(val, str):
                v = val.replace(",", "").replace("%", "").strip()
                if v == "" or v.lower() in ["nan", "none", "null", "-"]:
                    return None
                return float(v)
            return float(val)
        except:
            return None

    # ---------------- APPLY CLEANING FOR FLOAT COLUMNS ----------------
    float_cols_parameters = [
        "coun_check", "percentage", "meeting_criteria", "total_count"
    ]

    for col in float_cols_parameters:
        if col in df_parameters.columns:
            df_parameters[col] = df_parameters[col].apply(clean_float)

    # Condition_Defination FLOAT column
    if "priority" in df_condition.columns:
        df_condition["priority"] = df_condition["priority"].apply(clean_float)

    # Clean string columns
    df_parameters = df_parameters.applymap(clean_str)
    df_condition  = df_condition.applymap(clean_str)

    print("🧹 Cleaning completed.\n")

    # ---------------- CONNECT DATABASE ----------------
    conn = pymssql.connect(
        server=mssql_host,
        user=mssql_user,
        password=mssql_pass,
        database=mssql_db
    )
    cur = conn.cursor()

    # Detect schema
    cur.execute("""
        SELECT TABLE_SCHEMA 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'Parameters'
    """)
    row = cur.fetchone()

    if not row:
        raise Exception("❌ ERROR: SQL TABLE 'Parameters' NOT FOUND!")

    schema = row[0]
    print(f"🟢 Using schema: {schema}")

    # ------- TRUNCATE DATA ONLY (NO DROP) ------
    cur.execute(f"DELETE FROM [{schema}].[Condition_Defination]")
    cur.execute(f"DELETE FROM [{schema}].[Parameters]")
    conn.commit()

    print("🗑 Old data cleared.\n")

    # ---------------- INSERT INTO Condition_Defination ----------------
    condition_map = {
        "condition_name": "Condition_name",
        "priority": "Priority",
        "class": "Class",
        "class_map": "Class_Map",
        "query": "Query"
    }

    insert_condition = f"""
        INSERT INTO [{schema}].[Condition_Defination]
        ({','.join(f'[{v}]' for v in condition_map.values())})
        VALUES ({','.join(['%s'] * len(condition_map))})
    """

    for _, row in df_condition.iterrows():
        values = [row.get(col) for col in condition_map.keys()]
        cur.execute(insert_condition, values)
    

    conn.commit()
    print("🟢 Condition_Defination inserted.\n")

    # ---------------- INSERT INTO Parameters ----------------
    parameter_map = {
        "mo_class": "MO_Class",
        "parameter_name": "Parameter_Name",
        "technology": "Technology",
        "parameter_description": "Parameter Description",
        "associated_feature_name": "Associated Feature Name",
        "parameter_value": "Parameter_Value",
        "condition_name": "Condition_name",
        "type": "Type",
        "site_type": "Site_Type",
        "coun_check": "Coun Check",
        "son_enforced": "SON_Enforced",
        "data_type": "data_type",
        "priority": "priority",
        "correction": "Correction",
        "dump_value": "dump value",
        "check_sarfraz": "Check_sarfraz",
        "percentage": "Percentage",
        "meeting_criteria": "Meeting_Criteria",
        "total_count": "Total_Count"
    }

    insert_parameters = f"""
        INSERT INTO [{schema}].[Parameters]
        ({','.join(f'[{v}]' for v in parameter_map.values())})
        VALUES ({','.join(['%s'] * len(parameter_map))})
    """

    for idx, row3 in df_parameters.iterrows():
        values = [clean_str(row3.get(col)) for col in parameter_map.keys()]

        

        try:
            cur.execute(insert_parameters, values)
        except Exception as e:

            raise e
    conn.commit()
    conn.close()

    print("\n Upload completed successfully — No Float Error, No NULL Issue!")



# process_zip_and_run_procedures("/root/ma/backend/code/uploads/enm_files_nokia_two/823dbad598344a9db8426ad27fcfb5b4_JK2.zip")


# upload_excel_sheets_to_mssql("/root/ma/backend/code/uploads/settings_nokia_two/8d15cdb892754b87a05a83e955ea2997_Input_Parameters2.xlsx")