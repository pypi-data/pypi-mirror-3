import re

filename='0_04.orig'
filename_out='0_04.txt'

f=open(filename)
content=f.read()
f.close()


table = [re.split('\ \ +',r) for r in re.split('\n',content)][:-1]

f=open(filename_out,'w')
for r in table:
    row = "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (r[0],r[2],r[3],r[4],r[5],r[6],r[1])
    f.write(row)

f.close()


import re

tableb_filename='bufrtab_tableb.htm'
f=open(tableb_filename)
raw=f.read()
# Filter the first part.
raw=raw[raw.find('CLASS 00'):]
raw=re.sub('&nbsp;',' ',raw)
raw=re.sub('&gt;','>',raw)
raw=re.sub('\n','',raw)
#for classes in re.split('CLASS \d{2}',raw):
#import string
for classes in re.split('CLASS ',raw):
    #print classes
    if re.search('^\d{2}\ -',classes):
        filename = "0_%s.txt" % classes[:2]
        print "Writing the file: %s" % filename
        f=open(filename,'w')
    for line in re.findall('(0-\d{2}-\d{3}.*?)<br>',classes):
        line=re.sub('<.*?>','',line)
        tmp={'descriptor':line[0:10],'description':line[12:62],'unit':line[64:84],'scale':line[86:93],'ref.value':line[95:106],'datawidth':line[108:117],'mnemonic':line[119:]}
	print tmp
        for k in tmp: tmp[k]=tmp[k].strip()
	tmp['F']=tmp['descriptor'][0:1]
	tmp['X']=tmp['descriptor'][2:4]
	tmp['Y']=tmp['descriptor'][5:8]
	f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (tmp['descriptor'],tmp['scale'],tmp['ref.value'],tmp['datawidth'],tmp['mnemonic'],tmp['unit'],tmp['description']))
    f.close()


for x in tmp:
...   print x, descriptorstable[x[0],x[1],x[2]]

