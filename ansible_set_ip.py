import sys

inputfile = 'inputfile.txt'
outfile_name = sys.argv[1]
service_name = sys.argv[2]
role_type = sys.argv[3]
service_template = "{}_template.txt".format(service_name)

sections = []

with open(inputfile) as f:
   lines = f.read().strip()

ip=lines.split("\n")
st_out=""
mas_out=""
sla_out=""

with open(service_template) as f:
   sections = f.read().strip().split("\n").strip()

if role_type == 'standalone' :
    if len(ip) == 1 :
        st_out=ip[0]
    if len(ip) > 1 :
        mas_out=ip[0]
        sla_out="\n".join(ip[1:])

if role_type == 'non-standalone' :
    st_out=ip[0]
    mas_out=ip[1]
    sla_out="\n".join(ip[2:])

with open(outfile_name,'at') as out:
    try:
        out.write('{}\n{}\n'.format(sections[0],st_out))
        out.write('{}\n{}\n'.format(sections[1],mas_out))
        out.write('{}\n{}\n'.format(sections[2],sla_out))

    finally:
        out.close()

print(open(sys.argv[1],'rt').read())
