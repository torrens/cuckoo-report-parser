import json
import os
from pathlib import Path
import time
import zipfile


def read_data(file_path, start, end):
    f = open(file_path)
    f.seek(start)
    data = f.read(end-start)
    json_data = '{' + data + '}'
    json.loads(json_data)


def is_close(data):
    return is_close_object(data) or is_close_array(data)


def is_close_object(data):
    return '}' in data


def is_close_array(data):
    return ']' in data


def is_open(data):
    return is_open_object(data) or is_open_array(data)


def is_open_object(data):
    return '{' in data


def is_open_array(data):
    return '[' in data


def is_object(data):
    return is_open_object(data) or is_close_object(data)


OBJ_S = 'OBJ_START'
OBJ_E = 'OBJ_END'
ARR_S = 'ARR_START'
ARR_E = 'ARR_END'


def json_type(data):
    if is_open_object(data):
        return OBJ_S
    elif is_close_object(data):
        return OBJ_E
    elif is_open_array(data):
        return ARR_S
    elif is_close_array(data):
        return ARR_E
    else:
        raise ValueError('Unkown type', data)


def if_closes(stack_top, token):
    if stack_top == OBJ_S:
        return is_close_object(token)
    elif stack_top == ARR_S:
        return is_close_array(token)


def remove_quote_contents(data):
    # "blah" : "blah" -> "" : ""
    removed = ''
    in_quotes = False
    escaped = False

    for c in data:
        if escaped:
            escaped = False
            pass
        elif c == '\\':
            escaped = True
            pass
        elif c == ' ' or c == '\n':
            pass
        elif not in_quotes and c == '"':
            removed += c
            in_quotes = True
            pass
        elif in_quotes and c == '"':
            removed += c
            in_quotes = False
            pass
        elif in_quotes:
            pass
        else:
            removed += c

    return removed


def indexer(file_path, start_string):

    top_found = False
    running_offset = 0
    start_pos = 0
    end_pos = 0

    stack = list()

    f = open(file_path)
    for line_number, line in enumerate(f, 1):
        running_offset += len(line)

        # The start_string is found
        if not top_found and line.startswith(start_string):
            top_found = True
            start_pos = running_offset - len(line)
            stack.append(json_type(line))
        # If already found
        elif top_found:
            mod_line = remove_quote_contents(line)

            # If closes current
            if if_closes(stack[-1], mod_line):
                stack.pop()
            # Finished
            if not stack:
                # Strip comma
                index = line.find(',')
                end_pos = running_offset - (len(line) - index)
                break
            # If a new start
            elif is_open(mod_line):
                # Test an open isn't closes on the same line
                if is_close(mod_line):
                    pass
                else:
                    stack.append(json_type(mod_line))

    f.close()
    return start_pos, end_pos


def index(file):
    an_index = dict()

    string_indexes = indexer(file, '    \"strings\": [')
    an_index['strings'] = {"start": string_indexes[0], "end": string_indexes[1]}

    target_indexes = indexer(file, '    \"target\": {')
    an_index['target'] = {"start": target_indexes[0], "end": target_indexes[1]}

    apistats_indexes = indexer(file, '        \"apistats\": {')
    an_index['apistats'] = {"start": apistats_indexes[0], "end": apistats_indexes[1]}

    processes_indexes = indexer(file, '        \"processes\": [')
    an_index['processes'] = {"start": processes_indexes[0], "end": processes_indexes[1]}

    imports_indexes = indexer(file, '        \"pe_imports\": [')
    an_index['imports'] = {"start": imports_indexes[0], "end": imports_indexes[1]}

    parts = os.path.splitext(file)
    json.dump(an_index, open(parts[0] + '.idx', 'w'))


def unzip_report(file_path):
    file_name_path = Path(file_path)
    file_name = file_name_path.name
    suffix = file_name_path.suffix

    json_file_path = file_path[0:len(file_path) - len(suffix)] + '.json'
    json_path = file_path[0:len(file_path) - len(file_name)]

    zipfile.ZipFile(file_path, 'r').extractall(json_path)
    return json_file_path


def read_zip_files(root):
    files = []
    for dir_name, sub_dir_list, file_list in os.walk(root):
        for file_name in file_list:
            file_path = os.path.join(dir_name, file_name)
            if 'zip' in file_path:
                files.append(file_path)

    return files


def process_zip_file(file_path):
    start = time.time()
    
    json_file_path = unzip_report(file_path)
    print('Indexing', json_file_path)
    index(json_file_path)
    os.remove(json_file_path)

    print('Indexed', str(time.time() - start))


zip_files = read_zip_files(os.getcwd() + os.sep + 'reports')
for zip_file in zip_files:
    process_zip_file(zip_file)
