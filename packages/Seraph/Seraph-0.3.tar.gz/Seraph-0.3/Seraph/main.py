#!usr/env/bin python
# -*- coding:utf-8 -*-

import yaml,markdown
from jinja2 import Environment, FileSystemLoader
import jinja2
import os,sys,time
import getopt
from Seraph.common import readf,sep,Logger
import Seraph

class Page(dict):
    def __init__(self, fl_loc):
        f = open(fl_loc,'r',encoding='utf-8')
        self['title'] = None
        self['build_loc'] = fl_loc.replace('source','build')
        self['rlink'] = self['build_loc'].replace('build/','')
        self['build_dir'] = self['build_loc'].replace(\
                os.path.basename(self['build_loc']),'')
        self['cat'] = ''
        self['raw_time'] = os.stat(fl_loc).st_ctime
        __temp_time=list(time.localtime(self['raw_time'])[:5])
        for i in range(len(__temp_time)):
            if len(str(__temp_time[i])) == 1:
                __temp_time[i] = "0%d" % __temp_time[i]
        self['time'] = None

        def head_load(d):
            for k in d.keys():
                self[k] = d[k]

        (raw_head, self['raw']) = sep(fl_loc)
        head_dict = yaml.load(raw_head)
        if head_dict:
            head_load(head_dict)

        if self['time'] == None:
            self['time'] =  '%s-%s-%s %s:%s'%tuple(__temp_time)
        else:
            self['raw_time'] = time.mktime(time.strptime(self['time'].strip(),\
                    "%Y-%m-%d %H:%M"))
        self['short_time'] = self['time'][:11]
        self['cat'] = self['cat'].strip()
        f.close()
        self['content'] = markdown.markdown(self['raw'])
        self['name'] = os.path.basename(fl_loc).split('.')[0]

class Site():
    def __init__(self, local=False):
        self.logger = Logger()
        self.config = yaml.load(readf('site.yaml'))
        if (not 'root' in self.config.keys()) or (local == True):
            self.logger.info('Local Mode ON.')
            self.config['root'] = os.getcwd()+"/build"
            self.logger.info('  -- in \"%s\".'%self.config['root'])
        self.logger.info('Config site.yaml loaded.')
        self.structure = {}
        for cat in self.config['categories']:
            self.structure[cat] = []
        self.__timeline, self.pages, self.listable = [], [], []
        self.__time_to_page = {}
        self.__load(['source'])
        self.__timeline.sort()
        self.__timeline.reverse()
        self.__newest = None
        for t in self.__timeline:
            p = self.__time_to_page[t]
            self.pages.append(p)
            if p['cat'] in self.structure.keys():
                self.structure[p['cat']].append(p)
            if not p['title'] == None:
                self.listable.append(p)
        self.__newest = self.listable[0]
        self.logger.info('All pages got ready to be built.')

        self.__extensions, self.__e_exports = {},{}
        try:
            sys.path.append(os.getcwd()+"/extensions")
            for i in os.listdir("extensions"):
                if ".py" in i:
                    module_name = i.split(".")[0]
                    self.__extensions[module_name] = __import__(module_name)
            from Seraph.extensions.rss import parseRss
        finally:
            pass
        self.__extensions['rss'] = Seraph.extensions.rss

    def __load(self, loc):
        all_file = True
        for i in range(len(loc)):
            entry = loc[i]
            if os.path.isdir(entry):
                all_file = False
                fl = os.listdir(entry)
                loc.remove(entry)
                for j in range(len(fl)):
                    fl[j] = "%s/%s" % (entry, fl[j])
                loc.extend(fl)
            else:
                p = Page(entry)
                if not p['raw_time'] in self.__timeline:
                    self.__timeline.append(p['raw_time'])
                    self.__time_to_page[p['raw_time']] = p
        if all_file:
            return
        self.__load(loc)

    def __tpl_render(self,tpl,p=None,sc=None):
        return tpl.render(
                    newest=self.__newest,
                    pages=self.pages,
                    page=p,
                    site=self.config,
                    listable=self.listable,
                    structure=self.structure,
                    selected_cat=sc,
                    extensions=self.__e_exports)

    def build(self):
        jinja_env = Environment(loader=FileSystemLoader(\
                os.getcwd()+'/templates'))
        exports = {}
        for e in self.__extensions.keys():
            self.__e_exports[e] = getattr(self.__extensions[e],"export")(
                    listable=self.listable,
                    site=self.config,
                    pages=self.pages,
                    newest=self.__newest)
        for p in self.pages:
            tpl = jinja_env.get_template('post.htm')
            if p['name'] in self.config['specific'].keys():
                _tpl = self.config['specific'][p['name']]
                tpl = jinja_env.get_template(_tpl+".htm")
            output = self.__tpl_render(tpl,p)
            if not os.path.exists(p['build_dir']):
                self.logger.info('Folder \"%s\" made.'%p['build_dir'])
                os.makedirs(p['build_dir'])
            f = open(p['build_loc'],'w+',encoding='utf-8')
            f.write(output)
            f.close()
            self.logger.info("Page \"%s\" built."%p['build_loc'])
        for cat in self.structure.keys():
            tpl = jinja_env.get_template('listing.htm')
            if not os.path.exists('build/tags'):
                os.makedirs('build/tags')
            f = open('build/tags/%s.htm'%cat,'w',encoding='utf-8')
            output = self.__tpl_render(tpl,p,self.structure[cat])
            f.write(output)
            f.close()
            self.logger.info('Tag list \"%s\" built.'%cat)
        tpl = jinja_env.get_template('listing.htm')
        output = self.__tpl_render(tpl,None,self.listable)
        f = open('build/posts/index.htm','w',encoding='utf-8')
        self.logger.info('Archieve list built.')
        f.write(output)
        f.close()

        for e in self.__extensions.keys():
            getattr(self.__extensions[e],"after_built")(
                    listable=self.listable,
                    config=self.config,
                    build_loc=os.getcwd()+"/build",
                    logger=self.logger)
