import re


def parse_dynamic_data_to_dict(*, para_file: list) -> dict:
    def normalize(value):
        if type(value) == str and re.match('(.*,ManagedElement=[^,]*),(.*)', value):
            return re.match('(.*,ManagedElement=[^,]*),(.*)', value).group(2)
        else: return value

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
                    str(parse_nested_dict(v[1:-1])) if v.startswith("{") and v.endswith("}") else str(normalize(v.strip()))
                    for v in value[1:-1].split(", ")
                ]
            elif value.startswith('"') and value.endswith('"'): value = normalize(value[1:-1])  # Remove surrounding quotes

            nested_dict[key] = normalize(value)
        return nested_dict

    def parse_list_of_dicts(value) -> list:
        value = value.strip("[]")  # Remove surrounding square brackets
        dicts = re.findall(r"\{([^{}]+)\}", value)  # Extract all `{...}` blocks
        return [parse_nested_dict(item) for item in dicts]

    def moodify_block_if_colon_is_missing(*, block_data: list) -> list:
        indices_to_remove = []
        for i in range(len(block_data)):
            if ' : ' not in block_data[i]:
                block_data[i-1] = block_data[i-1] + block_data[i]
                indices_to_remove.append(i)
        indices_to_remove.sort(reverse=True)
        for i in indices_to_remove:
            del block_data[i]
        return block_data

    def parse_fdn_dict_block(*, block_data: list) -> dict:
        result = {}
        # block_data = moodify_block_if_colon_is_missing(block_data=block_data)
        for para_line in block_data:
            key, value = para_line.split(" : ", maxsplit=1)
            key, value = str(key.strip()), str(value.strip())
            if value == "<empty>": value = None
            elif value.startswith("{") and value.endswith("}"): value = parse_nested_dict(value[1:-1])
            elif value.startswith("[") and value.endswith("]") and "{" in value: value = parse_list_of_dicts(value)
            # Detect and process simple lists
            elif value.startswith("[") and value.endswith("]"):
                value = [normalize(str(v.strip().strip('"'))) for v in value[1:-1].split(", ")]
            elif value.startswith('"') and value.endswith('"'): value = normalize(value.strip('"'))
            result[key] = value
        return result

    mos_dict = {}
    node, current_fdn, block_data = None, None, []
    for l_file in para_file:
        with open(l_file, 'r') as log_file:
            for line in log_file:
                line = line.strip().strip('\n')
                if not line or ' :' not in line: continue
                if line.startswith("FDN :"):
                    if node and current_fdn:
                        mos_dict[node][current_fdn].update(parse_fdn_dict_block(block_data=block_data))
                        node, current_fdn, block_data = None, None, []
                    fdn = line.split("FDN :", maxsplit=1)[1].strip().strip('"')
                    if re.match('.*,MeContext=([^,]*).*', fdn):
                        node = re.match('.*,MeContext=([^,]*).*', fdn).group(1)
                        if re.match('.*,ManagedElement=([^,]*),.*', fdn):
                            current_fdn = re.match('.*,ManagedElement=[^,]*,(.*)', fdn).group(1)
                        else: current_fdn = fdn
                    elif re.match('NetworkElement=([^,]*).*', fdn):
                        node = re.match('NetworkElement=([^,]*).*', fdn).group(1)
                        current_fdn = fdn
                    else:
                        node, current_fdn = None, None
                    if node and current_fdn:
                        if node not in mos_dict.keys(): mos_dict[node] = {}
                        if current_fdn not in mos_dict[node].keys(): mos_dict[node][current_fdn] = {}
                        if not mos_dict[node].get('me_me') and re.match('(.*,ManagedElement=[^,]*),.*', fdn):
                            mos_dict[node]['me_me'] = re.match('(.*,ManagedElement=[^,]*),(.*)', fdn).group(1)
                else:
                    block_data.append(line)
            if node and current_fdn: mos_dict[node][current_fdn].update(parse_fdn_dict_block(block_data=block_data))
    return mos_dict
