import add
import json
import os

names = ()
trustedNS = "ns1.afraid.org"

cdir = os.path.join(os.path.expanduser("~"),".config")
if not os.path.exists(cdir):
    os.makedirs(cdir)

config = os.path.join(cdir,"specialDNS.json")

def load():
    global names
    global trustedNS
    try:
        with open(config) as inp:
            names,trustedNS = json.load(inp)
    except Exception,e:
        print(e)
        initialize()

def save():
    with open(config,"wt") as out:
        json.dump((names,trustedNS),out,sort_keys=True, indent=4)

def initialize():
    global trustedNS
    doSave = False
    print("Enter a trusted name server (default "+trustedNS+")")
    ns = raw_input("> ").strip();
    if len(ns)>0:
        doSave = True
        trustedNS = ns
    add.add()
    if doSave:
        save()

load()
