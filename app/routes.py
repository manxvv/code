from flask import send_file,send_from_directory,Blueprint,url_for, request, jsonify, current_app
from app.database import mongo
from passlib.hash import bcrypt
import jwt
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

import os
import tempfile
import shutil
import zipfile
from typing import List
import sys

path_nsa_sa = os.path.join(os.path.join(os.getcwd(),"app"),"nsa_sa")
print(sys.path)
sys.path.append(path_nsa_sa)
from app.nsa_sa.script_runner import scripting_nsa_sa

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

        return os.path.abspath(zip_filename)

    finally:
        # 3. Clean up
        shutil.rmtree(temp_dir)



@api.route("/register", methods=["POST"])
def register():
    data = request.json
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not email or not password:
        return jsonify({"error": "All fields (full_name, email, password) are required"}), 400

    if mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400

    hashed_pw = bcrypt.hash(password)
    user = {
        "full_name": full_name,
        "email": email,
        "hashed_password": hashed_pw,
        "role": "user"   
    }

    mongo.db.users.insert_one(user)

    return jsonify({"message": "User created successfully"}), 201


@api.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = mongo.db.users.find_one({"email": email})
    if not user or not bcrypt.verify(password, user["hashed_password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode(
        {
            "sub": str(user["_id"]),
            "role": user.get("role", "admin"),  
            "exp": datetime.utcnow() + timedelta(hours=1)
        },
        current_app.config["JWT_SECRET"],
        algorithm=current_app.config["JWT_ALGORITHM"]
    )

    return jsonify({
        "email": user["email"],
        "role": user.get("role", "admin"),
        "access_token": token
    })

@api.route("/", methods=["GET"])
def user111():
    return {"message": "Hello from Flask!"}


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






@api.route("/upload", methods=["POST"])
@token_required
def upload_file():
    if ("precheck" or "postcheck") not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    
    precheckfile = request.files.getlist("precheck")
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
        
    
    
    
    
    
    print(postcheck_files,precheck_files)
    
    
    
    clc = Calculator()
    
    pre_file = ""
    post_file = ""
    if(len(precheck_files) > 0):
        pre_file=clc.start_parser(precheck_files,"Pre_")
        
    if(len(postcheck_files) > 0):
        post_file=clc.start_parser(postcheck_files,"Post_")
    # pre_file="post08_09_2025_01_56_16_cells_data_temp.xlsx"
    # pre_file="pre08_09_2025_02_03_56_cells_data_temp.xlsx"
    # post_file="post08_09_2025_02_04_01_cells_data_temp.xlsx"






    if(len(postcheck_files) > 0):
        clc.startdiffCalc(pre_file,post_file)

    
    if(len(precheck_files) > 0):
        clc.rearrangecol(pre_file)
        clc.coloring_formatting(pre_file)
        clc.re_arrange_node_status(pre_file)
    
    if(len(postcheck_files) > 0):
        clc.rearrangecol(post_file)
        clc.coloring_formatting(post_file)
    
    
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
        "path": post_file if len(postcheck_files) > 0 else pre_file
    }

    result = mongo.db.files.insert_one(file_doc)
    
    return jsonify({
        "message": "File uploaded successfully",
        "file_id": str(result.inserted_id),
        "filename": unique_filename,
        "parsed_excel_filename": post_file if len(postcheck_files) > 0 else pre_file
    }), 201





@api.route("/uploadenm", methods=["POST"])
@token_required
def uploadenm_file():
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    print(request.files.get("file"))
    
    
    enm_circle_cursor = mongo.db.enms.find({
        "user_id":request.user.get("sub")  
    })
    
    
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
    
    
    updf = df[["circle","enm"]]
    
    
    updf["merge_ce"] = updf["circle"]+"_cp_"+updf["enm"]
    
    read_df["merge_ce"] = read_df["circle"]+"_cp_"+read_df["ENM"]
    
    
    print(updf,read_df,"updfupdfupdfupdfupdf")
    read_df_enmmm = set(read_df["merge_ce"].unique())
    
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
    
    file_doc = {
        "user_id": request.user.get("sub"),
        "original_filename": original_filename,
        "filename": unique_filename,
        "enm_file_name": ",".join(fileNameList),
        "enms": "/".join(enm_list),
        "circle":"/".join(circle_list),
        "site_id":"/".join(SiteID_list),
        "nodes":"/".join(Node_list)
    }

    result = mongo.db.enmfiles.insert_one(file_doc)
    result = mongo.db.migration.insert_one({**file_doc,"status":"Pending"})
    
    return jsonify({
        "message": "File uploaded successfully",
        "file_id": str(result.inserted_id),
        "filename": unique_filename,
        "enm_file_name": ffnme
    }), 201
    
    
    
def script_entry_migration(file_con,file_path):
    
    
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
        "nodes":"/".join(Node_list)
    }
    
    
    final_data = {**file_con,**datafind}
    
    mongo.db.scripting.insert_one(
        final_data
    )
    
    mongo.db.migration.update_one(
        datafind,
        {"$set": {"status": "Done"}}
    )
    
    
    
    
    
@api.route("/uploadScripting", methods=["POST"])
@token_required
def uploadScripting_file():
    if "eFile" not in request.files and not "siteList" in request.files:
        return jsonify({"message": "No file part"}), 400
    
    eFile = request.files.get("eFile")
    if not eFile:
        return jsonify({"message": "No selected eFile file"}), 400


    siteList = request.files.get("siteList")
    if not siteList:
        return jsonify({"message": "No selected siteList file"}), 400


    siteList_original_filename = secure_filename(siteList.filename)
    eFile_original_filename = secure_filename(eFile.filename)
    siteList_unique_filename = f"{uuid.uuid4().hex}_{siteList_original_filename}"
    eFile_unique_filename = f"{uuid.uuid4().hex}_{eFile_original_filename}"
    
    
    curr_dir = os.getcwd()
    
    
    circle_name = request.form.get('circle')
    enm_name = request.form.get('enm')
    
    
    
    
    
    
    siteList_file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"scripting_sites"), siteList_unique_filename)
    siteList.save(siteList_file_path)
    eFile_file_path = os.path.join(os.path.join(UPLOAD_FOLDER,"scripting_enm"), eFile_unique_filename)
    eFile.save(eFile_file_path)
    
    
    nsa_sa_path = os.path.join(os.getcwd(),"app","nsa_sa")
    
    sys.path.append(nsa_sa_path)
    
    print(sys.path,"sys.pathsys.pathsys.pathsys.path")
    
    nsa_op_folder = scripting_nsa_sa(siteList_original_filename,eFile_original_filename,nsa_sa_path,circle_name,enm_name,os.path.join(curr_dir,siteList_file_path),os.path.join(curr_dir,eFile_file_path),curr_dir)

    list_dirr = os.listdir(nsa_op_folder)
    
    excel_file = ""
    
    

    shutil.make_archive(nsa_op_folder, 'zip', nsa_op_folder)

    for i in list_dirr:
        if("xlsx" in i):
            excel_file = i
            
    
    file_con = {
        "siteList_original_filename":siteList_original_filename,
        "siteList_unique_filename":siteList_unique_filename,
        "eFile_original_filename":eFile_original_filename,
        "eFile_unique_filename":eFile_unique_filename,
        "nsa_op_folder":nsa_op_folder.replace(os.getcwd(),"")+".zip",
    }
    script_entry_migration(file_con,os.path.join(nsa_op_folder,excel_file))
    
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
            '$project': {
                'user_id_obj': 0, 
                'userresult.hashed_password': 0, 
                'userresult._id': 0, 
                '_id': 0
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
            '$project': {
                'user_id_obj': 0, 
                'userresult.hashed_password': 0, 
                'userresult._id': 0, 
                '_id': 0
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
        "name": data["name"]
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

    # Validate required fields
    if not data or "enm" not in data or "circle" not in data:
        return jsonify({"message": "Invalid input, 'ENM' and 'Circle' are required"}), 400

    # Check if the combination already exists
    existing = mongo.db.enms.find_one({"enm": data["enm"], "circle": data["circle"]})
    if existing:
        return jsonify({"message": "ENM with this 'ENM' and 'Circle' already exists"}), 400

    enm = {
        "user_id": request.user.get("sub"),
        "enm": data["enm"],
        "circle": data["circle"]
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


@api.route("/enms", methods=["GET"])
@token_required
def get_enms():
    user_id = request.user.get("sub")

    enms_cursor = mongo.db.enms.find({"user_id": user_id})
    enms = []
    for e in enms_cursor:
        enms.append({
            "id": str(e["_id"]),
            "enm": e.get("enm"),
            "circle": e.get("circle")
        })

    return jsonify(enms), 200
