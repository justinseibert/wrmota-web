import os
from re import sub, match, IGNORECASE
from datetime import datetime

from flask import current_app

from wrmota.api import hashes as Hash

def website(item):
    item = sub(r'\s*',r'',item)
    item = sub(r'(/home\.html|/)$',r'',item)
    item = sub(r'^(https*://)*(www\.)*(.*)',r'\3',item)
    return item

def spaces(item):
    item = sub(r'\s{2,}', r' ', item)
    item = sub(r'^\s*|\s*$', r'', item)
    return item

def is_code(item):
    has_code = search(r'[a-dA-D]{4}',item)
    if has_code:
        return has_code.group(0).upper()
    else:
        return False

def date_directory(style):
    folders = ''.join('%{}/'.format(i) for i in style)
    return datetime.now().strftime(folders)

def media_file(name):
    directory = date_directory('md')
    unique_name = Hash.generate_token(8).decode('utf-8')
    extension = name.rsplit('.', 1)[1].lower()
    relative_path = '{}{}.{}'.format(directory,unique_name,extension)

    try:
        path = os.path.join(current_app.config['UPLOAD_DIRECTORY'],directory)
        os.makedirs(path,exist_ok=False)
        os.chmod(path,0o755)
        print('UPLOAD: created new directory {}'.format(directory))
    except OSError:
        print('UPLOAD: directory {} already exists'.format(directory))

    return {
        'directory': directory,
        'name': unique_name,
        'extension': extension,
        'original_filename': name,
        'full_path': os.path.join(current_app.config['UPLOAD_DIRECTORY'], relative_path)
    }
