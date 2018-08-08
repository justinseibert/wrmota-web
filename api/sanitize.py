import os
import string
from re import sub, match, search, IGNORECASE
from datetime import datetime

from flask import current_app

from wrmota.api import hashes as Hash

def make_ascii(text):
    return text.decode('unicode_escape').encode('ascii','ignore')

def make_unicode(text):
    printable = set(string.printable)
    text = filter(lambda a:a in printable, text)
    text = sub(r'(.*)\s+$', r'\1', text)
    return unicode(text).decode('unicode_escape').encode('utf-8','ignore')

def website(item):
    item = sub(r'\s*',r'',item)
    item = sub(r'(/home\.html|/)$',r'',item)
    item = sub(r'^(https*://)*(www\.)*(.*)',r'\3',item)
    return item

def spaces(item):
    item = sub(r'\s{2,}', r' ', item)
    item = sub(r'^\s*|\s*$', r'', item)
    return item

def remove_spaces(item):
    return sub(r'\s', r'', item)

def remove_dots(item):
    return sub(r'\.', r'', item)

def weird_stuff(item):
    return sub(r'[\s,\.\/;\'\[\]\`\-=*\/<>\?:"\{\}\|\\~!@#$%\^&\*\(\)_\+]', r'', item)

def remove_email_confidentiality_statement(item):
    print('removing confidential')
    item = str(item)
    return sub(r'\s*\*{4}\s*THE INFORMATION CONTAINED IN THIS EMAIL.*$', r'', item)

def brick_as_letter(item):
    return str(string.ascii_uppercase[item])

def visitor_status(item):
    return 'visiting' if item == 1 else 'local'

def email_sender(item):
    m = match(r'(.*)\s+\<(.*[@]*)\>', item)
    if m:
        return {
            'name': m.group(1),
            'email': m.group(2)
        }
    else:
        return False

def is_code(item):
    has_code = search(r'[a-dA-D]{4}',item)
    if has_code:
        return has_code.group(0).upper()
    else:
        return False

def get_extension(item, withdot=False, split=False):
    parts = item.rsplit('.', 1)
    name = parts[0]
    extension = parts[1].lower()
    extension = '.{}'.format(extension) if withdot else extension

    if split:
        return {
            'name': name,
            'extension': extension
        }
    else:
        return extension

def date_directory(style):
    folders = ''.join('%{}/'.format(i) for i in style)
    return datetime.now().strftime(folders)

def media_file(name, mediatype=None):
    directory = date_directory('MIS')
    if mediatype:
        directory = mediatype + '/' + directory
    unique_name = Hash.generate_token(8).decode('utf-8')
    extension = get_extension(name)
    relative_path = '{}{}.{}'.format(directory,unique_name,extension)

    try:
        path = os.path.join(current_app.config['UPLOAD_DIRECTORY'],directory)
        os.makedirs(path)
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
