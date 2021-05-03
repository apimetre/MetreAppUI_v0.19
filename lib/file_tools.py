import os
import json
import textwrap

CONSOLE_WIDTH = 140
INDENT_STR = '       '

def print_wrap(text, indent_str, len):
    lines = textwrap.wrap(text, width=len, subsequent_indent=indent_str)
    for line in lines:
        print(line)

def dir(filename_search_term):
    return [s for s in os.listdir() if filename_search_term in s]

def nfile(path_name):
    path = path_name.split('/')[0]
    name = path_name.split('.')[-2]
    ext = path_name.split('.')[-1]
    return {'path':path, 'name':name, 'ext':ext}

def binfile_to_list(file_path, scalar=1.0):
    count = 0
    data = []
    with open(file_path, 'rb') as f:
        while True:
            two_bytes = f.read(2)
            if not two_bytes:
                break
            data.append(scalar * int.from_bytes(two_bytes, byteorder='big'))
    return data

def binfile_to_dict(file_path, scalar=1.0):
    out_dict = {}
    with open(file_path) as f:
        try:
            return json.load(f)
        except ValueError:
            return {'data': binfile_to_list(file_path, scalar)}

def update_json_file(file_path, new_data_dict):
    try:
        with open(file_path) as f:
            old_data_dict = json.load(f)
        with open(file_path, 'w') as f:
            old_data_dict.update(new_data_dict)
            json.dump(old_data_dict, f)
        return old_data_dict
    except ValueError:
        return None

def dict_to_json_file(file_path, out_dict):
    with open(file_path, 'w') as f:
         json.dump(out_dict, f)

def json_file_to_dict(file_path):
    try:
        with open(file_path) as f:
            return json.load(f)
    except ValueError:
        return None
        
if __name__ == '__main__':
    # test
    print_wrap(f"binfile_to_list: {binfile_to_list('../result.bin')}", INDENT_STR, CONSOLE_WIDTH)
    print_wrap(f"binfile_to_dict (bin): {binfile_to_dict('../result.bin')}", INDENT_STR, CONSOLE_WIDTH)
    dict_to_json_file('../result.json', binfile_to_dict('../result.bin'))
    print_wrap(f"json_file_to_dict: {json_file_to_dict('../result.json')}", INDENT_STR, CONSOLE_WIDTH)
    update_json_file('../result.json', {'foo':'bar1'})
    print_wrap(f"update_json_file: {json_file_to_dict('../result.json')}", INDENT_STR, CONSOLE_WIDTH)
