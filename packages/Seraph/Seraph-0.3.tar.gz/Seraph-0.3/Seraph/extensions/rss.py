# -*- coding: utf-8 -*-

from xml.dom.minidom import Document
from Seraph.common import Logger

def parseRss(l, info):
    feed = Document()
    rss = feed.createElement("rss")
    channel = feed.createElement("channel")
    title = feed.createElement("title")
    title_text = feed.createTextNode(info["title"])
    link = feed.createElement("link")
    link_text = feed.createTextNode(info["root"])
    title.appendChild(title_text)
    link.appendChild(link_text)
    channel.appendChild(title)
    channel.appendChild(link)
    for p in l:
        item = feed.createElement('item')
        pair = {\
            'title':p['title'], 'description':p['content'],\
            'link':info['root']+'/'+p['rlink']}
        for n in pair.keys():
            node = feed.createElement(n)
            node_text = feed.createTextNode(pair[n])
            node.appendChild(node_text)
            item.appendChild(node)
        channel.appendChild(item)
    rss.appendChild(channel)
    feed.appendChild(rss)
    return feed.toxml()

def after_built(listable=[],config={},build_loc="",logger=None):
    with open(build_loc+"/rss.xml","w") as f:
        f.write(parseRss(listable,config))
    logger.info("RSS generated.")

def export(listable, site, pages, newest):
    return {}
