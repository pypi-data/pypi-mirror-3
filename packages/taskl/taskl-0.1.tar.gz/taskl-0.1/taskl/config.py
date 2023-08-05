import os
import yaml

def conf():
    if os.access('.tlrc', 0):
        raw = open('.tlrc').read()
        data = yaml.load(raw) or {}
    else:
        data = {}

    return data

def save(data):
    rc_f = open('.tlrc', 'w')
    rc_f.write(yaml.safe_dump(data, default_flow_style=False))
    rc_f.close()

def opt(top, key=None, data=None):
    full = conf()

    opts = full.get(top) or {}
    if key is None:
        return opts

    if data is None:
        return opts.get(key)

    opts[key] = data

    full[top] = opts

    save(full)
 
