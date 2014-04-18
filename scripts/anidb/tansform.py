#!/usr/bin/env python
# coding:utf-8
import json
i = open("output.json","r")
o = open("anidb.csv","w")
lines = i.readlines()
o.write("url,main_title,official_title,date,creator,director,genre,company,released,characters,description\n")
for line in lines:
    l = json.loads(line)
    o.write('"'+l["url"]+'",')
    o.write('"'+l["Main_Title"]+'",')
    o.write('"'+l["titles"].get("en","")+'",')
    o.write('"'+l["Year"]+'",')
    o.write('"'+', '.join(l["staffs"].get("Original Work",""))+'",')
    o.write('"'+', '.join(l["staffs"].get("Direction",""))+'",')
    if(type(l["Categories"])==list):
        o.write('"'+', '.join(l["Categories"])+'",')
    else:
        o.write(",")
    o.write('"'+', '.join(l["staffs"].get("Animation Work",""))+'",')
    o.write('"'+l["Type"]+'",')
    char = [j.get("char","") for j in l["casts"]]
    o.write('"'+', '.join(char)+'",')
    #print('"'+l.get("desc","")+'"\n')

    o.write('"'+l.get("desc","").encode("utf-8").replace('"',"'")[1:]+'"\n')
    #print "done"
o.close()

i.close()
