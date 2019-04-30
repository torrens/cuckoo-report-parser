import json
import os
import zipfile

PRINT_MAX = 10


def unzip_report(file_path):
    json_path = os.path.dirname(file_path) + os.sep
    json_file_path = os.path.splitext(file_path)[0] + '.json'

    zipfile.ZipFile(file_path, 'r').extractall(json_path)
    return json_file_path


def read_json_report(json_file_path):
    f = open(json_file_path)
    json_data = json.load(f)
    return json_data


def read_data(file_path, start, end):
    f = open(file_path)
    f.seek(start)
    data = f.read(end-start)
    json_data = '{' + data + '}'
    return json.loads(json_data)


def delete_json_report(json_file_path):
    os.remove(json_file_path)


def read_md5(file_path, index):
    target_idx = index['target']
    data = read_data(file_path, target_idx['start'], target_idx['end'])

    return data['target']['file']['md5']


def process_strings(md5, file_path, index):
    strings_idx = index['strings']
    data = read_data(file_path, strings_idx['start'], strings_idx['end'])

    strings = "\t".join(data['strings'])
    print(f'md5: {md5} strings: {strings}')


def process_imports(md5, file_path, index):
    imports_idx = index['imports']
    data = read_data(file_path, imports_idx['start'], imports_idx['end'])
    print_count = 0

    try:
        for an_import_list in data['pe_imports']:
            dll = an_import_list['dll'].lower()
            for an_import in an_import_list['imports']:
                import_name = an_import['name']
                if import_name is not None:
                    if print_count <= PRINT_MAX:
                        print(f'Imports md5: {md5} dll: {dll} import: {import_name}')
                        print_count += 1
    except Exception as ex:
        print('process_imports error', ex)


def process_calls(md5, file_path, index):
    processes_idx = index['processes']
    data = read_data(file_path, processes_idx['start'], processes_idx['end'])
    print_count = 0

    sequence = 0
    try:
        for a_processes_list in data['processes']:
            calls = a_processes_list['calls']
            for a_call in calls:
                if sequence > 10000:
                    break

                api = a_call['api'].lower()
                time = a_call['time']
                if print_count <= PRINT_MAX:
                    print(f'Calls md5: {md5} api: {api} time: {time}')
                    print_count += 1
                sequence += 1
    except Exception as ex:
        print(ex)


def process_api_stats(md5, file_path, index):
    apistats_idx = index['apistats']
    data = read_data(file_path, apistats_idx['start'], apistats_idx['end'])
    print_count = 0

    try:
        api_stats = data['apistats']
        keys = api_stats.keys()
        for key in keys:
            stats_obj = api_stats[key]
            calls = stats_obj.keys()
            for call in calls:
                count = stats_obj[call]
                if print_count <= PRINT_MAX:
                    print(f'API Stats md5: {md5} call: {call} count: {count}')
                    print_count += 1
    except Exception as ex:
        print('process_api_stats error', ex)


def read_index(path):
    parts = os.path.splitext(path)
    idx = parts[0] + '.idx'
    f = open(idx)
    return json.load(f)


def process_zip_file(file_path):
    print('Processing', file_path)
    json_file_path = unzip_report(file_path)
    index = read_index(file_path)
    md5 = read_md5(json_file_path, index)
    process_strings(md5, json_file_path, index)
    process_imports(md5, json_file_path, index)
    process_calls(md5, json_file_path, index)
    process_api_stats(md5, json_file_path, index)
    delete_json_report(json_file_path)


def read_zip_files(root):
    files = []
    for dir_name, sub_dir_list, file_list in os.walk(root):
        for file_name in file_list:
            file_path = os.path.join(dir_name, file_name)
            if 'zip' in file_path:
                files.append(file_path)

    return files


zip_files = read_zip_files(os.getcwd() + os.sep + 'reports')
for zip_file in zip_files:
    process_zip_file(zip_file)


