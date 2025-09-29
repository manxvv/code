from flask import send_file,send_from_directory,Blueprint,url_for, request, jsonify, current_app
from app.database import mongo
from passlib.hash import bcrypt
import jwt
import traceback
from datetime import datetime, timedelta
from app.utils import token_required
from bson import ObjectId
import os
import uuid
from werkzeug.utils import secure_filename
# from app.parsinglogic import parse_text_to_excel,Calculator
from app.parsinglogicver import Calculator
import mimetypes
import pandas as pd

import pymongo
import threading

import os
import tempfile
import shutil
import zipfile
from typing import List
import sys

from app.nsa_sa.script_runner import scripting_nsa_sa
from app.gpl_audit.audit_test_runner import run_gpl_audit

cal = Calculator()

api = Blueprint("api", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_zip_from_files(file_paths: List[str], zip_filename: str) -> str:
    
    temp_dir = tempfile.mkdtemp()

    try:
        
        for file_path in file_paths:
            if os.path.isfile(file_path):
                shutil.copy(file_path, temp_dir)

        # 2. Create zip file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.basename(file_path)  # just filename inside zip
                    zipf.write(file_path, arcname)

        return zip_filename

    finally:
        # 3. Clean up
        shutil.rmtree(temp_dir)



def create_zip_from_folder(folder_path: str, zip_filename: str) -> str:
    """
    Creates a zip file from a folder (including all subfolders and files).
    
    Args:
        folder_path (str): Path of the folder to zip.
        zip_filename (str): Path of the output zip file.
        
    Returns:
        str: Path of the created zip file.
    """
    # Ensure folder exists
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")

    # Create a temporary directory (optional, can copy if needed)
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Copy entire folder structure into temp dir (optional)
        temp_folder_path = os.path.join(temp_dir, os.path.basename(folder_path))
        shutil.copytree(folder_path, temp_folder_path)
        
        # Create zip
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create relative path inside zip
                    arcname = os.path.relpath(file_path, start=temp_folder_path)
                    zipf.write(file_path, arcname)
        
        return zip_filename
    finally:
        # Clean up temp folder
        shutil.rmtree(temp_dir)


@api.route("/register", methods=["POST"])
@token_required
def register():
    data = request.json
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    
    user_id = request.user.get("sub") 

    if not full_name or not email or not password:
        return jsonify({"error": "All fields (full_name, email, password) are required"}), 400

    if mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400

    hashed_pw = bcrypt.hash(password)
    
    user = {
        "full_name": full_name,
        "email": email,
        "hashed_password": hashed_pw,
        "role": "user",
        "created_ts":datetime.now().timestamp(),
        "created_by":user_id
    }

    mongo.db.users.insert_one(user)

    return jsonify({"message": "User created successfully"}), 201


@api.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # user_id = request.user.get("sub") 
    user = mongo.db.users.find_one({"email": email})
    if not user or not bcrypt.verify(password, user["hashed_password"]):
        
        login_details = {
            "created_ts":datetime.now().timestamp(),
            # "created_by":user_id,
            "email":email,
            "password":password,
            "status":"invalid"
        }

        mongo.db.login_status.insert_one(login_details)
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode(
        {
            "sub": str(user["_id"]),
            "role": user.get("role", "admin"),  
            "exp": datetime.utcnow() + timedelta(hours=6)
        },
        current_app.config["JWT_SECRET"],
        algorithm=current_app.config["JWT_ALGORITHM"]
    )

    login_details = {
        "created_ts":datetime.now().timestamp(),
        # "created_by":user_id,
        "email":email,
        "password":password,
        "status":"valid"
    }

    mongo.db.login_status.insert_one(login_details)
    return jsonify({
        "email": user["email"],
        "role": user.get("role", "admin"),
        "access_token": token
    })

@api.route("/", methods=["GET"])
def user111():
    return {"message": "Hello from Flask!"+"------------"+os.getenv("APP_NAME")+"-----------"+os.getenv("MONGO_DB")}


@api.route("/users", methods=["GET"])
@token_required
def get_users():
    users = mongo.db.users.find({"role": {"$ne": "admin"}})  
    
    user_list = []
    for user in users:
        user_list.append({
            "id": str(user["_id"]),
            "full_name": user.get("full_name"),
            "email": user.get("email"),
            "role": user.get("role", "user")  
        })

    return jsonify(user_list), 200


# @api.route("/upload", methods=["POST"])
# @token_required
# def upload_file():
#     if ("precheck" or "postcheck") not in request.files:
#         return jsonify({"message": "No file part"}), 400
    
    
#     precheckfile = request.files.getlist("precheck")
#     print(precheckfile!=0)
#     postcheckfile = request.files.getlist("postcheck")
#     print(len(postcheckfile) != 0 and len(precheckfile) != 0)
#     if (len(precheckfile) == 0 and len(postcheckfile) != 0) or (len(postcheckfile) == 0 and len(precheckfile) == 0):
#         return jsonify({"message": "No selected file"}), 400



#     print(postcheckfile,precheckfile,"filefilefilefile=>>>>>>filefilefilefile")
    
    
#     precheck_files = []
#     postcheck_files = []
    
#     org_file_pre = []
#     org_file_post = []
    
#     for oneprefile in precheckfile:
#         original_filename = secure_filename(oneprefile.filename)
#         unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
#         org_file_pre.append({
#             "original_filename":original_filename,
#             "unique_filename":unique_filename
#         })
#         file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"pre"), unique_filename)
#         oneprefile.save(file_path)
#         precheck_files.append(file_path)
        
#     for onepostfile in postcheckfile:
#         original_filename = secure_filename(onepostfile.filename)
#         unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
#         file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"post"), unique_filename)
#         onepostfile.save(file_path)
#         postcheck_files.append(file_path)
        
#         org_file_post.append({
#             "original_filename":original_filename,
#             "unique_filename":unique_filename
#         })
        
    
    
#     cal = Calculator()
#     prefiledata = cal.startCalc(precheck_files,"pre","","")
    
#     postfiledata = {}
    
#     if(len(postcheckfile) > 0):
#         postfiledata = cal.startCalc(postcheck_files,"post","","")
    
#     print(prefiledata,"prefiledataprefiledataprefiledata")
    
    
#     file_path_final = prefiledata["file_name_all"]
    
#     finer_name = prefiledata["file_all"]
    
    
#     if(len(postcheckfile) > 0):
#         postcheck = postfiledata["file_name_all"]
        
#         finer_name = postfiledata["file_all"]
    
#         # file_path_final = cal.startdiffCalc(post_files=postcheck,pre_files=file_path_final)
        
#         file_path_final = postcheck
        
    
    
#     print(file_path_final,"file_path_finalfile_path_finalfile_path_finalfile_path_final")
    
        
    
        
    
#     file_doc = {
#         "user_id": request.user.get("sub"),
#         "original_filename": finer_name,
#         "org_file_pre": org_file_pre,
#         "org_file_post": org_file_post,
#         "filename": unique_filename,
#         "precheck_files":", ".join(precheck_files),
#         "postcheck_files":", ".join(postcheck_files),
#         "prefiledata_nodes":", ".join(prefiledata["nodeIdList"]),
#         "postfiledata_nodes":", ".join(prefiledata["nodeIdList"]),
#         "path": file_path_final
#     }

#     result = mongo.db.files.insert_one(file_doc)
    
#     return jsonify({
#         "message": "File uploaded successfully",
#         "file_id": str(result.inserted_id),
#         "filename": unique_filename,
#         "parsed_excel_filename": file_path_final
#     }), 201




def db_update_migration(uid,task,tno, file_path, taskId):
    
    print(task, file_path, taskId,"task, pre_filetask, pre_filetask, pre_file")
    
    read_df = []
    sec_read_df = []
    if("scripting_completed" != task):
        read_df = pd.read_excel(file_path,sheet_name="NodeStatus")
        sec_read_df = pd.read_excel(file_path,sheet_name="NodeStatus")
        
    else:
        read_df_all = pd.read_excel(file_path,sheet_name="Site")
        read_df = read_df_all[read_df_all["log"] == True]
        sec_read_df = pd.read_excel(file_path,sheet_name="AMF")
    
    if("node" in read_df.columns):
        read_df["NodeId"] = read_df["node"]
        sec_read_df["NodeId"] = sec_read_df["node"]
    
    print(read_df["NodeId"].unique(),"read_dfread_dfread_df")
    
    node_id_df = read_df["NodeId"].dropna().unique()
    node_id_list = read_df["NodeId"].dropna().unique().tolist()
    
    
    final_status = {
        "node_id":"/".join(node_id_list),
        "taskId":taskId,
        "task":task,
        "tno":tno,
        "uid":uid,
        "ts":datetime.now().timestamp(),
    }
    mongo.db.status_log_node_bulk.insert_one(final_status)
    
    for i in node_id_df:
        
        
        final_status_updated_by = {
            "node_id":i,
            "taskId":taskId,
        }
        final_status = {
            "$set": {
                "node_id": i,
                "taskId": taskId,
                f"{task}_completed": task,
                f"{task}_completed_by": uid,
                f"{task}_completed_at": datetime.now().timestamp(),
                f"{task}tno": tno,
            },
            "$setOnInsert": {  # optional fields only when inserting first time
                "created_at": datetime.now().timestamp()
            }
        }

        # mongo.db.status_log_node.insert_one(final_status)
        # mongo.db.status_log_node.insert_one(final_status)
        mongo.db.status_log_node.update_one(final_status_updated_by, final_status, upsert=True)
    
    
    if("Unnamed: 3" in sec_read_df.columns):
        
        sec_read_df["ttmamf"] = sec_read_df["Unnamed: 3"]
        
    
    if("termPointToAmfId" in sec_read_df.columns):
        
        sec_read_df["ttmamf"] = sec_read_df["termPointToAmfId"]
        
    
    for i,one_data in sec_read_df.iterrows():
        if pd.to_numeric(pd.Series(one_data["ttmamf"]), errors="coerce").notna().iloc[0]:
            print(i, one_data["ttmamf"], "✅ number")
            
            
            # final_status = {
            #     "node_id":one_data["NodeId"],
            #     "taskId":taskId,
            #     "task":"Migration Completed",
            #     "tno":5
            # }
            # mongo.db.status_log_node.insert_one(final_status)
              
            
            final_status_updated_by = {
                "node_id":one_data["NodeId"],
                "taskId":taskId,
            }
            final_status = {
                 "$set": {
                    "node_id":one_data["NodeId"],
                    "taskId":taskId,
                    "migration_completed":"completed",
                    "migration_completed_by":uid,
                    "migration_completed_at":datetime.now().timestamp(),
                    "migration_"+"tno":5
                }
            }
            # mongo.db.status_log_node.insert_one(final_status)
            # mongo.db.status_log_node.insert_one(final_status)
            mongo.db.status_log_node.update_one(final_status_updated_by, final_status, upsert=True)
        
        else:
            print(i, one_data["ttmamf"], "❌ not number")

        
        
    return 'db_update_migration'

@api.route("/upload", methods=["POST"])
@token_required
def upload_file():
    
    uid = request.user.get("sub")
    if ("precheck" or "postcheck") not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    
    
    precheckfile = request.files.getlist("precheck")
    
    taskId = request.form.get("taskId")
    print(precheckfile!=0)
    postcheckfile = request.files.getlist("postcheck")
    print(len(postcheckfile) != 0 and len(precheckfile) != 0)
    if (len(precheckfile) == 0 and len(postcheckfile) != 0) or (len(postcheckfile) == 0 and len(precheckfile) == 0):
        return jsonify({"message": "No selected file"}), 400



    print(postcheckfile,precheckfile,"filefilefilefile=>>>>>>filefilefilefile")
    
    
    precheck_files = []
    postcheck_files = []
    
    org_file_pre = []
    org_file_post = []
    
    for oneprefile in precheckfile:
        original_filename = secure_filename(oneprefile.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        org_file_pre.append({
            "original_filename":original_filename,
            "unique_filename":unique_filename
        })
        file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"pre"), unique_filename)
        oneprefile.save(file_path)
        precheck_files.append(file_path)
        
    for onepostfile in postcheckfile:
        original_filename = secure_filename(onepostfile.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"post"), unique_filename)
        onepostfile.save(file_path)
        postcheck_files.append(file_path)
        
        org_file_post.append({
            "original_filename":original_filename,
            "unique_filename":unique_filename
        })
        
    
    
    
    
    
    print(postcheck_files,taskId,precheck_files)
    
    
    print("taskIdtaskId",taskId,"taskIdtaskId")
    
    
    
    
    
    one_task_data = mongo.db.enmfiles.find_one({"task_id":taskId})

    try:    
        print(one_task_data,"one_task_dataone_task_data")
        clc = Calculator()
        
        pre_file = ""
        post_file = ""
        if(len(precheck_files) > 0):
            pre_file=clc.start_parser(precheck_files,"Pre_",os.path.join(os.getcwd(),UPLOAD_FOLDER,"enm",one_task_data["filename"]))
            
        if(len(postcheck_files) > 0):
            post_file=clc.start_parser(postcheck_files,"Post_",os.path.join(os.getcwd(),UPLOAD_FOLDER,"enm",one_task_data["filename"]))
        # pre_file="post08_09_2025_01_56_16_cells_data_temp.xlsx"
        # pre_file="pre08_09_2025_02_03_56_cells_data_temp.xlsx"
        # post_file="post08_09_2025_02_04_01_cells_data_temp.xlsx"






        if(len(postcheck_files) > 0):
            clc.startdiffCalc(pre_file,post_file)

        
        if(len(precheck_files) > 0):
            clc.rearrangecol(pre_file)
            clc.coloring_formatting(pre_file)
            clc.re_arrange_node_status(pre_file)
            
            datafind = {
                "task_id":taskId
            }
            mongo.db.site_id_status.update_one(
                datafind,
                {
                    "$set": {
                        "status": "Pre Check Completed",
                        
                        "pre_ts":datetime.now().timestamp(),
                        "statusCtr":2,
                        "pre_updated":request.user.get("sub") 
                    }
                }
            )
            if(len(postcheck_files) == 0):
                db_update_migration(uid,"pre_check",2,pre_file,taskId)
        if(len(postcheck_files) > 0):
            clc.rearrangecol(post_file)
            clc.coloring_formatting(post_file)
            clc.re_arrange_node_status(post_file)
            datafind = {
                "task_id":taskId
            }
            mongo.db.site_id_status.update_one(
                datafind,
                {"$set": {
                    "status": "Post Check Completed",
                    "statusCtr":3,
                    "post_ts":datetime.now().timestamp(),
                    "post_updated":request.user.get("sub") 
                    }}
            )
            
            db_update_migration(uid,"post_check",4,post_file,taskId)
            
        
        
        
        
        
        
            # clc.re_arrange_node_status(post_file)
        
        
        
        
        tss  = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
            
        
        
        
        file_doc = {
            "user_id": request.user.get("sub"),
            "org_file_pre": org_file_pre,
            "org_file_post": org_file_post,
            "filename": unique_filename,
            "time_stamp":tss,
            "ts":datetime.now().timestamp(),
            "precheck_files":", ".join(precheck_files),
            "postcheck_files":", ".join(postcheck_files),
            "activity_type":"Post Check" if len(postcheck_files) > 0 else "Pre Check",
            # "prefiledata_nodes":", ".join(prefiledata["nodeIdList"]),
            # "postfiledata_nodes":", ".join(prefiledata["nodeIdList"]),
            "path": post_file if len(postcheck_files) > 0 else pre_file,
            "taskId":taskId
        }

        result = mongo.db.files.insert_one(file_doc)
        
        return jsonify({
            "message": "File uploaded successfully",
            "file_id": str(result.inserted_id),
            "filename": unique_filename,
            "parsed_excel_filename": post_file if len(postcheck_files) > 0 else pre_file
        }), 201

    except Exception as e:
        print(e,"eeeeeeeeeeeeeeeeeee")
        print(traceback.print_exc())
        return jsonify({"message": "Please check the file again"}), 400



@api.route("/dashboard", methods=["GET"])
@token_required
def dashboard():
    
    aggr = [
        {
            '$group': {
                '_id': {
                    'node_id': '$node_id', 
                    'taskId': '$taskId'
                }, 
                'pre_check_completed': {
                    '$sum': {
                        '$cond': [
                            {
                                '$ifNull': [
                                    '$pre_check_completed', False
                                ]
                            }, 1, 0
                        ]
                    }
                }, 
                'post_check_completed': {
                    '$sum': {
                        '$cond': [
                            {
                                '$ifNull': [
                                    '$post_check_completed', False
                                ]
                            }, 1, 0
                        ]
                    }
                }, 
                'scripting_completed_completed': {
                    '$sum': {
                        '$cond': [
                            {
                                '$ifNull': [
                                    '$scripting_completed_completed', False
                                ]
                            }, 1, 0
                        ]
                    }
                }, 
                'migration_completed': {
                    '$sum': {
                        '$cond': [
                            {
                                '$ifNull': [
                                    '$migration_completed', False
                                ]
                            }, 1, 0
                        ]
                    }
                }
            }
        }, {
            '$group': {
                '_id': '', 
                'migration_completed': {
                    '$sum': '$migration_completed'
                }, 
                'scripting_completed_completed': {
                    '$sum': '$scripting_completed_completed'
                }, 
                'post_check_completed': {
                    '$sum': '$scripting_completed_completed'
                }, 
                'pre_check_completed': {
                    '$sum': '$scripting_completed_completed'
                }, 
                'total': {
                    '$sum': 1
                }
            }
        }
    ]
    
    site_id_status_cursor = mongo.db.status_log_node.aggregate(aggr)
    site_id_status_len_cursor = mongo.db.site_id_status.find()
    
    

    counter = 0
    for i in site_id_status_len_cursor:
        counter += 1
    
    site_id_status_list = []
    for f in site_id_status_cursor:
        
        print(f)
        
        
        site_id_status_list.append(f)
    
    final = site_id_status_list[0] if len(site_id_status_list) else {}
    return jsonify({
        "site_id_status":final,
        "total_count":final["total"] if "total" in final else 0
    }), 200
    
    
@api.route("/uploadenm", methods=["POST"])
@token_required
def uploadenm_file():
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    print(request.files.get("file"))
    
    
    # enm_circle_cursor = mongo.db.enms.find({
    #     "user_id":request.user.get("sub")  
    # })
    enm_circle_cursor = mongo.db.enms.find()
    
    
    enm_circle_list = list(enm_circle_cursor)

    df = pd.DataFrame(enm_circle_list)
    
    print(df,"dfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdf")
    
    
    
    file = request.files.get("file")
    if not file:
        return jsonify({"message": "No selected file"}), 400


    original_filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_con = {
        "original_filename":original_filename,
        "unique_filename":unique_filename
    }
    file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"enm"), unique_filename)
    file.save(file_path)
    
    
    print(file_path,"file_pathfile_pathfile_path")
    read_df = pd.read_excel(file_path)
    
    read_df["Node"] = read_df['Node'].apply(str)
    
    
    fileNameList = []
    
    enmList = []
    
    if(len(df) == 0):
        return jsonify({"error": "Please add Circle & ENM in Admin."}), 400
    
    
    
    updf = df[["circle","enm"]]
    
    
    updf["merge_ce"] = updf["circle"]+"_cp_"+updf["enm"]
    
    read_df["merge_ce"] = read_df["circle"]+"_cp_"+read_df["ENM"]
    
    
    print(updf,read_df,"updfupdfupdfupdfupdf")
    read_df_enmmm = set(read_df["merge_ce"].unique())
    
    print(read_df_enmmm,"read_df_enmmmread_df_enmmmread_df_enmmm")
    
    if(len(read_df_enmmm) > 1): 
        return jsonify({"error": "Multiple combination of ENM & Circle Exist "}), 400
    unique_enm = set(updf["merge_ce"].unique())

    # Find which subset ENMs are missing
    missing_enms = [enm for enm in read_df_enmmm if enm not in unique_enm]

    print("Missing ENMs:", missing_enms)


    if(len(missing_enms) > 0):
        final_enn = ""
        for oneenm in missing_enms:
            final_enn=final_enn+" Circle - "+oneenm.split("_cp_")[0]+" & "+"ENM - "+oneenm.split("_cp_")[1]+", "
        return jsonify({"error": final_enn + " is missing "}), 400
    
    
    for node, group in read_df.groupby("ENM"):
        
        
        print(node,group,"node,groupnode,group")
        
        enmList.append(node)
        
        nodes_list = group["Node"].to_list()
    
    
    
    
    
        
        file_text_content = """NodeStatus

cmedit get NodeId1;NodeId2
CmFunction.(syncStatus);
NRSectorCarrier.(arfcnDL,arfcnUL,bSChannelBwDL,bSChannelBwUL,configuredMaxTxPower,operationalState);
NRCellDU.(administrativeState,cellState,operationalState,serviceState,ssbDuration,ssbFrequency,ssbOffset,ssbPeriodicity);
EUtranCellTDD.(administrativeState,cellSubscriptionCapacity,channelBandwidth,earfcn,operationalState);
EUtranCellFDD.(administrativeState,dlChannelBandwidth,earfcndl,earfcnul,operationalState,ulChannelBandwidth);
SectorCarrier.(SectorCarrierId,configuredMaxTxPower,operationalState,reservedBy,rfBranchRxRef,rfBranchTxRef);
SectorEquipmentFunction.(administrativeState,operationalState,availableHwOutputPower,reservedBy,rfBranchRef);
FieldReplaceableUnit.(administrativeState,operationalState,productData);
TermPointToAmf.(administrativeState,operationalState,defaultAmf,ipv4Address1,ipv4Address2,ipv6Address1,ipv6Address2,usedIpAddress) --list


NodeAlarms

alarm get NodeId1;NodeId2 --list

ScriptLogs

cmedit get NodeId1;NodeId2
TermPointToAmf.(termPointToAmfId,administrativeState,defaultAmf,pwsRestartHandling,ipv6Address1,ipv6Address2,ipv4Address1,ipv4Address2);SystemFunctions.<w>;Lm.<w>;FeatureState.(description,featureState,featureStateId,licenseState,serviceState);CmFunction.(syncStatus);ManagedElement.<w>;AnrFunction.<w>;AnrFunctionNR.<w>;AnrFunctionNRUeCfg.<w>;AnrFunctionEUtran.<w>;AnrFunctionEUtranUeCfg.<w>;Transport.<w>;SctpProfile.<w>;Sctp.<w>;SctpEndpoint.<w>;AddressIPv4.<w>;AddressIPv6.<w>;EndpointResource.<w>;LocalSctpEndpoint.<w>;LocalIpEndpoint.<w>;GNBDUFunction.<w>;NRCellDU.<w>;NRSectorCarrier.<w>;DU5qiTable.<w>;DU5qi.<w>;Paging.<w>;Rrc.<w>;RadioBearerTable.<w>;SignalingRadioBearer.<w>;BWP.<w>;BWPSet.<w>;DynPowerOpt.<w>;BWPSetUeCfg.<w>;BWPSetCfg.<w>;UeCC.<w>;UeBb.<w>;UeBbProfile.<w>;UeBbProfileUeCfg.<w>;Rach.<w>;RachUeCfg.<w>;RadioLinkControl.<w>;DrbRlc.<w>;DrbRlcUeCfg.<w>;UeAdaptiveRlc.<w>;UeAdaptiveRlcUeCfg.<w>;QosPriorityMapping.<w>;PriorityDomainMapping.<w>;DrxProfile.<w>;DrxProfileUeCfg.<w>;PuschRepRel16Drx.<w>;GNBCUCPFunction.<w>;NRCellCU.<w>;EmCall.<w>;SecurityHandling.<w>;CUCP5qiTable.<w>;CUCP5qi.<w>;NRNetwork.<w>;NRFrequency.<w>;NRFreqRelation.<w>;EUtraNetwork.<w>;EUtranFrequency.<w>;EUtranFreqRelation.<w>;NRCellRelation.<w>;Mcpc.<w>;McpcPCellEUtranFreqRelProfile.<w>;McpcPCellEUtranFreqRelProfileUeCfg.<w>;McpcPCellProfile.<w>;McpcPCellProfileUeCfg.<w>;UeCC.<w>;InactivityProfile.<w>;InactivityProfileUeCfg.<w>;SrHandling.<w>;SrHandlingUeCfg.<w>;DrbRlc.<w>;DrbRlcUeCfg.<w>;UserPlaneProfile.<w>;UserPlaneProfileUeCfg.<w>;RrcInactiveProfile.<w>;RrcInactiveProfileUeCfg.<w>;Rohc.<w>;RohcUeCfg.<w>;Mcfb.<w>;McfbCellProfile.<w>;McfbCellProfileUeCfg.<w>;TrafficSteering.<w>;TrStPSCellNrFreqRelProfile.<w>;TrStPSCellNrFreqRelProfileUeCfg.<w>;TrStPSCellProfile.<w>;TrStPSCellProfileUeCfg.<w>;TrStSaCellProfile.<w>;TrStSaCellProfileUeCfg.<w>;TrStSaEUtranFreqRelProfile.<w>;TrStSaEUtranFreqRelProfileUeCfg.<w>;TrStSaNrFreqRelProfile.<w>;TrStSaNrFreqRelProfileUeCfg.<w>;UeMC.<w>;UeMCNrFreqRelProfile.<w>;UeMCNrFreqRelProfileUeCfg.<w>;UeMCCellProfile.<w>;UeMCCellProfileUeCfg.<w>;UeMCEUtranFreqRelProfile.<w>;UeMCEUtranFreqRelProfileUeCfg.<w>;UeCovMeas.<w>;UcmCellProfile.<w>;UcmCellProfileUeCfg.<w>;UcmNrFreqRelProfile.<w>;UeGroupSelection.<w>;PrefUeGroupSelectionProfile.<w>;UeAdmissionGroupDefinition.<w>;UeGroupSelectionProfile.<w>;UeMobilityGroupDefinition.<w>;UeServiceGroupDefinition.<w>;GNBCUUPFunction.<w>;CUUP5qiTable.<w>;CUUP5qi.<w>;UeCC.<w>;DcDlCfg.<w>;GtpuSupervision.<w>;GtpuSupervisionProfile.<w>;ENodeBFunction.<w>;UePolicyOptimization.<w>;EUtranCellFDD.<w>;EUtranCellTDD.<w>;UeMeasControl.<w>;ReportConfigB1NR.<w>;GUtranSyncSignalFrequency.<w>;GUtranFreqRelation.<w>;GUtranCellRelation.<w> --dynamic

"""
        
        
        

        print(nodes_list,"; ".join(nodes_list),"nodes_listnodes_listnodes_list")
        final_text = file_text_content.replace("NodeId1;NodeId2",";".join(nodes_list)+" ")
        
        print(final_text,"final_textfinal_textfinal_text")
        
        # ffnme = os.path.join("downloads",node+"_Command_"+datetime.now().strftime("%d_%m_%Y_%H_%M_%S")+"_"+uuid.uuid4().hex+ ".txt")
        ffnme = os.path.join("downloads",node+"_Command_"+datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + ".txt")
            
        with open(os.path.join(os.getcwd(),ffnme),"w+") as file:
            
            file.write(final_text)
    
    
        fileNameList.append(ffnme)
        
    print(read_df,"read_dfread_dfread_df")
    circle_list = read_df["circle"].unique().tolist()
    enm_list = read_df["ENM"].unique().tolist()
    SiteID_list = read_df["SiteID"].unique().tolist()
    Node_list = read_df["Node"].unique().tolist()
    
    
    one_last_data = mongo.db.enmfiles.find_one(sort=[('_id', -1)])

    task_id = "DY000001"

    if(one_last_data):
        last_task = one_last_data["task_id"].replace("DY","")
        
        new_id = int(last_task)+1
        
        
        str_new_id = len(str(new_id))
        
        task_id = "DY"+(6-str_new_id)*"0"+str(new_id)
        
        
        print(task_id)
        

    
    print(one_last_data,"one_last_dataone_last_dataone_last_data")
    
    
    file_doc = {
        "datetime":datetime.now().timestamp(),
        "datetime_stamp":datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "user_id": request.user.get("sub"),
        "original_filename": original_filename,
        "filename": unique_filename,
        "enm_file_name": ",".join(fileNameList),
        "enms": "/".join(enm_list),
        "circle":"/".join(circle_list),
        "site_id":"/".join(SiteID_list),
        "nodes":"/".join(Node_list),
        "task_id":task_id,
        "updated":request.user.get("sub") 
    }
    
    
    
    task_file_doc={
        "enm_updated":request.user.get("sub"),
        "enm_ts":datetime.now().timestamp(),
        "task_id":task_id,
        
        "status":"ENM Command Executed",
        "statusCtr":1
    }
    
    
    
    
    
    result = mongo.db.site_id_status.insert_one(task_file_doc)

    result = mongo.db.enmfiles.insert_one(file_doc)
    
    
    for index, oneValDf in read_df.iterrows():
        print(oneValDf["ENM"],"sajdsakdaskjdsak")
        final_data = {
            "enms": oneValDf["ENM"],
            "circle":oneValDf["circle"],
            "site_id":oneValDf["SiteID"],
            "nodes":oneValDf["Node"],
            "task_id":task_id,
            "ts":datetime.now().timestamp(),
            "pre_updated":request.user.get("sub") 
        }
        mongo.db.migration.insert_one({**final_data,"status":"Pending"})
    
    return jsonify({
        "message": "File uploaded successfully",
        "file_id": str(result.inserted_id),
        "filename": unique_filename,
        "enm_file_name": ffnme
    }), 201
    
    
    
def script_entry_migration(request,taskId,file_con,file_path):
    
    
    df = pd.read_excel(file_path,sheet_name=None)
    print(file_path,df,"file_pathfile_pathfile_pathfile_path")
    
    print(df["Site"])
    
    unique_circle = df["Site"]["circle"].unique()
    unique_enm = df["Site"]["enm"].unique()
    SiteID_list = df["Site"]["siteid"].unique().tolist()
    Node_list = df["Site"]["node"].unique().tolist()
    
    datafind = {
        "enms": "/".join(unique_enm),
        "circle":"/".join(unique_circle),
        "site_id":"/".join(SiteID_list),
        "nodes":"/".join(Node_list),
        "ts":datetime.now().timestamp(),
        "updated":request.user.get("sub") 
    }
    
    
    final_data = {**file_con,**datafind}
    
    mongo.db.scripting.insert_one(
        final_data
    )
    
    mongo.db.migration.update_one(
        datafind,
        {"$set": {"status": "Done"}}
    )
    
    

def process_scripting_task(task_data, eFile_original_filename, eFile_file_path, siteList_file_path, curr_dir, uid):
    try:
        nsa_sa_path = os.path.join(os.getcwd(), "app", "nsa_sa")
        sys.path.append(nsa_sa_path)

        nsa_op_folder = scripting_nsa_sa(
            task_data["original_filename"],
            eFile_original_filename,
            nsa_sa_path,
            task_data["circle"],
            task_data["enms"],
            os.path.join(curr_dir, siteList_file_path),
            os.path.join(curr_dir, eFile_file_path),
            curr_dir
        )

        list_dirr = os.listdir(nsa_op_folder)
        excel_file = ""
        script_file = ""
        for i in list_dirr:
            if "Script_Status" in i:
                excel_file = i
                script_file = i

        shutil.make_archive(nsa_op_folder, 'zip', nsa_op_folder)

        file_con = {
            "siteList_original_filename": task_data["original_filename"],
            "siteList_unique_filename": task_data["filename"],
            "eFile_original_filename": eFile_original_filename,
            "eFile_unique_filename": os.path.basename(eFile_file_path),
            "nsa_op_folder": nsa_op_folder.replace(os.getcwd(), "") + ".zip",
            "taskId": task_data["task_id"]
        }

        script_entry_migration(None, task_data["task_id"], file_con, os.path.join(nsa_op_folder, excel_file))

        mongo.db.site_id_status.update_one(
            {"task_id": task_data["task_id"]},
            {"$set": {
                "status": "Scripting Completed",
                "statusCtr": 4,
                "scripting_ts": datetime.now().timestamp(),
                "scripting_updated": uid
            }}
        )

        db_update_migration(uid, "scripting_completed", 3, os.path.join(nsa_op_folder, script_file), task_data["task_id"])
    
    except Exception as e:
        print("Error in background task:", str(e))

    
    
    
    
@api.route("/uploadScripting", methods=["POST"])
@token_required
def uploadScripting_file():
    
    uid = request.user.get("sub")
    if "eFile" not in request.files and not "siteList" in request.files:
        return jsonify({"message": "No file part"}), 400
    
    eFile = request.files.get("eFile")
    if not eFile:
        return jsonify({"message": "No selected eFile file"}), 400


    # siteList = request.files.get("siteList")
    # if not siteList:
    #     return jsonify({"message": "No selected siteList file"}), 400


    # siteList_original_filename = secure_filename(siteList.filename)
    eFile_original_filename = secure_filename(eFile.filename)
    # siteList_unique_filename = f"{uuid.uuid4().hex}_{siteList_original_filename}"
    eFile_unique_filename = f"{uuid.uuid4().hex}_{eFile_original_filename}"
    
    
    curr_dir = os.getcwd()
    
    
    # circle_name = request.form.get('circle')
    # enm_name = request.form.get('enm')
    taskId = request.form.get('taskId')
    
    
    
    one_task_data = mongo.db.enmfiles.find_one({"task_id":taskId})
    
    print(one_task_data["filename"],"one_task_dataone_task_dataone_task_data")
    
    siteList_file_path = os.path.join(UPLOAD_FOLDER,"enm",one_task_data["filename"])
    
    # siteList_file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"scripting_sites"), siteList_unique_filename)
    # siteList.save(siteList_file_path)
    eFile_file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"scripting_enm"), eFile_unique_filename)
    eFile.save(eFile_file_path)
    
    
    
    
    threading.Thread(
        target=process_scripting_task,
        args=(one_task_data, eFile_original_filename, eFile_file_path, siteList_file_path, curr_dir, uid),
        daemon=True
    ).start()

    return jsonify({"message": "File uploaded successfully, processing started in background"}), 201

    
    
    nsa_sa_path = os.path.join(os.getcwd(),"app","nsa_sa")
    
    sys.path.append(nsa_sa_path)
    
    print(sys.path,"sys.pathsys.pathsys.pathsys.path")
    
    nsa_op_folder = scripting_nsa_sa(one_task_data["original_filename"],eFile_original_filename,nsa_sa_path,one_task_data["circle"],one_task_data["enms"],os.path.join(curr_dir,siteList_file_path),os.path.join(curr_dir,eFile_file_path),curr_dir)

    list_dirr = os.listdir(nsa_op_folder)
    
    excel_file = ""
    
    

    shutil.make_archive(nsa_op_folder, 'zip', nsa_op_folder)
    
    script_file = ""
    for i in list_dirr:
        if("Script_Status" in i):
            excel_file = i
            
        if("Script_Status" in i):
            script_file = i
        
            
    
    file_con = {
        "siteList_original_filename":one_task_data["original_filename"],
        "siteList_unique_filename":one_task_data["filename"],
        "eFile_original_filename":eFile_original_filename,
        "eFile_unique_filename":eFile_unique_filename,
        "nsa_op_folder":nsa_op_folder.replace(os.getcwd(),"")+".zip",
        "taskId":taskId
    }
    script_entry_migration(request,taskId,file_con,os.path.join(nsa_op_folder,excel_file))
    
    
    datafind = {
        "task_id":taskId
    }
    mongo.db.site_id_status.update_one(
        datafind,
        {"$set": {
            "status": "Scripting Completed",
            "statusCtr":4,
            "scripting_ts":datetime.now().timestamp(),
            "scripting_updated":request.user.get("sub") 
            }}
    )
    
    
    
    
    db_update_migration(uid,"scripting_completed",3,os.path.join(nsa_op_folder,script_file),taskId)
    
    # with zipfile.ZipFile(nsa_op_folder+".zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
    #     for root, _, files in os.walk(nsa_op_folder):
    #         print(file,"filefilefile")
    #         for file in files:
                
    #             print(file,"filefilefile")
    #         deoijejdi3e
                
    #             # file_path = os.path.join(root, file)
    #             # arcname = os.path.basename(file_path)  # just filename inside zip
    #             # zipf.write(file_path, arcname)

    # print(os.path.abspath(nsa_op_folder),"abspathabspathabspath")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    return jsonify({
        "message": "File uploaded successfully"
    }), 201
    
    
    
@api.route("/user-files", methods=["GET"])
@token_required
def get_user_files():
    user_id = request.user.get("sub")  
    
    
    aggr = [
        {
            '$addFields': {
                'user_id_obj': {
                    '$convert': {
                        'input': '$user_id', 
                        'to': 'objectId'
                    }
                }, 
                'uID': {
                    '$convert': {
                        'input': '$_id', 
                        'to': 'string'
                    }
                }
            }
        }, {
            '$lookup': {
                'from': 'users', 
                'localField': 'user_id_obj', 
                'foreignField': '_id', 
                'as': 'userresult'
            }
        }, {
            '$unwind': {
                'path': '$userresult', 
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$lookup': {
                'from': 'enmfiles', 
                'localField': 'taskId', 
                'foreignField': 'task_id', 
                'as': 'taskIdresult'
            }
        }, {
            '$unwind': {
                'path': '$taskIdresult', 
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$sort': {
                '_id': -1
            }
        },{
            '$project': {
                'user_id_obj': 0, 
                'userresult.hashed_password': 0, 
                'userresult._id': 0, 
                '_id': 0, 
                'taskIdresult._id': 0
            }
        }
    ]

    # files_cursor = mongo.db.files.find({"user_id": user_id})
    files_cursor = mongo.db.files.aggregate(aggr)
    
    
    files_list = []
    for f in files_cursor:
        
        print(f)
        
        
        files_list.append(f)
    
    return jsonify(files_list), 200




@api.route("/user-enm-files", methods=["GET"])
@token_required
def get_user_enm_files():
    user_id = request.user.get("sub")  
    
    
    aggr = [
        {
            '$addFields': {
                'user_id_obj': {
                    '$convert': {
                        'input': '$user_id', 
                        'to': 'objectId'
                    }
                }, 
                'uID': {
                    '$convert': {
                        'input': '$_id', 
                        'to': 'string'
                    }
                }
            }
        }, {
            '$lookup': {
                'from': 'users', 
                'localField': 'user_id_obj', 
                'foreignField': '_id', 
                'as': 'userresult'
            }
        }, {
            '$unwind': {
                'path': '$userresult', 
                'preserveNullAndEmptyArrays': True
            }
        },{
            '$sort': {
                '_id': -1
            }
        }, {
            '$project': {
                'user_id_obj': 0, 
                'userresult.hashed_password': 0, 
                'userresult._id': 0, 
                '_id': 0
            }
        }
    ]

    # files_cursor = mongo.db.files.find({"user_id": user_id})
    files_cursor = mongo.db.enmfiles.aggregate(aggr)
    
    
    
    files_list = []
    for f in files_cursor:
        
        print(f)
        
        
        files_list.append(f)
    
    return jsonify(files_list), 200





@api.route("/user-scripting-files", methods=["GET"])
@token_required
def get_user_scripting_files():
    user_id = request.user.get("sub")  
    
    
    aggr = [
        {
            '$addFields': {
                'user_id_obj': {
                    '$convert': {
                        'input': '$user_id', 
                        'to': 'objectId'
                    }
                }, 
                'uID': {
                    '$convert': {
                        'input': '$_id', 
                        'to': 'string'
                    }
                }
            }
        }, {
            '$lookup': {
                'from': 'users', 
                'localField': 'user_id_obj', 
                'foreignField': '_id', 
                'as': 'userresult'
            }
        }, {
            '$unwind': {
                'path': '$userresult', 
                'preserveNullAndEmptyArrays': True
            }
        },{
            '$sort': {
                '_id': -1
            }
        }, {
            '$project': {
                'user_id_obj': 0, 
                'userresult.hashed_password': 0, 
                'userresult._id': 0, 
                '_id': 0
            }
        }
    ]

    # files_cursor = mongo.db.files.find({"user_id": user_id})
    files_cursor = mongo.db.scripting.aggregate(aggr)
    
    
    
    files_list = []
    for f in files_cursor:
        
        print(f)
        
        
        files_list.append(f)
    
    return jsonify(files_list), 200

@api.route("/migrationList", methods=["GET"])
@token_required
def migrationList():
    user_id = request.user.get("sub")  
    
    
    # aggr = [
    #     {
    #         '$lookup': {
    #             'from': 'status_log_node', 
    #             'let': {
    #                 'node': '$nodes', 
    #                 'task': '$task_id'
    #             }, 
    #             'pipeline': [
    #                 {
    #                     '$match': {
    #                         '$expr': {
    #                             '$and': [
    #                                 {
    #                                     '$eq': [
    #                                         '$node_id', '$$node'
    #                                     ]
    #                                 }, {
    #                                     '$eq': [
    #                                         '$taskId', '$$task'
    #                                     ]
    #                                 }
    #                             ]
    #                         }
    #                     }
    #                 }, {
    #                     '$project': {
    #                         '_id': 0, 
    #                         'task': 1
    #                     }
    #                 }
    #             ], 
    #             'as': 'statusList'
    #         }
    #     }, {
    #         '$group': {
    #             '_id': {
    #                 'node_id': '$nodes', 
    #                 'taskId': '$task_id'
    #             }, 
    #             'statuses': {
    #                 '$addToSet': '$statusList.task'
    #             }, 
    #             'task_id': {
    #                 '$first': '$task_id'
    #             }, 
    #             'enms': {
    #                 '$first': '$enms'
    #             }, 
    #             'circle': {
    #                 '$first': '$circle'
    #             }, 
    #             'site_id': {
    #                 '$first': '$site_id'
    #             }, 
    #             'nodes': {
    #                 '$first': '$nodes'
    #             }
    #         }
    #     }, {
    #         '$unwind': {
    #             'path': '$statuses', 
    #             'preserveNullAndEmptyArrays': True
    #         }
    #     }
    # ]
    
    
    aggr = [
        {
            '$lookup': {
                'from': 'status_log_node', 
                'let': {
                    'node': '$nodes', 
                    'task': '$task_id'
                }, 
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$and': [
                                    {
                                        '$eq': [
                                            '$node_id', '$$node'
                                        ]
                                    }, {
                                        '$eq': [
                                            '$taskId', '$$task'
                                        ]
                                    }
                                ]
                            }
                        }
                    }, {
                        '$project': {
                            '_id': 0
                        }
                    }
                ], 
                'as': 'statusList'
            }
        }, {
            '$unwind': {
                'path': '$statusList', 
                'preserveNullAndEmptyArrays': True
            }
        },{
            '$sort': {
                '_id': -1
            }
        }
    ]

    # files_cursor = mongo.db.files.find({"user_id": user_id})
    files_cursor = mongo.db.migration.aggregate(aggr)
    
    
    files_list = []
    for f in files_cursor:
        
        print(f)
        
        
        files_list.append(f)
    
    return jsonify(files_list), 200

@api.route("/downloads/<file_id>", methods=["GET"])
@token_required
def download_file(file_id):
    # file_doc = mongo.db.files.find_one({"_id": ObjectId(file_id)})

    # if not file_doc or file_doc["user_id"] != request.user.get("sub"):
    #     return jsonify({"message": "File not found"}), 404

    # if file_doc.get("parsed_excel_path") and os.path.exists(file_doc["parsed_excel_path"]):
    #     file_path = file_doc["parsed_excel_path"]
    #     # download_name = file_doc.get("parsed_excel_filename", "parsed.xlsx")
    #     # content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    # else:
    #     file_path = os.path.join(os.getcwd(),file_doc["path"])
    #     download_name = file_doc["original_filename"]
    #     content_type = mimetypes.guess_type(file_path)

    
    # print(download_name,"download_namedownload_namedownload_name")
    final_file = os.path.join(os.getcwd(),"downloads",file_id)
    content_type = mimetypes.guess_type(final_file)
    
    print(content_type,"content_typecontent_type")
    return send_file(
        final_file,
        as_attachment=True
    )
    
    
     
    
    return send_from_directory("downloads", download_name, as_attachment=True)





@api.route("/downloads/nsa_sa/<file_id>", methods=["GET"])
@token_required
def download_file_nsa_sa(file_id):
    
    final_file = os.path.join(os.getcwd(),"downloads","nsa_sa",file_id)
    content_type = mimetypes.guess_type(final_file)
    
    print(content_type,"content_typecontent_type")
    return send_file(
        final_file,
        as_attachment=True
    )
    

@api.route("/downloads/gpl_audit/<file_id>", methods=["GET"])
@token_required
def download_file_gpl_audit(file_id):
    
    final_file = os.path.join(os.getcwd(),"downloads","gpl_audit",file_id)
    content_type = mimetypes.guess_type(final_file)
    
    print(content_type,"content_typecontent_type")
    return send_file(
        final_file,
        as_attachment=True
    )

@api.route("/enm_downloads/<file_id>", methods=["GET"])
# @token_required
def enm_download_file(file_id):
    
    
    print(file_id,"file_idfile_idfile_id")
    
    enm_listt = mongo.db.enmfiles.find_one({
        "_id": ObjectId(file_id)
    })
    
    print(enm_listt["enm_file_name"],"enm_listtenm_listtenm_listt")
    
    enm_zip_file = []
    for enmfilei in enm_listt["enm_file_name"].split(","):
        
        enm_zip_file.append(os.path.join(os.getcwd(),enmfilei))
        
    if(len(enm_zip_file) == 1):
        print(enm_zip_file)
        
        return send_file(
            enm_zip_file[0],
            as_attachment=True
        )
    

    zip_path = create_zip_from_files(enm_zip_file, os.path.join("downloads","enm_output.zip"))
    print("ZIP created at:", zip_path)
    return send_file(
        zip_path,
        as_attachment=True
    ) 

@api.route("/circles", methods=["POST"])
@token_required
def create_circle():
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"message": "Invalid input, 'name' is required"}), 400

    circle = {
        "user_id": request.user.get("sub"),
        "name": data["name"],
        "ts":datetime.now().timestamp(),
        "updated":request.user.get("sub") 
    }

    result = mongo.db.circles.insert_one(circle)

    return jsonify({
        "message": "Circle created successfully",
        "id": str(result.inserted_id),
        "circle": circle
    }), 201




@api.route("/enms", methods=["POST"])
@token_required
def create_enm():
    data = request.get_json()

    vendor = data.get("vendor")
    vendor = data["vendor"].strip().lower()  # Normalize to lowercase
    # Conditional validation based on vendor
    if vendor == "ericsson":
        if not data or "enm" not in data or "circle" not in data:
            return jsonify({"message": "Invalid input, 'ENM' and 'Circle' are required for Ericsson"}), 400
    elif vendor == "nokia":
        if not data or "circle" not in data:
            return jsonify({"message": "Invalid input, 'Circle' is required for Nokia"}), 400
    else:
        return jsonify({"message": "Invalid vendor"}), 400

    # Check if combination already exists
    query = {"circle": data["circle"]}
    if vendor == "ericsson":
        query["enm"] = data["enm"]

    existing = mongo.db.enms.find_one(query)
    if existing:
        return jsonify({"message": f"ENM with this combination already exists for {vendor}"}), 400

    enm_record = {
        "user_id": request.user.get("sub"),
        "vendor": vendor,
        "circle": data["circle"],
        "ts": datetime.now().timestamp(),
        "updated": request.user.get("sub")
    }

    # Include ENM only if vendor is Ericsson
    if vendor == "ericsson":
        enm_record["enm"] = data["enm"]

    result = mongo.db.enms.insert_one(enm_record)

    print(enm_record, "enmenmenm")
    return jsonify({
        "message": "ENM created successfully",
        "id": str(result.inserted_id)
    }), 201
    
    

@api.route("/users", methods=["POST"])
@token_required
def create_users():
    data = request.get_json()

    # Validate required fields
    if not data or "email" not in data or "full_name" not in data or "password" not in data:
        return jsonify({"message": "Invalid input, All fiels are required"}), 400

    # Check if the combination already exists
    existing = mongo.db.enms.find_one({"email": data["email"]})
    if existing:
        return jsonify({"message": "Email already exists"}), 400

    enm = {
        "user_id": request.user.get("sub"),
        "enm": data["enm"],
        "ts":datetime.now().timestamp(),
        "circle": data["circle"],
        "updated":request.user.get("sub") 
    }

    result = mongo.db.enms.insert_one(enm)

    print(enm,"enmenmenm")
    return jsonify({
        "message": "ENM created successfully",
        "id": str(result.inserted_id)
    }), 201
    
@api.route("/enms/<enm_id>", methods=["DELETE"])
@token_required
def delete_enm(enm_id):
    try:
        enm = mongo.db.enms.find_one({
            "_id": ObjectId(enm_id),
            "user_id": request.user.get("sub")
        })

        if not enm:
            return jsonify({"message": "ENM not found"}), 404

        mongo.db.enms.delete_one({"_id": ObjectId(enm_id)})

        return jsonify({"message": "ENM deleted successfully"}), 200

    except Exception as e:
        return jsonify({"message": "Error deleting ENM", "error": str(e)}), 500



@api.route("/users/<user_id>", methods=["DELETE"])
@token_required
def delete_user(user_id):
    try:
        enm = mongo.db.users.find_one({
            "_id": ObjectId(user_id)
        })

        if not enm:
            return jsonify({"message": "User not found"}), 404

        mongo.db.users.delete_one({"_id": ObjectId(user_id)})

        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        return jsonify({"message": "Error deleting ENM", "error": str(e)}), 500


@api.route("/enms", methods=["GET"])
@token_required
def get_enms():
    user_id = request.user.get("sub")

    # enms_cursor = mongo.db.enms.find({"user_id": user_id})
    enms_cursor = mongo.db.enms.find()
    enms = []
    for e in enms_cursor:
        enms.append({
            "id": str(e["_id"]),
            "enm": e.get("enm"),
            "circle": e.get("circle"),
            "vendor":e.get("vendor")
        })


    return jsonify(enms), 200

# dsadsajdkas

@api.route("/create_user", methods=["GET"])
def create_mera_user():
    
    hashed_pw = bcrypt.hash("Sarfraz@123")
    user = {
        "full_name": "Sarfraz",
        "email": "sarfraz@datayog.com",
        "hashed_password": hashed_pw,
        "ts":datetime.now().timestamp(),
        # "updated":request.user.get("sub") 
    }

    mongo.db.users.insert_one(user)

@api.route("/check_conn", methods=["GET"])
def check_conn():
    
    
    
    mongo_uri = os.environ.get("MONGO_URI")
    temp_client = pymongo.MongoClient(mongo_uri)
    try:
        temp_client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        return "✅ Connected to MongoDB"
    except Exception as e:
        print("❌ Connection failed:", e)
        return "❌ Connection failed:" + str(e)



@api.route("/run_gpl_audit_nokia", methods=["POST"])
@token_required
def run_gpl_audit_nokia_api():
    
    
    
    circle_name = request.form.get("circle")
    
    settings = request.files.get("settings")
    enm_files = request.files.get("enm_file")
    if not settings or not enm_files:
        return jsonify({"message": "No selected settings or eFile file"}), 400
    
    
    
    if settings:
        settings_original_filename = secure_filename(settings.filename)
        settings_unique_filename = f"{uuid.uuid4().hex}_{settings_original_filename}"
        settings_file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"settings_nokia"), settings_unique_filename)
        settings.save(settings_file_path)
        
    
    if enm_files:
        enm_files_original_filename = secure_filename(enm_files.filename)
        enm_files_unique_filename = f"{uuid.uuid4().hex}_{enm_files_original_filename}"
        enm_files_file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"enm_files_nokia"), enm_files_unique_filename)
        enm_files.save(enm_files_file_path)
        
        
        
        # 
        
    
        

    return jsonify({"message": "GPL Audit Nokia Completed successfully"}), 201
    
    
    return ""


@api.route("/run_gpl_audit", methods=["POST"])
@token_required
def run_gpl_audit_api():
    
    uid = request.user.get("sub")
    if "Efile" not in request.files and not "siteList" in request.files:
        return jsonify({"message": "No file part"}), 400
    
    eFile = request.files.getlist("Efile")
    if not eFile:
        return jsonify({"message": "No selected eFile file"}), 400


    siteList = request.files.get("siteList")
    circle_name = request.form.get("circle")
    if not siteList:
        return jsonify({"message": "No selected siteList file"}), 400


    print(siteList,eFile)

    siteList_original_filename = secure_filename(siteList.filename)
    siteList_unique_filename = f"{uuid.uuid4().hex}_{siteList_original_filename}"
    
        
    siteList_file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"gpl_audit_site"), siteList_unique_filename)
    siteList.save(siteList_file_path)
    
    
    
    
    
    eFile_original_filename_list = []
    enmFile_list = []
    for oneefile in eFile:    
        eFile_original_filename = secure_filename(oneefile.filename)
        eFile_unique_filename = f"{uuid.uuid4().hex}_{eFile_original_filename}"
        oneefile_file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"gpl_audit_enm"), eFile_unique_filename)
        
        eFile_original_filename_list.append({
            "eFile_original_filename":eFile_original_filename,
            "eFile_unique_filename":eFile_unique_filename,
            "efile_file_path":oneefile_file_path
        })
        
        
        enmFile_list.append(oneefile_file_path)
        
    
        
        
        oneefile.save(oneefile_file_path)
        
    
    
    print(eFile_original_filename_list,siteList_file_path)
        
        
    one_last_data = mongo.db.audit_files.find_one(sort=[('_id', -1)])

    aud_task_id = "AUD000001"

    if(one_last_data):
        last_task = one_last_data["aud_task_id"].replace("AUD","")
        
        new_id = int(last_task)+1
        
        
        str_new_id = len(str(new_id))
        
        aud_task_id = "AUD"+(6-str_new_id)*"0"+str(new_id)
        
        
    print(aud_task_id)
        
        
        


        
        
        
        
        
    
    
    curr_dir = os.getcwd()
    
    print(enmFile_list,siteList_file_path)
    
    final_file_path = run_gpl_audit(curr_dir,circle_name,enmFile_list,siteList_file_path,aud_task_id)
    
    
    final_file_path_list = []
    
    for fill in os.path.join(os.getcwd(),final_file_path):
        final_file_path_list.append(fill)
    
    
    shutil.copy(siteList_file_path, final_file_path)
    
    # for filll in enmFile_list:
        
    #     shutil.copy(filll, final_file_path)
        
    
    zip_path = create_zip_from_folder(final_file_path, final_file_path+".zip")
    
    print(final_file_path,"final_file_pathfinal_file_path")
    
    
    
    audit_data = {
        "zip_path":zip_path,
        "output_folder":final_file_path,
        "aud_task_id":aud_task_id,
        "enmFile_list":enmFile_list,
        "siteList_file_path":siteList_file_path,
        "eFile_original_filename_list":eFile_original_filename_list,
        "siteList_original_filename":siteList_original_filename,
        "siteList_unique_filename":siteList_unique_filename,
        "circle":circle_name,
        "tss":datetime.now().timestamp(),
        "user_id": request.user.get("sub"),
        "updated":request.user.get("sub") 
    }
    
    
    
    mongo.db.audit_files.insert_one(audit_data)
    
    
    
    
    return jsonify({"message": "Audit Completed successfully"}), 201
    
    

@api.route("/gpl_audit_files", methods=["GET"])
@token_required
def get_gpl_audit_files():
    user_id = request.user.get("sub")  
    
    
    aggr = [
        {
            '$addFields': {
                'user_id_obj': {
                    '$convert': {
                        'input': '$user_id', 
                        'to': 'objectId'
                    }
                }, 
                'uID': {
                    '$convert': {
                        'input': '$_id', 
                        'to': 'string'
                    }
                }
            }
        }, {
            '$lookup': {
                'from': 'users', 
                'localField': 'user_id_obj', 
                'foreignField': '_id', 
                'as': 'userresult'
            }
        }, {
            '$unwind': {
                'path': '$userresult', 
                'preserveNullAndEmptyArrays': True
            }
        },{
            '$sort': {
                '_id': -1
            }
        }, {
            '$project': {
                'user_id_obj': 0, 
                'userresult.hashed_password': 0, 
                'userresult._id': 0, 
                '_id': 0
            }
        }
    ]

    # files_cursor = mongo.db.files.find({"user_id": user_id})
    files_cursor = mongo.db.audit_files.aggregate(aggr)
    
    
    
    files_list = []
    for f in files_cursor:
        
        print(f)
        
        
        files_list.append(f)
    
    return jsonify(files_list), 200