#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from pprint import pprint
import json
import random

import networkx
from networkx.readwrite import json_graph
import web
import pystache
from datertots.core import (
        xls_to_dicts,
        writeToXls,
        )


g = networkx.Graph()

def simpl(stuff):
    for thing in stuff:
        d = {}
        for k, v in thing.items():
            d[ k.lower() ] = v.lower()
        yield d

def idify(string):
    string = string.strip()
    notOK = list(u"()?.:-–—,!@'\"")
    string = string.lower()
    for s in notOK:
        string = string.replace(s, '')
    string = string.replace(' ', '_')
    return string


def add_nodes(items):
    for d in simpl(items):
        g.add_node(d['name'], **d)

def build_graph_from_sheet():
    fname = "contributions.xlsx"
    folder = "data"
    path = os.path.join(folder, fname)
    data = xls_to_dicts(path, "Sheet1")
    topics = (
            "Building Infrastructure and Resource Effectiveness",
            "Networking Smarter Cities",
            "Matching Economic and Democratic Goals",
            "Designing and Governing Adaptive Cities and Regions ",
            "Developing Housing and Jobs in Healthy Communities",
            "Praxis",
            )
    projects = {}
    # each of these is s list of projects/publications for one person
    # I therefore have enough info to make a ton of links
    # show me all the projects. Are there any repeats?
    for d in data:
        for k in d:
            if k in topics: # is it a topic?
                project = d[k] # it's a project
                if project and len(project) > 5:
                    if project not in projects: #it's new
                        p = {}
                        p['names'] = d['name']
                        p['detail'] = project
                        for t in topics:
                            if t == k:
                                p[t] = 'x'
                            else:
                                p[t] = 'o'
                        projects[project] = p
                    else: #it exists
                        print "found a repeat project"
                        #set this category to x
                        projects[project][k] = 'x'
                        if d['name'] not in p['names']:
                            p['names'] += ' | ' + d['name']
    project_list = [projects[k] for k in projects]
    writeToXls('data/projects.xls', project_list)
    print 'projects written'

def newgraph():
    fname = "projects2.xls"
    folder = "data"
    path = os.path.join(folder, fname)
    projects = xls_to_dicts(path, "projects")
    people = xls_to_dicts(path, "people")
    topics = xls_to_dicts(path, "topics")
    # add the nodes to the graph
    # be sure to construct ids
    for person in people:
        person['id'] = idify(person['name'])
        g.add_node(person['id'], **person)
    for topic in topics:
        topic['id'] = idify(topic['name'])
        g.add_node(topic['id'], **topic)
    for project in projects:
        p = project['name']
        pcore = {
                'name':project['name'],
                'description':project['detail'],
                'type':project['type'],
                }
        pcore['id'] = idify(p)
        if p not in g:
            g.add_node(pcore['id'], **pcore)
        for k in project:
            if idify(k) in g:
                if project[k] == 'x':
                    # link the project to the topic
                    g.add_edge(idify(k), idify(p))
                    # link the person to the topic
                    g.add_edge(idify(k), idify(project['names']))
                    #print "linked %s to %s" % (k, p)
        if idify(project['names']) not in g:
                print "can't find", project["names"]
        else:
            g.add_edge(idify(project['names']), idify(p))
            #print "linked %s to %s" % (project['names'], p)

def print_nodes():
    import pystache
    outpath = "www/index.html"
    skeletemplate = "templates/skeletemplate.mustache"
    nodes = g.nodes(data=True)
    g_guide = {}
    for n in nodes:
        g_guide[ n[0] ] = g.neighbors(n[0])
    nodes = [n[1] for n in nodes]
    random.shuffle(nodes)
    edges = g.edges()
    context = {
            'nodes':nodes,
            'graph':json.dumps(g_guide),
            }
    template = open(skeletemplate, 'r').read()
    f = open(outpath, 'w')
    f.write( pystache.render(template, context).encode('utf-8') )
    f.close()


def graph_test():
    g.add_node('h')
    g['h']['i'] = 'illo'


def build_graph():

    folder = "/Users/benjamin/projects/mitdusp/data/"
    fname = "graph_data.xlsx"


    path = os.path.join(folder, fname)

    sheets = [
            "faculty",
            "topics",
            "affiliations",
            "problems",
            "methods",
            ]

    faculty = xls_to_dicts(path, "faculty")
    topics = xls_to_dicts(path, "topics")
    affiliations = xls_to_dicts(path, "affiliations")
    problems = xls_to_dicts(path, "problems")
    methods = xls_to_dicts(path, "methods")

    add_nodes(faculty)
    add_nodes(topics)

    for d in simpl(affiliations):
        if d['group'] not in g:
            g.add_node( d['group'], **{
                'name': d['group'],
                'type': 'program group',
                })
        g.add_edge( d['name'], d['group'], **{
            'level': d['level'],
            })

    for d in simpl(problems):
        if d['target'] not in g:
            g.add_node( d['target'], **{
                'name': d['target'],
                'type': 'topic',
                })
        g.add_edge( d['start'], d['target'])

def getAtt(node, att):
    props = g[node]
    for k in props:
        if k == att:
            return props[k]
    return None

def hasAtt(node, att, value):
    val = getAtt(node, att)
    if val == value:
        return True
    return False

def nodeEdges(node):
    edges = networkx.edges(g, node)
    return edges

def buildVisGraph():
    degrees = g.degree()
    ok_nodes = []
    nodes = []
    edges = []
    enum = {}
    groups = []
    for n in degrees:
        if degrees[n] > 0:
            ok_nodes.append(n)
    for name, node in g.nodes(data=True):
        if name in ok_nodes:
            if 'type' in node:
                if node['type'] == 'program group':
                    groups.append( name )
                    node['class'] = name
                else:
                    node['class'] = node['type']
                if node['type'] in ('faculty', 'topic', 'program group'):
                    nodes.append(node)
                    enum[name] = len(enum)
    for n0, n1, data in g.edges(data=True):
        edge = {}
        if n0 in enum and n1 in enum:
            edge['source'] = enum[n0]
            edge['target'] = enum[n1]
        else:
            continue
        if 'level' in data:
            if data['level'] == 'primary':
                edge['value'] = 20
            elif data['level'] == 'secondary':
                edge['value'] = 10
        else:
            edge['value'] = 1
        if n0 in groups:
            edge['class'] = n0
        if n1 in groups:
            edge['class'] = n1
        if 'class' in edge:
            edge['class'] += ' link'
        else:
            edge['class'] = 'link'
        edges.append(edge)
    d = {
            "nodes": nodes,
            "links": edges,
            }
    outpath = "www/data.js"
    f = open(outpath, 'w')
    f.write('var graph = ')
    f.write(json.dumps(d, indent=2))
    f.write(';\n')
    f.close()
    print 'done'




def getData():
    #pprint( g.nodes() )
    #pprint( g.edges() )
    pass


#build_graph()
#buildVisGraph()
#build_graph_from_sheet()
#graph_test()
newgraph()
print_nodes()


