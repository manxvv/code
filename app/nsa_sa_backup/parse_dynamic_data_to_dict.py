import re


def parse_dynamic_data_to_dict(*, para_file: str) -> dict:
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

    def parse_fdn_dict_block(*, block_data: list) -> dict:
        result = {}
        for para_line in block_data:
            key, value = para_line.split(" :", maxsplit=1)
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

    mos_dict, block_data, current_fdn, node = {}, [], None, None
    with open(para_file, 'r') as log_file:
        for line in log_file:
            line = line.strip().strip('\n')
            if not line or ' :' not in line: continue
            if line.startswith("FDN :"):
                if node and current_fdn:
                    mos_dict[node][current_fdn].update(parse_fdn_dict_block(block_data=block_data))
                    block_data = []
                current_fdn = line.split("FDN :", maxsplit=1)[1].strip().strip('"')
                if ',MeContext=' in current_fdn: node = re.match('.*,MeContext=([^,]*),.*', current_fdn).group(1)
                elif current_fdn.startswith('NetworkElement='): node = re.match('NetworkElement=([^,]*),.*', current_fdn).group(1)
                else: current_fdn, node = None, None
                if node and node not in mos_dict.keys(): mos_dict[node] = {}

                if current_fdn and re.match('(.*,ManagedElement=[^,]*),.*', current_fdn):
                    if not mos_dict[node].get('me_me', None):
                        mos_dict[node]['me_me'] = re.match('(.*,ManagedElement=[^,]*),(.*)', current_fdn).group(1)
                    current_fdn = re.match('(.*,ManagedElement=[^,]*),(.*)', current_fdn).group(2)
                if current_fdn not in mos_dict.get(node, {}).keys(): mos_dict[node][current_fdn] = {}
            else:
                block_data.append(line)
        if node and current_fdn: mos_dict[node][current_fdn].update(parse_fdn_dict_block(block_data=block_data))
    return mos_dict
