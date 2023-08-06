# -*- coding: utf-8 -*-

import os

def after_built(*pros, **attrs):
    tpl = attrs['env'].get_template('listing.htm')
    sc = attrs['exports']['category']['structure']
    for c in sc.keys():
        cat_loc = attrs['build_loc']+'/cat'
        if not os.path.exists(cat_loc):
            os.makedirs(cat_loc)
        with open('%s/cat/%s.htm'%(attrs['build_loc'],c),'w') as f:
            f.write(tpl.render(site=attrs['config'],selected_cat=sc[c]))
            attrs['logger'].info('\"cat/%s.htm\" has been built.'%c)

def export(*pros, **attrs):
    structure = {}
    for c in attrs['config']['categories']:
        structure[c] = []
    for p in attrs['listable']:
        if 'cat' in p.keys():
            structure[p['cat']].append(p)
    return {'structure':structure}
