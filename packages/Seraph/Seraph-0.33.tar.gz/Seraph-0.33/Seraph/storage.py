# -*- coding: utf-8 -*-

site_yaml="""name: "[site name]"
author: 
#root: your.domain.com
title: "[Blog title]"
categories:
    - one
    - two
specific:
    index: index
    about: about"""

base_css="""/*  css blocks here for the template "template/base.htm". */"""

post_css="""/*  css blocks here for the template "template/post.htm". */"""

post_indicating_htm="""title: This is title.
cat: one
time: 2012-12-18 00:00
==========

This is content of the post.
*bold* _italic_
#A big font."""

source_index_htm = """==========
This is content in sources/index.htm ."""

template_base_htm = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="{{ site.root }}/styles/base.css" type="text/css" media="screen" charset="utf-8" />
    <link rel="stylesheet" href="styles/fontello.css">
        {% block css %}{% endblock %}
    <title>{% block title %}Elegies{% endblock %}</title>
</head>
    <body>
    <div id="header">
        <ul id="navbar">
            <li><a href="{{ site.root }}/index.htm">home</a></li>
             <li><a href="{{ site.root }}/posts/index.htm"}}">archieve</a></li>
            {% for cat in site.categories %}
            <li><a href="{{ site.root }}/cat/{{ cat }}.htm">{{ cat }}</a></li>
        {% endfor %}</ul>
    </div>
    <div id="container">{% block contents %}{% endblock %}</div><div id="footer">Powered by <a href="https://github.com/wontoncc/Seraph/">Seraph</a> | <a href="{{ site.root }}/rss.xml">RSS<a></div>
    </body>
 </html>"""

template_index_htm= """{% extends "base.htm" %}
{% block contents %}
<div>{{ page.content }}</div>
{% endblock %}"""

template_listing_htm = """{% extends 'base.htm' %}
{% block contents %}
<ul class="listing">
    {% for post in selected_cat %}
    <li class="listing title">{{ post.time }} - <a href="{{ site.root }}/{{ post.rlink }}">{{ post.title }}</a></li>
    {% endfor %}
</ul>
{% endblock %}
"""

template_post_htm = """{% extends "base.htm" %}
{% block css %}
<link rel="stylesheet" href="{{ site.root }}/styles/post.css" type="text/css" media="screen" charset="utf-8" />
{% endblock %}
{% block title %}{{ page.title }} @ Elegies{% endblock %}
{% block contents %}
<div class="post title">{{ page.title }}</div>
<div class="post time">{{ page.time }}</div>
<div class="post content">{{ page.content }}</div>
{% endblock %}
"""

extensions_sample = """
# -*- coding: utf-8 -*-
def export(**attrs):
    return {}

def after_built(**attrs):
    pass
"""

inital_site = {
        "site.yaml":"site_yaml",
        "source":{
            "posts":{
                "index.htm":"source_index_htm",
                "post-indicating.htm":"post_indicating_htm"
                },
            "index.htm":"source_index_htm"
            },
        "templates":{
            "base.htm":"template_base_htm",
            "index.htm":"template_index_htm",
            "post.htm":"template_post_htm",
            "listing.htm":"template_listing_htm"
            },
        "extensions":{
            "sample.py":"extensions_sample"
            }
        }
