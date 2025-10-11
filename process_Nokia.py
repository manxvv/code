import paramiko
import pymssql
import pandas as pd
import os
import time

# ================== Remote SSH Server (31.220.88.4) ==================
ssh_host = "31.220.88.4"
ssh_user = "root"
ssh_pass = "cf2DgN8vhM4d"

user = "sarfraz"
data_path = f"/data/web/{user}/"
xml_path = f"{data_path}xml/"
local_zip = "/root/ma/backend/code/xml.zip"  # Absolute path to local zip
remote_zip = f"{xml_path}files.zip"

local_script = "/root/ma/backend/code/process_Nokia.py"
remote_script = f"/root/process_Nokia.py"

# Output folder for CSV
output_path = os.path.join(data_path, "nokia")
os.makedirs(output_path, exist_ok=True)

# ================== MSSQL Config ==================
mssql_host = "31.220.88.4"
mssql_user = "sa"
mssql_pass = "Sarfraz@987"
mssql_db   = "MCOM_India"

# ================== SSH Connect ==================
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ssh_host, username=ssh_user, password=ssh_pass)

# ================== Step 0: Upload Python script ==================
sftp = ssh.open_sftp()
if not os.path.isfile(local_script):
    #print(f"Error: Local Python script {local_script} not found!")
    exit(1)
sftp.put(local_script, remote_script)
sftp.close()
#print(f"Uploaded Python script: {local_script} -> {remote_script}")

# ================== Step 1: Delete old folder ==================
ssh.exec_command(f"rm -rf {data_path}")
#print(f"Deleted old folder: {data_path}")
time.sleep(1)

# ================== Step 2: Create XML folder ==================
ssh.exec_command(f"mkdir -p {xml_path}")
#print(f"Created folder: {xml_path}")
time.sleep(1)

# ================== Step 3: Upload & unzip files ==================
if not os.path.isfile(local_zip):
    #print(f"Error: Local zip file {local_zip} not found!")
    exit(1)

sftp = ssh.open_sftp()
sftp.put(local_zip, remote_zip)
sftp.close()
#print(f"Uploaded zip: {local_zip} -> {remote_zip}")

stdin, stdout, stderr = ssh.exec_command(f"unzip -o {remote_zip} -d {xml_path}")
#print(stdout.read().decode())
#print(stderr.read().decode())
#print("Unzip completed ✅")
time.sleep(1)

# ================== Step 4: Run Java command ==================
stdin, stdout, stderr = ssh.exec_command(f"java -jar /var/opt/sarfraz/ncm.jar {xml_path} /var/opt/sarfraz/Nokia_CM.txt read 1")
#print("Running Java command...")
#print(stdout.read().decode())
#print(stderr.read().decode())
#print("Java process completed ✅")

# ================== Step 5: Run remote Python script (optional) ==================
stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_script}")
#print("Running remote Python script...")
#print(stdout.read().decode())
#print(stderr.read().decode())
#print("Remote Python script executed ✅")

ssh.close()

# ================== Step 6: MSSQL Stored Procedures + CSV Export ==================
try:
    conn = pymssql.connect(server=mssql_host, user=mssql_user, password=mssql_pass, database=mssql_db)
    cursor = conn.cursor()
    #print("Executing MSSQL stored procedures...")

    cursor.execute("exec [dbo].[clean_data]")
    cursor.execute(f"exec [dbo].[load_csv] '{data_path}output/'")
    cursor.execute("exec [dbo].[Conditional_defination_main] %s", (user,))
    cursor.execute("exec [dbo].[conditional_distname] %s", (user,))
    cursor.execute("exec [dbo].[paramter_audit] %s", (user,))
    conn.commit()

    # --- Export Query Results to CSV ---
    queries = {
        "Nokia_Parameters_Discrepancies.csv": "SELECT * FROM [ison].[Nokia_Parameters_Discrepancies]",
        "Nokia_Parameters.csv": "SELECT * FROM [set].[Nokia_Parameters]"
    }

    for filename, query in queries.items():
        df = pd.read_sql(query, conn)
        file_path = os.path.join(output_path, filename)
        df.to_csv(file_path, index=False)
        #print(f"Saved CSV: {file_path} ✅")

    conn.close()
    #print("All MSSQL data exported to CSV successfully! 🎉")
    #print("MSSQL procedures executed ✅")
except Exception as e:
    #print(f"Error connecting to MSSQL: {e}")

#print("All process completed successfully! 🎉")