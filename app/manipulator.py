import re
import ast

a = [
    "[[{mncLength=2, mcc=401, mnc=91},{mncLength=2, mcc=500, mnc=94}],[{mncLength=2, mcc=404, mnc=594},{mncLength=2, mcc=424, mnc=94}]]",
    "[{a5Thr2RsrqFreqQciOffset=-50, lbA5Threshold2RsrqOffset=0, atoThresh2QciProfileHandling=ALLOWED, a3RsrqFreqQciOffsetAdjustment=0, a3RsrpFreqQciOffsetAdjustment=0, timeToTriggerA3Rsrq=-1, timeToTriggerA3=-1, qciProfileRef=SubNetwork=ONRM_ROOT_MO,SubNetwork=LTE_5G,MeContext=TN-NLBELHLL-1,ManagedElement=TN-NLBELHLL-1,ENodeBFunction=1,QciTable=default,QciProfilePredefined=qci1, lbQciProfileHandling=FORBIDDEN, a5Thr1RsrpFreqQciOffset=2, a5Thr1RsrqFreqQciOffset=-240, a5Thr2RsrpFreqQciOffset=10, atoThresh1QciProfileHandling=ALLOWED, lbA5Threshold2RsrpOffset=0}],[{a5Thr2RsrqFreqQciOffset=-30, lbA5Threshold2RsrqOffset=0, atoThresh2QciProfileHandling=ALLOWED, a3RsrqFreqQciOffsetAdjustment=0, a3RsrpFreqQciOffsetAdjustment=0, timeToTriggerA3Rsrq=-1, timeToTriggerA3=-1, qciProfileRef=SubNetwork=ONRM_ROOT_MO,SubNetwork=LTE_5G,MeContext=TN-NLPLKOD2-1,ManagedElement=TN-NLPLKOD2-1,ENodeBFunction=1,QciTable=default,QciProfilePredefined=qci1, lbQciProfileHandling=FORBIDDEN, a5Thr1RsrpFreqQciOffset=-2, a5Thr1RsrqFreqQciOffset=-240, a5Thr2RsrpFreqQciOffset=62, atoThresh1QciProfileHandling=ALLOWED, lbA5Threshold2RsrpOffset=0}]",
    "[SubNetwork=ONRM_ROOT_MO,SubNetwork=LTE_5G,MeContext=TN-NLPLKOD2-1,ManagedElement=TN-NLPLKOD2-1,GNBDUFunction=1,NRSectorCarrier=S2_N11,SubNetwork=ONRM_ROOT_MO,SubNetwork=LTE_5G,MeContext=TN-NLPLKOD2-1,ManagedElement=TN-NLPLKOD2-1,GNBDUFunction=1,NRSectorCarrier=S2_N11]",
    "[false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false]",
    "{acBarringFactor=95, acBarringForSpecialAC=[false, false, false, false, false], acBarringTime=64}",
    "[false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false]",
    "[false, false, true, true]"
]





def data_type_id(stripped_text,set_of_list):
    
    
    
    
    
    if(stripped_text.startswith("[") and stripped_text.endswith("]")):
        matches = re.findall(r'\{.*?\}', stripped_text)
        
        for onematch in matches:
            print(onematch)
            print(matches)
            if("=" in onematch or ":" in onematch):
                data_type_id(onematch.replace("=",":"),set_of_list)
            
            
    elif(stripped_text.startswith("{") and stripped_text.endswith("}")):
        print("Dict Capture"+stripped_text)
        data_type_id(stripped_text[1:-1],set_of_list)
    
    else:
        splitted_val = stripped_text.split(", ")
        
        # for oneval in splitted_val:
        #     print(oneval,"oneval")
        #     if("=" in oneval or ":" in oneval):
        #         set_of_list[oneval.split("=")[0]] = oneval.split("=")[1]
        #     else:
        #         print(oneval)
        # print("string")
        
    
final_arr = []

for oneText in a:
    
    print("=========================================================")
    
    set_of_list={}
    stripped_oneText = oneText.strip()
    data_type_id(stripped_oneText,set_of_list)
    final_arr.append(set_of_list)
    # print(set_of_list)

    print("=========================================================")

# print(set_of_list)