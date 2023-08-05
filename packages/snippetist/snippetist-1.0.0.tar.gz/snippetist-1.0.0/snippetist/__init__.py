#!/usr/bin/env python
import pystache
import yaml
import uuid
import copy
import os

def readtpl(name):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), name + '.mustache')) as fl:
        return fl.read()

def mksnippet(src):
    src = src.split('\n')
    whitespc = len([True for ch in src[1] if ch == ' '])
    return {'name': src[0],
            'cont': '\n'.join([ln[whitespc-1:] for ln in src[1:]]) + '\n'}

def tabify(snip):
    snip['cont'] = '\t' + '\n\t'.join(snip['cont'].split('\n'))[:-1]
    return snip

def mkfiles(data, template, extension=''):
    files = {}
    tpl = readtpl(template)
    for snip in data['snippets']:
        data.update(snip)
        files[snip['name'] + extension] = pystache.render(tpl, data)
    return files

def process(txt, name):
    txt = txt.split('\n---\n')
    data = yaml.load(txt[0])
    data['uuid'] = uuid.uuid4()
    data['snippets'] = map(mksnippet, txt[1].split('\n\n'))
    vimdata = copy.deepcopy(data)
    vimdata['snippets'] = map(tabify, vimdata['snippets'])
    return {name + '-vim/snippets': {name + '.snippets': pystache.render(readtpl('vim'), vimdata)},
            name + '-emacs/' + data['emacs_mode']: mkfiles(data, 'emacs'),
            name + '.tmbundle/Snippets': mkfiles(data, 'textmate', '.tmSnippet')}