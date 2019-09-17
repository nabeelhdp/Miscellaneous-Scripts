#!/usr/bin/python

import sys

inputfile = sys.argv[1]
outfile_name = sys.argv[2]
service_name = sys.argv[3]
role_type = sys.argv[4]
service_template = "{}_template.txt".format(service_name)
section_content={}
sections = []

with open(inputfile) as f:
  inputlines_ = f.read().strip()

# Remove empty element in list \
# may get generated at end due to trailing newline
# or due to other issues
inputlines = filter( None, inputlines_.split("\n"))

with open(service_template) as f:
    sections_ = f.read().strip().lower().split("\n")
    # Remove empty element in list \
    # may get generated at end due to trailing newline
    # or due to other issues
    sections =  filter(None, sections_)
    for section in sections:
      section_content[section]=[]

for inputline in inputlines:
    type=inputline.split(" ")[-1].split("=")[1]
    section_content[type].append(inputline.split(" ")[:-1])
    
with open(outfile_name,'at') as out:
   try:
       for s in section_content:
           if len(section_content[s])>0:
               out.write('{}\n'.format(s))
               for entries in section_content[s]:
                   out.write('{}\n'.format(entries))


   finally:
       out.close()

print(open(sys.argv[1],'rt').read())
