from re import sub, match, IGNORECASE

def website(item):
    item = sub(r'\s*',r'',item)
    item = sub(r'(/home\.html|/)$',r'',item)
    item = sub(r'^(https*://)*(www\.)*(.*)',r'\3',item)
    return item

def spaces(item):
    item = sub(r'\s{2,}', r' ', item)
    item = sub(r'^\s*|\s*$', r'', item)
    return item

def code(item):
    has_code = search(r'[a-dA-D]{4}',item)
    if has_code:
        return has_code.group(0).upper()
    else:
        return False
