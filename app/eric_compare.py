import paramiko
import pymssql
import pandas as pd
import os
import time
from dotenv import load_dotenv

load_dotenv()

# ================== SSH SERVER CONFIG ==================


ssh_host = os.environ.get("SSH_HOST")
ssh_user = os.environ.get("SSH_USER")
ssh_pass = os.environ.get("SSH_PASS")

# ================== USER & PATH CONFIG ==================
user = "sarfraz"

data_path  = f"/data/mcom/airtel/eric/compare/{user}/"
# data_path  = f"/ssd/mcom/airtel/eric/compare/{user}/"
xml_path   = f"{data_path}xml/"
output_dir = f"{data_path}output/"


# local_zip_folder = "/root/ma/backend/code/uploads/eric_compare/"
local_zip_folder = "/var/www/dataplusBe/code/uploads/eric_compare/"

# ================== MSSQL CONFIG ==================
mssql_host = os.environ.get("MSSQL_HOST")
mssql_user = os.environ.get("MSSQL_USER")
mssql_pass = os.environ.get("MSSQL_PASS")
mssql_db   = os.environ.get("MSSQL_DB")

# ================== SSH CONNECT ==================
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ssh_host, username=ssh_user, password=ssh_pass)

import pyodbc
import pandas as pd
import os


def upload_setting_to_mssql(setting_file_path: str):

    print("\n============================")
    print("📄 Reading Setting File:", setting_file_path)
    print("============================\n")

    if not os.path.exists(setting_file_path):
        raise Exception("❌ Setting file not found")

    # ---------------- READ EXCEL ----------------
    try:
        xls = pd.ExcelFile(setting_file_path)
    except Exception as e:
        raise Exception(f"❌ Unable to read setting file: {str(e)}")

    # ---------------- CONNECT MSSQL ----------------
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={mssql_host};"
        f"DATABASE={mssql_db};"
        f"UID={mssql_user};"
        f"PWD={mssql_pass};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )

    cursor = conn.cursor()
    cursor.fast_executemany = True

    try:

        # ==================================================
        # 1️⃣ MO_CLASS SHEET
        # ==================================================
        print("📥 Processing sheet: MO_Class")

        df_mo = pd.read_excel(xls, "MO_Class", dtype=str)

        df_mo.columns = (
            df_mo.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        required_cols = ["mo_class", "compare", "script"]

        missing = [c for c in required_cols if c not in df_mo.columns]
        if missing:
            raise Exception(f"❌ Missing columns in MO_Class sheet: {missing}")

        df_mo = df_mo.replace(
            {"": None, "nan": None, "None": None, "null": None, "-": None}
        )

        print("🧹 Clearing old data from [set].[MO_Class]")
        cursor.execute("DELETE FROM [set].[MO_Class]")

        insert_sql = """
        INSERT INTO [set].[MO_Class]
        (MO_Class, Compare, Script)
        VALUES (?, ?, ?)
        """

        df_mo = df_mo.dropna(subset=["mo_class", "compare", "script"])

        data_mo = list(
            df_mo[["mo_class", "compare", "script"]]
            .itertuples(index=False, name=None)
        )

        cursor.executemany(insert_sql, data_mo)

        inserted_mo = len(data_mo)

        # ==================================================
        # 2️⃣ EXCLUSIONS SHEET
        # ==================================================
        print("📥 Processing sheet: Exclusions")

        df_ex = pd.read_excel(xls, "Exclusions", dtype=str)

        print("Raw Exclusions rows:", len(df_ex))

        df_ex.columns = (
            df_ex.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        print("Cleaned Exclusions columns:", df_ex.columns.tolist())

        required_cols = ["mo_class", "parameter"]

        missing = [c for c in required_cols if c not in df_ex.columns]
        if missing:
            raise Exception(f"❌ Missing columns in Exclusions sheet: {missing}")

        df_ex = df_ex.replace(
            {"": None, "nan": None, "None": None, "null": None, "-": None}
        )

        print("🧹 Clearing old data from [set].[Exclusions]")
        cursor.execute("DELETE FROM [set].[Exclusions]")
        print("🧹 Old Exclusions cleared")

        insert_sql = """
        INSERT INTO [set].[Exclusions]
        (MO_Class, Parameters)
        VALUES (?, ?)
        """

        df_ex = df_ex.dropna(subset=["mo_class", "parameter"])

        data_ex = list(
            df_ex[["mo_class", "parameter"]]
            .itertuples(index=False, name=None)
        )

        cursor.executemany(insert_sql, data_ex)

        inserted_ex = len(data_ex)

        conn.commit()

        print(f"✅ MO_Class inserted: {inserted_mo}")
        print(f"✅ Exclusions inserted: {inserted_ex}")

    except Exception as e:
        conn.rollback()
        raise Exception(f"❌ MSSQL insert failed: {str(e)}")

    finally:
        conn.close()

    print("\n🎉 Setting upload completed successfully!\n")

    return {
        "mo_class_inserted": inserted_mo,
        "exclusions_inserted": inserted_ex
    }
def run_eric_compare_file(old_zip_path: str, new_zip_path: str):
    """
    

    Arguments:
        old_zip_path: local path of old.zip
        new_zip_path: local path of new.zip

    Returns:
        final_excel_path (str)
    """


    print("\n🚀 STARTING ERIC COMPARE FULL PROCESS\n")

    # ============================================================
    # SSH CONNECT
    # ============================================================
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, username=ssh_user, password=ssh_pass)

    try:
        # ============================================================
        # STEP 1 → OLD OUTPUT FILES DELETE
        # ============================================================
        ssh.exec_command(f"rm -rf {output_dir}*")
        time.sleep(1)

        # ============================================================
        # STEP 2 → OLD XML FILES DELETE
        # ============================================================
        ssh.exec_command(f"rm -rf {xml_path}*")
        time.sleep(1)

        ssh.exec_command(f"mkdir -p {xml_path}")
        ssh.exec_command(f"mkdir -p {output_dir}")
        time.sleep(1)

        # ============================================================
        # STEP 3 → SCP OLD & NEW ZIP
        # ============================================================
        sftp = ssh.open_sftp()

        remote_old_zip = f"{xml_path}old.zip"
        remote_new_zip = f"{xml_path}new.zip"

        print("📤 SCP old.zip")
        sftp.put(old_zip_path, remote_old_zip)

        print("📤 SCP new.zip")
        sftp.put(new_zip_path, remote_new_zip)

        sftp.close()

        # ============================================================
        # STEP 4 → UNZIP BOTH FILES
        # ============================================================
        # ssh.exec_command(f"unzip -o {remote_old_zip} -d {xml_path}")
        # ssh.exec_command(
        #     f"cd {xml_path} && "
        #     f"ls *.xml | head -n 1 | xargs -I {{}} mv {{}} old.xml"
        # )
        # ssh.exec_command(f"unzip -o {remote_new_zip} -d {xml_path}")
        # time.sleep(1)
        # ssh.exec_command(
        #     f"cd {xml_path} && "
        #     f"ls *.xml | grep -v old.xml | head -n 1 | xargs -I {{}} mv {{}} new.xml"
        # )
        # ssh.exec_command(f"rm -f {remote_old_zip} {remote_new_zip}")
        # time.sleep(2)
        # print("🟢 Unzip completed")

        # ============================================================
        # STEP 4 → UNZIP BOTH FILES & RENAME TO old.xml / new.xml
        # ============================================================

        # Unzip old.zip
        ssh.exec_command(f"unzip -o {remote_old_zip} -d {xml_path}")
        time.sleep(1)

        # Rename extracted OLD file to old.xml
        ssh.exec_command(
            f"cd {xml_path} && "
            f"ls *.xml | head -n 1 | xargs -I {{}} mv {{}} old.xml"
        )

        # Unzip new.zip
        ssh.exec_command(f"unzip -o {remote_new_zip} -d {xml_path}")
        time.sleep(1)

        # Rename extracted NEW file to new.xml
        ssh.exec_command(
            f"cd {xml_path} && "
            f"ls *.xml | grep -v old.xml | head -n 1 | xargs -I {{}} mv {{}} new.xml"
        )

        # Remove zip files
        ssh.exec_command(f"rm -f {remote_old_zip} {remote_new_zip}")

        time.sleep(2)
        print("🟢 Unzip + rename completed (old.xml & new.xml)")


        # ============================================================
        # STEP 5 → RUN JAVA JAR
        # ============================================================
        java_cmd = f"java -jar /opt/jar/DataPlus_E_CM.jar {xml_path} {output_dir}"
        # java_cmd = f"java -jar /data/system/parser/DataPlus_E_CM.jar {xml_path} {output_dir}"
        stdin, stdout, stderr = ssh.exec_command(java_cmd)

        print(stdout.read().decode())
        print(stderr.read().decode())

        print("🟢 Java JAR executed")
        time.sleep(2)

    finally:
        ssh.close()

    # ============================================================
    # STEP 6–11 → MSSQL PROCEDURES & CSV EXPORT
    # ============================================================
    try:
        conn = pymssql.connect(
            server=mssql_host,
            user=mssql_user,
            password=mssql_pass,
            database=mssql_db,
            autocommit=True
        )
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")
        print("CONNECTED DB =", cursor.fetchone()[0])
        print("⚙ Running MSSQL procedures...")

        cursor.execute("EXEC clean_data")
        print("output_dir",output_dir)
        cursor.execute("EXEC load_csv %s, %s", ("Yes", output_dir))
        print("✅ clean_data & load_csv executed")
        try:
            cursor.execute("EXEC create_distname")
        except Exception as e:
            print("⚠ WARNING: create_distname failed — skipped")
            print(e)
        print("✅ create_distname executed")
        try:
            cursor.execute("EXEC data_compare 'old.xml','new.xml'")
        except Exception as e:
            print("⚠ WARNING: data_compare failed — skipped 1")
            print(e)
        try:
            cursor.execute("EXEC [dbo].[feature_comparison] 'old.xml','new.xml'")
        except Exception as e:
            print("⚠ WARNING: feature_comparison failed — skipped 2")
            print(e)
        conn.commit()

        # ============================================================
        # EXPORT CSV
        # ============================================================
        csv_output_path = os.path.join(os.getcwd(),"uploads/eric_compare/output/")
        os.makedirs(csv_output_path, exist_ok=True)
        print("📤 Exporting CSV files to:", csv_output_path)
        export_queries = {
            "Parameters.csv":
                "SELECT * FROM [dbo].[compare_output_formatted]",
            "Features.csv":
                "SELECT * FROM [set].feature_comparison_output",
            "Scripts.csv":
                "select * from [dbo].[compare_output_script]",
        }

        for file, query in export_queries.items():
            df = pd.read_sql(query, conn)
            print(f"📤 Exporting {file} with {len(df)} rows")
            df.to_csv(os.path.join(os.getcwd(), csv_output_path, file), index=False)
            print(f"📁 Saved: {file}")

        conn.close()

    except pymssql.ProgrammingError as e:
        error_msg = str(e).lower()

        if "invalid column name" in error_msg and "distname" in error_msg:
            print("⚠ WARNING: distname column missing — data_compare skipped")
        else:
            print("⚠ WARNING: data_compare failed — skipped 3")
            print(e)

    except Exception as e:
        raise Exception(f"❌ MSSQL ERROR: {str(e)}")

    # ============================================================
    # STEP 12 → CREATE FINAL EXCEL (2 SHEETS)
    # ============================================================

    output_path =  os.path.join(os.getcwd(),"uploads/eric_compare/output/")
    os.makedirs(output_path, exist_ok=True)

    final_excel_path = os.path.join(
        output_path,
        "eric_compare_result.xlsx"
    )

    df_param = pd.read_csv(os.path.join(output_path, "Parameters.csv"))
    df_feat = pd.read_csv(os.path.join(output_path, "Features.csv"))
    df_scripts = pd.read_csv(os.path.join(output_path, "Scripts.csv"))

    with pd.ExcelWriter(final_excel_path, engine="xlsxwriter") as writer:
        df_param.to_excel(writer, sheet_name="Parameters", index=False)
        df_feat.to_excel(writer, sheet_name="Features", index=False)
        df_scripts.to_excel(writer, sheet_name="Scripts", index=False)

    print("✅ Final Excel created:", final_excel_path)

    print("\n🎉 FULL ERIC COMPARE PROCESS COMPLETED SUCCESSFULLY\n")

    return final_excel_path



# # ============================================================
# # STEP 1 → OLD OUTPUT FILES DELETE
# # ============================================================
# ssh.exec_command(f"rm -rf {output_dir}*")
# time.sleep(1)

# # ============================================================
# # STEP 2 → OLD XML FILES DELETE
# # ============================================================
# ssh.exec_command(f"rm -rf {xml_path}*")
# time.sleep(1)

# ssh.exec_command(f"mkdir -p {xml_path}")
# ssh.exec_command(f"mkdir -p {output_dir}")
# time.sleep(1)

# # ============================================================
# # STEP 3 → AUTO-DETECT LATEST ZIP, UPLOAD, UNZIP
# # ============================================================
# zip_files = glob.glob(os.path.join(local_zip_folder, "*.zip"))

# if not zip_files:
#     print("❌ NO ZIP FILE FOUND!")
#     exit(1)

# latest_zip = max(zip_files, key=os.path.getmtime)
# print(f"🟢 Latest ZIP detected: {latest_zip}")

# remote_zip = f"{xml_path}input.zip"

# # Upload ZIP
# sftp = ssh.open_sftp()
# sftp.put(latest_zip, remote_zip)
# sftp.close()
# # print ("unzip -o {remote_zip} -d {xml_path}")
# # Unzip file
# stdin, stdout, stderr = ssh.exec_command(f"unzip -o {remote_zip} -d {xml_path}")
# ssh.exec_command(f"rm -f {remote_zip}")
# ssh.exec_command(f"rm -f {remote_zip}")
# print(stdout.read().decode())
# print(stderr.read().decode())
# print("🟢 Unzip completed.")
# time.sleep(2)



# # ============================================================
# # STEP 4 → RUN JAVA JAR
# # ============================================================
# java_cmd = f"java -jar /opt/jar/DataPlus_E_CM.jar {xml_path} {output_dir}"

# stdin, stdout, stderr = ssh.exec_command(java_cmd)
# print(stdout.read().decode())
# print(stderr.read().decode())
# print("🟢 Java JAR executed.")
# time.sleep(2)

# ssh.close()


# # ============================================================
# # STEP 6–11 → MSSQL PROCEDURES & EXPORT
# # ============================================================
# try:
#     conn = pymssql.connect(
#         server=mssql_host,
#         user=mssql_user,
#         password=mssql_pass,
#         database=mssql_db
#     )
#     cursor = conn.cursor()

#     print("⚙ Running MSSQL procedures...")

#     cursor.execute("EXEC clean_data")
#     cursor.execute("EXEC load_csv %s, %s", ("Yes", output_dir))
#     cursor.execute("EXEC create_distname")
#     cursor.execute("EXEC data_compare 'old.xml','new.xml'")
#     conn.commit()

#     # Export CSV
#     save_path = "/root/eric2_output"
#     os.makedirs(save_path, exist_ok=True)

#     export_queries = {
#         "Parameters.csv":
#             "SELECT * FROM [dbo].[compare_output_formatted]",

#         "Features.csv":
#             """
#             SELECT *
#             FROM  [set].feature_comparison_output
#             """
#     }

#     for file, query in export_queries.items():
#         df = pd.read_sql(query, conn)
#         df.to_csv(os.path.join(save_path, file), index=False)
#         print(f"📁 Saved:", file)

#     conn.close()
#     print("🎉 FULL PROCESS COMPLETED SUCCESSFULLY!")

# except Exception as e:
#     print("❌ MSSQL ERROR:", e)



