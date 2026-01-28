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

# data_path  = f"/data/mcom/airtel/eric/compare/{user}/"
data_path  = f"/ssd/mcom/airtel/eric/compare/{user}/"
xml_path   = f"{data_path}xml/"
output_dir = f"{data_path}output/"


local_zip_folder = "/root/ma/backend/code/uploads/eric_compare/"

# ================== MSSQL CONFIG ==================
mssql_host = os.environ.get("MSSQL_HOST")
mssql_user = os.environ.get("MSSQL_USER")
mssql_pass = os.environ.get("MSSQL_PASS")
mssql_db   = os.environ.get("MSSQL_DB")

# ================== SSH CONNECT ==================
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ssh_host, username=ssh_user, password=ssh_pass)


def upload_setting_to_mssql(setting_file_path: str):
    """
    Read setting XLSX / CSV having columns:
    - MO_Class
    - Compare
    Insert data into [set].[MO_Class]
    """

    print("\n============================")
    print("📄 Reading Setting File:", setting_file_path)
    print("============================\n")

    if not os.path.exists(setting_file_path):
        raise Exception("❌ Setting file not found")

    # ---------------- READ FILE ----------------
    try:
        if setting_file_path.lower().endswith(".csv"):
            df = pd.read_csv(setting_file_path)
        else:
            df = pd.read_excel(setting_file_path)
    except Exception as e:
        raise Exception(f"❌ Unable to read setting file: {str(e)}")

    if df.empty:
        raise Exception("❌ Setting file is empty")

    # ---------------- NORMALIZE COLUMN NAMES ----------------
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    print("🔍 Detected Columns:", df.columns.tolist())

    # ---------------- REQUIRED COLUMNS ----------------
    required_cols = ["mo_class", "compare"]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        raise Exception(f"❌ Missing required columns: {missing}")

    # ---------------- SAFE STRING CLEANER ----------------
    def clean_str(val):
        if val is None or pd.isna(val):
            return None
        if isinstance(val, str):
            v = val.strip()
            if v.lower() in ["", "nan", "none", "null", "-"]:
                return None
            return v
        return str(val)

    df = df.applymap(clean_str)
    df = df.where(pd.notnull(df), None)

    # ---------------- CONNECT MSSQL ----------------
    conn = pymssql.connect(
        server=mssql_host,
        user=mssql_user,
        password=mssql_pass,
        database=mssql_db
    )
    cursor = conn.cursor()

    try:
        print("🧹 Clearing old data from [set].[MO_Class] ...")
        cursor.execute("DELETE FROM [set].[MO_Class]")
        conn.commit()

        insert_sql = """
            INSERT INTO [set].[MO_Class]
            (MO_Class, Compare)
            VALUES (%s, %s)
        """

        inserted = 0
        skipped = 0

        for _, row in df.iterrows():
            mo_class = row.get("mo_class")
            compare_val = row.get("compare")

            # Mandatory check
            if not mo_class or not compare_val:
                skipped += 1
                continue

            cursor.execute(
                insert_sql,
                (
                    mo_class,
                    compare_val,
                )
            )
            inserted += 1

        conn.commit()

        print(f"✅ Inserted rows: {inserted}")
        print(f"⚠ Skipped rows: {skipped}")

    except Exception as e:
        conn.rollback()
        raise Exception(f"❌ MSSQL insert failed: {str(e)}")

    finally:
        conn.close()

    print("\n🎉 Setting upload completed successfully!\n")

    return {
        "inserted": inserted,
        "skipped": skipped
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
        ssh.exec_command(f"unzip -o {remote_old_zip} -d {xml_path}")
        ssh.exec_command(f"unzip -o {remote_new_zip} -d {xml_path}")
        ssh.exec_command(f"rm -f {remote_old_zip} {remote_new_zip}")
        time.sleep(2)

        print("🟢 Unzip completed")

        # ============================================================
        # STEP 5 → RUN JAVA JAR
        # ============================================================
        # java_cmd = f"java -jar /opt/jar/DataPlus_E_CM.jar {xml_path} {output_dir}"
        java_cmd = f"java -jar /data/system/parser/DataPlus_E_CM.jar {xml_path} {output_dir}"
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
            database=mssql_db
        )
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")
        print("CONNECTED DB =", cursor.fetchone()[0])
        print("⚙ Running MSSQL procedures...")

        cursor.execute("EXEC clean_data")
        print("output_dir",output_dir)
        cursor.execute("EXEC load_csv %s, %s", ("Yes", output_dir))
        cursor.execute("EXEC create_distname")
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

        export_queries = {
            "Parameters.csv":
                "SELECT * FROM [dbo].[compare_output_formatted]",
            "Features.csv":
                "SELECT * FROM [set].feature_comparison_output"
        }

        for file, query in export_queries.items():
            df = pd.read_sql(query, conn)
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

    with pd.ExcelWriter(final_excel_path, engine="xlsxwriter") as writer:
        df_param.to_excel(writer, sheet_name="Parameters", index=False)
        df_feat.to_excel(writer, sheet_name="Features", index=False)

    print("✅ Final Excel created:", final_excel_path)

    print("\n🎉 FULL ERIC COMPARE PROCESS COMPLETED SUCCESSFULLY\n")

    return final_excel_path

print("dsjgfjdsf",os.getcwd(),"/uploads/eric_compare/output/")

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



