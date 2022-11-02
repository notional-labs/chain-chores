# Line requirements:
# Apply Google CLI Syntax for required and optional args
# https://developers.google.com/style/code-syntax

import os
import re

current_dir = os.path.dirname(os.path.realpath(__file__))
# os.chdir(current_dir)

IGNORE_VARIABLES = ["flags"] # [flags]


def _replace_array(line: str):
    '''
    Convert [value][,[value]] -> VALUE...
    '''
    matches = re.findall(r'\[,\[(.*?)\]\]', line) # ['name', 'receiver']
    if matches:
        for variable_name in matches:
            if variable_name in IGNORE_VARIABLES: continue                                
            line = line.replace(f'[{variable_name}][,[{variable_name}]]', f"{variable_name.upper().replace('-', '_')}...")                
    return line


def _replace_standard(line: str):
    '''
    Convert [value] -> VALUE
    '''
    matches = re.findall(r'\[(.*?)\]', line) # ['name', 'receiver']
    if matches:
        for variable_name in matches:
            if variable_name in IGNORE_VARIABLES: continue
            line = line.replace(f'[{variable_name}]', f'{variable_name.upper().replace("-", "_")}')            
    return line


def convert_commands_to_google_format(chain: str, debug: bool = False):

    for root, dirs, files in os.walk(chain):
        
        if 'cmd' in root or '/cli' in root:
            if debug: print(root, files)

            for file in files:
                if not file.endswith(".go"):
                    continue

                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                with open(file_path, 'w') as f:
                    for line in lines:
                        if re.search(r'Use:.*\"', line):
                            line = _replace_array(line)
                            line = _replace_standard(line)        
                        f.write(line)