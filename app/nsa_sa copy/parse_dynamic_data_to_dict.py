import re


def parse_dynamic_data_to_dict(*, para_file: str) -> dict:
    def parse_nested_dict(nested: str) -> dict:
        nested_dict = {}
        pattern = re.compile(r'([\w]+)=("[^"]*"|{[^}]*}|\[[^\]]*\]|[^,]+)')
        matches = pattern.findall(nested)  # Extract key-value pairs from nested string
        for key, value in matches:
            key, value = str(key.strip()), str(value.strip())
            # Detect nested lists or dictionaries, and process them
            if value.startswith("{") and value.endswith("}"): value = parse_nested_dict(value[1:-1])
            elif value.startswith("[") and value.endswith("]"):
                value = [
                    str(parse_nested_dict(v[1:-1])) if v.startswith("{") and v.endswith("}") else str(v.strip())
                    for v in value[1:-1].split(",")
                ]
            elif value.startswith('"') and value.endswith('"'): value = value[1:-1]  # Remove surrounding quotes

            nested_dict[key] = value
        return nested_dict

    def parse_list_of_dicts(value) -> list:
        value = value.strip("[]")  # Remove surrounding square brackets
        dicts = re.findall(r"\{([^{}]+)\}", value)  # Extract all `{...}` blocks
        return [parse_nested_dict(item) for item in dicts]

    def parse_fdn_dict_block(*, block_data: list) -> dict:
        result = {}
        # lines = data.strip().split("\n")
        for para_line in block_data:
            key, value = para_line.split(" :", maxsplit=1)
            key, value = str(key.strip()), str(value.strip())
            if value == "<empty>": value = None
            elif value.startswith("{") and value.endswith("}"): value = parse_nested_dict(value[1:-1])
            elif value.startswith("[") and value.endswith("]") and "{" in value: value = parse_list_of_dicts(value)
            # Detect and process simple lists
            elif value.startswith("[") and value.endswith("]"):
                value = [str(v.strip().strip('"')) for v in value[1:-1].split(", ")]
            elif value.startswith('"') and value.endswith('"'): value = value.strip('"')
            result[key] = value
        return result

    mos_dict, block_data, current_fdn, node = {}, [], None, None
    with open(para_file, 'r') as log_file:
        for line in log_file:
            line = line.strip().strip('\n')
            if not line or ' :' not in line: continue
            if line.startswith("FDN : "):
                if node and current_fdn:
                    mos_dict[node][current_fdn] |= parse_fdn_dict_block(block_data=block_data)
                    block_data = []
                current_fdn = line.split("FDN : ")[1].strip().strip('"')
                if ',MeContext=' in current_fdn: node = re.match('.*,MeContext=([^,]*),.*', current_fdn).group(1)
                elif current_fdn.startswith('NetworkElement='): node = re.match('NetworkElement=([^,]*),.*', current_fdn).group(1)
                else: current_fdn, node = None, None
                if node and node not in mos_dict.keys(): mos_dict[node] = {}
                if current_fdn not in mos_dict.get(node, {}).keys(): mos_dict[node][current_fdn] = {}
            else:
                block_data.append(line)
        if node and current_fdn: mos_dict[current_fdn] = parse_fdn_dict_block(block_data=block_data)
    return mos_dict

# # Provided data string
# data = """
# acBarringPresence : {acBarringPrioMoSignalingSpecAc=[PRIORITY4, PRIORITY4, PRIORITY4, PRIORITY4, PRIORITY4], acBarringPriorityCsfb=PRIORITY0, acBarringPrioMoDataSpecAc=[PRIORITY4, PRIORITY4, PRIORITY4, PRIORITY4, PRIORITY4], acBarringPrioCsfbSpecAc=[PRIORITY4, PRIORITY4, PRIORITY4, PRIORITY4, PRIORITY4], acBarringPrioEmergencySpecAc=PRIORITY0, acBarringPriorityMmtelVideo=PRIORITY0, acBarringForEmergencySpecAcPres=MANUAL, acBarringForMmtelVideoPresence=OFF, acBarringForMoDataPresence=OFF, acBarringForCsfbPresence=OFF, acBarringPrioMmtelVoiceSpecAc=[PRIORITY4, PRIORITY4, PRIORITY4, PRIORITY4, PRIORITY4], acBarringForMoSignPresence=OFF, acBarringPriorityMoSignaling=PRIORITY0, acBarringPriorityMoData=PRIORITY0, acBarringPrioMmtelVideoSpecAc=[PRIORITY4, PRIORITY4, PRIORITY4, PRIORITY4, PRIORITY4], acBarringForMmtelVoicePresence=OFF, acBarringPriorityMmtelVoice=PRIORITY0}
# additionalPlmnList : [{mnc=1, mncLength=2, mcc=1}, {mnc=1, mncLength=2, mcc=1}, {mnc=1, mncLength=2, mcc=1}, {mnc=1, mncLength=2, mcc=1}, {mnc=1, mncLength=2, mcc=1}]
# acBarringForMoSignalling : {acBarringTime=64, acBarringFactor=95, acBarringForSpecialAC=[false, false, false, false, false]}
# arpPriorityLevelForSPIFHo : [false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false]
# prioOffsetPerQci : [{offsetPerQciPrio=7, qciProfileRef="SubNetwork=ONRM_ROOT_MO,SubNetwork=LTE_5G,MeContext=TN-NLPLKOD2-1,ManagedElement=TN-NLPLKOD2-1,ENodeBFunction=1,QciTable=default,QciProfilePredefined=qci1"}]
# """
#
# # Parse the data
# file_path = r'C:\Project\Input\Airtel\test\NEW\Paraemeter.txt'
# parsed_data = parse_data_to_dict(log_file=file_path)
#
# # Print the parsed dictionary
# from pprint import pprint
#
# pprint(parsed_data)
#











#
#
# import re
# from collections import defaultdict
#
#
#
#     #
#     # for line in lines:
#     #     line = line.strip()
#     #
#     #     if not line:  # Skip empty lines
#     #         continue
#     #
#     #     # Identify FDN lines
#     #     if line.startswith("FDN :"):
#     #         # Save the previous FDN block if it exists
#     #         if current_fdn:
#     #             log_dict[current_fdn] = parse_key_value_block(block_data)
#     #             block_data = []
#     #         current_fdn = line.split("FDN :")[1].strip()
#     #
#     #     else:
#     #         # Accumulate lines under the current FDN block
#     #         block_data.append(line)
#     #
#     # # Don't forget to process the last block
#     # if current_fdn:
#     #     log_dict[current_fdn] = parse_key_value_block(block_data)
#     #
#     # return log_dict
#
#
# # def parse_key_value_block(lines):
# #     data = {}
# #     for line in lines:
# #         # Match key-value pairs of type "key: value" or "key={...}"
# #         match = re.match(r'(\w+)\s*:\s*(.+)', line)
# #         if match:
# #             key = match.group(1)
# #             value = match.group(2)
# #
# #             # Process nested dictionaries or lists
# #             if value.startswith("{") and value.endswith("}"):
# #                 value = parse_nested_dict(value)
# #             elif value.startswith("[") and value.endswith("]"):
# #                 value = [v.strip() for v in value[1:-1].split(",")]
# #
# #             data[key] = value
# #     return data
#
#
# def parse_nested_dict(nested_str):
#     nested_dict = {}
#     # Remove surrounding braces and split on commas
#     items = nested_str[1:-1].split(", ")
#     for item in items:
#         # Match nested key-value pairs of type "key=value"
#         match = re.match(r'(\w+)=([\[\]{},\w\s-]+)', item)
#         if match:
#             key = match.group(1)
#             value = match.group(2)
#
#             # Handle nested lists or dictionaries
#             if value.startswith("{") and value.endswith("}"):
#                 value = parse_nested_dict(value)
#             elif value.startswith("[") and value.endswith("]"):
#                 value = [v.strip() for v in value[1:-1].split(",")]
#
#             nested_dict[key] = value
#     return nested_dict
#
#
# # Example log content
# log_content = """FDN : "SubNetwork=ONRM_ROOT_MO,SubNetwork=LTE_5G,MeContext=TN-NLPLKOD6-1,ManagedElement=TN-NLPLKOD6-1,ENodeBFunction=1,EUtranCellFDD=TN_E_F3_OM_PLKOD6B_B"
# acBarringForCsfb : {acBarringTime=64, acBarringFactor=95, acBarringForSpecialAC=[false, false, false, false, false]}
# acBarringForEmergency : false
# acBarringForMoData : {acBarringTime=64, acBarringFactor=95, acBarringForSpecialAC=[false, false, false, false, false]}
# acBarringInfoPresent : false
# FDN : "SubNetwork=ONRM_ROOT_MO,SubNetwork=LTE_6G,MeContext=TN-NABCD-1,ManagedElement=TN-NABCD-1,ENodeBFunction=1,EUtranCellFDD=TN_E_F3_OM_ABCD_B"
# adaptiveCfiHoProhibit : NO_HO_PROHIBIT_CFI
# additionalPlmnAlarmSupprList : [false, false, false, false, false]
# additionalPlmnReservedList : [false, true, false, true, true]
# """
#
# # Call the parsing function and display the result
# parsed_data = parse_log_to_dict(log_content)
# print(parsed_data)
#
#
