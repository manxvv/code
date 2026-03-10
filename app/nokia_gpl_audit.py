import paramiko
import pymssql
import pandas as pd
import os
import time
import glob
import re

# ================== GLOBAL CONFIG ==================
ssh_host = os.environ.get("SSH_HOST")
ssh_user = os.environ.get("SSH_USER")
ssh_pass = os.environ.get("SSH_PASS")

user = "nokia_audit"
data_path  = f"/data/web/{user}/"
xml_path   = f"{data_path}xml/"
output_dir = f"{data_path}output/"

local_zip_folder = "/root/ma/backend/code/uploads/enm_files_nokia_two/"



mssql_host = os.environ.get("MSSQL_HOST")
mssql_user = os.environ.get("MSSQL_USER")
mssql_pass = os.environ.get("MSSQL_PASS")
mssql_db   = "mcom_india_nokia_audit"


def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()

    if out:
        print(out)
    if err:
        print(err)

    if exit_code != 0:
        raise Exception(f"Command failed: {cmd}")



# =====================================================
# MAIN FUNCTION
# =====================================================
def process_xml_and_audit(local_zip_file):

    print("\n====== STARTING XML AUDIT PROCESS ======\n")

    data_path  = f"/data/web/{user}/"
    xml_path   = f"{data_path}xml/"
    input_xml  = f"{xml_path}input/"
    output_dir = f"{xml_path}output/"
    
 

    # ---------------- SSH CONNECT ----------------
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, username=ssh_user, password=ssh_pass)

    # ---------------- CLEAN ----------------
    print("🧹 Cleaning old user folder...")
    run(ssh, f"rm -rf {data_path}")

    print("📁 Creating directories...")
    run(ssh, f"mkdir -p {input_xml}")
    run(ssh, f"mkdir -p {output_dir}")

    # ---------------- UPLOAD ZIP AS input.zip ----------------
    remote_zip = f"{xml_path}input.zip"
    print("⬆ Uploading ZIP as input.zip ...")

    sftp = ssh.open_sftp()
    sftp.put(local_zip_file, remote_zip)
    sftp.close()

    run(ssh, f"ls -lh {remote_zip}")

    # ---------------- UNZIP ----------------
    print("📦 Unzipping into fixed input folder...")

    # unzip to temp then move everything inside input/
    run(ssh, f"unzip -o {remote_zip} -d {xml_path}")

    # move all xml recursively into input/
    run(ssh, f"find {xml_path} -type f -name '*.xml' -exec mv {{}} {input_xml} \\;")

    # remove zip and extra folders
    run(ssh, f"rm -f {remote_zip}")
    run(ssh, f"find {xml_path} -mindepth 1 -maxdepth 1 -type d ! -name 'input' -exec rm -rf {{}} \\;")

    print("📂 Final XML files:")
    run(ssh, f"ls -lh {input_xml}")

    # ---------------- RUN JAVA ----------------
    print("⚙ Running NCM JAR...")

    java_cmd = f"java -jar /opt/jar/ncm.jar {input_xml} /opt/jar/Nokia_CM.txt read 1"
    # run(ssh, java_cmd)

    # ssh.close()
    stdin, stdout, stderr = ssh.exec_command(java_cmd)

    output = stdout.read().decode()
    error = stderr.read().decode()

    # print(output)
    print("qwertyuiuytrewertyu",error)

    if "ParseException" in output or "ParseException" in error or "XML not terminated properly" in output:
        ssh.close()
        print("❌ XML parsing failed - file may be corrupted")

        return {
            "status": "error",
            "message": "The XML dump file appears to be incomplete or corrupted. Please regenerate and upload the file again."
        }

    ssh.close()
    

    # ===================================================
    # MSSQL PROCEDURES
    # ===================================================
    try:
        print("\n🗄 Connecting MSSQL...\n")

        conn = pymssql.connect(
            server=mssql_host,
            user=mssql_user,
            password=mssql_pass,
            database=mssql_db,
            autocommit=True
        )

        cursor = conn.cursor()

        print("⚙ Running Procedures...\n")
        cursor.execute("EXEC clean_data")
        print("🟢 clean_data done")
        cursor.execute("EXEC [dbo].[load_csv] %s", (output_dir,))
        print("🟢 load_csv done")

        cursor.execute("EXEC [dbo].[Conditional_defination_main] %s", (user,))
        print("🟢 Conditional_defination_main done")

        cursor.execute("EXEC [dbo].[conditional_distname] %s", (user,))
        print("🟢 conditional_distname done")

        cursor.execute("EXEC [dbo].[paramter_audit] %s", (user,))
        print("🟢 paramter_audit done")

        # ================= EXPORT =================
        output_path = "/var/www/dataplusBe/code/uploads/nokia_gpt_audit_output"
        os.makedirs(output_path, exist_ok=True)
        output_file = os.path.join(output_path, "exported_data.xlsx")

        export_queries = {
            "Parameters":
                "SELECT * FROM [mcom_india_nokia_audit].[set].[Nokia_Parameters]",
            "Discrepancies":
                "SELECT * FROM [mcom_india_nokia_audit].[ison].[Nokia_Parameters_Discrepancies]"
        }

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet, query in export_queries.items():
                print(f"📊 Exporting {sheet} ...")
                df = pd.read_sql(query, conn)
                
                df.to_excel(writer, sheet_name=sheet[:31], index=False)

        conn.close()

        print("\n🎉 XML AUDIT COMPLETED SUCCESSFULLY 🎉\n")

    except Exception as e:
        print("❌ MSSQL ERROR:", e)
        return False

    return True



# ===================================================================
# 🔵 FUNCTION 2 — Upload Excel Sheets into MSSQL (Clean + Insert)
# ===================================================================
def upload_excel_sheets_to_mssql(excel_path):
    print("\n============================")
    print("📄 Reading Excel File:", excel_path)
    print("============================\n")

    # SHEET ORDER (as per your requirement)
    df_parameters = pd.read_excel(excel_path, sheet_name=0)   # Nokia_Parameters
    df_condition  = pd.read_excel(excel_path, sheet_name=1)   # Condition_Defination
    df_class_map  = pd.read_excel(excel_path, sheet_name=2)   # Condition_Defination

    # Normalize column names
    df_condition.columns  = df_condition.columns.str.strip().str.lower().str.replace(" ", "_")
    df_parameters.columns = df_parameters.columns.str.strip().str.lower().str.replace(" ", "_")
    df_class_map.columns = df_class_map.columns.str.strip().str.lower().str.replace(" ", "_")

    print("🔍 SHEET-1 PARAMETERS HEADERS:", df_parameters.columns.tolist(), "\n")
    print("🔍 SHEET-2 CONDITION HEADERS:", df_condition.columns.tolist(), "\n")
    print("🔍 SHEET-3 CLASS MAP HEADERS:", df_class_map.columns.tolist(), "\n")

    # Replace NaN with None
    df_condition  = df_condition.where(pd.notnull(df_condition), None)
    df_parameters = df_parameters.where(pd.notnull(df_parameters), None)
    df_class_map = df_class_map.where(pd.notnull(df_class_map), None)

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
    df_class_map = df_class_map.applymap(clean_str)

    print("🧹 Cleaning completed.\n")

    # ---------------- CONNECT DATABASE ----------------
    conn = pymssql.connect(
        server=mssql_host,
        user=mssql_user,
        password=mssql_pass,
        database=mssql_db,
        autocommit=True
    )
    cur = conn.cursor()

    # Detect schema
    cur.execute("""
        SELECT TABLE_SCHEMA 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'Nokia_Parameters'
    """)
    row = cur.fetchone()

    if not row:
        raise Exception("❌ ERROR: SQL TABLE 'Nokia_Parameters' NOT FOUND!")

    schema = row[0]
    print(f"🟢 Using schema: {schema}")

    # ------- TRUNCATE DATA ONLY (NO DROP) ------
    cur.execute(f"DELETE FROM [{schema}].[Condition_Defination]")
    cur.execute(f"DELETE FROM [{schema}].[Nokia_Parameters]")
    cur.execute(f"DELETE FROM [{schema}].[class_map]")
    conn.commit()

    print("🗑 Old data cleared.\n")

    # ---------------- INSERT INTO Class_Map ----------------
    class_map = {
        "class": "Class",
        "class_map": "class_map"
    }

    insert_class_map = f"""
        INSERT INTO [{schema}].[class_map]
        ({','.join(f'[{v}]' for v in class_map.values())})
        VALUES ({','.join(['%s'] * len(class_map))})
    """

    for _, row in df_class_map.iterrows():
        values = [row.get(col) for col in class_map.keys()]
        cur.execute(insert_class_map, values)

    conn.commit()
    print("🟢 class_map inserted.\n")

    # ---------------- INSERT INTO Condition_Defination ----------------
    condition_map = {
        "condition_name": "Condition_name",
        "priority": "Priority",
        "class": "Class",
        "class_map": "class_map",
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
  "technology": "Technology",
  "parent": "Parent",
  "mo_class": "MO_Class",
  "abbreviated_name": "Abbreviated_Name",
  "full_name": "Full_Name",
  "description": "Description",
  "category": "Category",
  "condition_name": "Condition_name",
  "operator_recommended_value": "Operator_Recommended_Value",
  "data_type": "Data_Type",
  "son_enforced": "SON_Enforced",
  "priority": "Priority",
  "remarks": "Remarks",
  "last_updated_on": "Last_Updated_On",
  "total_count": "Total_Count",
  "meeting_criteria": "Meeting_Criteria",
  "percentage": "Percentage"
}


    insert_parameters = f"""
        INSERT INTO [{schema}].[Nokia_Parameters]
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

