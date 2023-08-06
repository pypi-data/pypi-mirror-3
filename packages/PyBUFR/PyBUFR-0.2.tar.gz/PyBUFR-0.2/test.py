#!/usr/bin/env python
# -*- coding: Latin-1 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import bufr
filename = './data/aoml.bufr'
f=open(filename,'r')
f.read(20)
#filename = './data/kars_dt.075509'
#f=open(filename,'r')
#f.read(39)
#filename = './data/wmo_sarep.bufr'
#f=open(filename,'r')


sectiondata={}
# Read section 0
sectiondata[0]=bufr.section0(f)
# Read section 1
if sectiondata[0]['version']==3:
    sectiondata[1]=bufr.section1v3(f)
elif sectiondata[0]['version']==4:
    sectiondata[1]=bufr.section1v4(f)
# Read section 2

if (sectiondata[1]['optionalsec'] != 0):
    print "Atention!!!! Not ready to read the section 2"

# Read section 3
sectiondata[3]=bufr.section3(f)


# ============================================================================
for k in sectiondata:
    print k,sectiondata[k]
    for kk in sectiondata[k]:
        print kk,sectiondata[k][kk]



# ============================================================================

import struct
#from UserDict import UserDict
#from UserDict import IterableUserDict
#from UserList import UserList

#if (content[0:4]!='BUFR') | (content[-4:]=='7777'):
#    print "Don't looks like a BUFR file"

def safe_unpack(fmt,var):
    n=struct.calcsize(fmt)
    fullvar=var
    for i in range(n-len(var)):
        fullvar='\x00'+fullvar
    output=struct.unpack(fmt,fullvar)
    return output[0]
# ====

def Denary2Binary(n):
    '''convert denary integer n to binary string bStr'''
    bStr = ''
    if n < 0: raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    return bStr

#descriptors = readdescriptor('table-B.txt')
#descriptorstable = bufr.readdescriptor('/home/castelao/work/projects/BUFR/others/bufr_000340/bufrtables/B0000000000000007000.TXT')
#descriptorstable = bufr.descriptorstable()

# ============================================================================
# ==== Read section 4
# ============================================================================

def int2bin(n, count=8):
    """returns the binary of integer n, using count number of digits"""
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

class BinaryData:
    def __init__(self,f,size):
        self.f=f
        dir(self.f)
        self.size=size
        self.n=0
        self.bitline=''
        return
    def read(self,nbits):
        print nbits,len(self.bitline)
        while (nbits>len(self.bitline)):
            #self.bitline+=int2bin(safe_unpack('>i', self.f.read(1)))
            #print dir(self.f)
            self.n+=1
            if (self.n>=self.size):
                print "Trying to read more then was supposed"
                return
            x=self.f.read(1)
            self.bitline+=int2bin(safe_unpack('>i', x))
        tmp = self.bitline
        output=self.bitline[:nbits]
        self.bitline=self.bitline[nbits:]
        print "BinaryData: ",tmp, "###", output, "###", self.bitline
        return output



sectiondata[4]={}

sectiondata[4]['size'] = safe_unpack('>i',f.read(3))
sectiondata[4]['reserved'] = safe_unpack('>i', f.read(1))

# Need to change it. Should read variable by variable.
#rownbits=8
#bitline=''
#for i in range(sectiondata[4]['size']-4):
#    bitline+=f.read(1)
#    bitline+=int2bin(safe_unpack('>i', f.read(1)))
binarydata=BinaryData(f,sectiondata[4]['size'])
sectiondata[4]['data']={}
fin=0
#sizes=[7,10,12,4,6,5,6,10,8]
#for s in sizes:
sectiondata[3]['descriptors'].reset()
d=sectiondata[3]['descriptors'].walk()
#for i in range(40):
soma=0
while d:
    print d
    s=d['bitwidth']
    #ini=fin
    #fin+=s
    b=binarydata.read(s)
    print "Read: ", b
    soma+=s
    print "Readed until now:", soma
    if bufr.datatype(d['unit'])=='int':
        #output = int(bitline[ini:fin],2)
        output = int(b,2)
        output = (output+d['reference'])
        print "Aqui:",int(b,2),d['reference'],output
        if d['scale'] != 0:
            #output = int(b,2)
            #output = output/10.**(d['scale'])
            # While I can't guarantee that scale will come as int.
            output = output/10.**(int(d['scale']))
    elif(bufr.datatype(d['unit'])=='str'):
        output="".join([struct.pack('>i',int(b[j*8:j*8+8],2))[-1] for j in range(len(b)/8)])
    else:
        output = b
    if d.X not in [30,31,32]:
        if d['index'] not in sectiondata[4]['data']:
            sectiondata[4]['data'][d['index']]=[]
        sectiondata[4]['data'][d['index']].append(output)
        #print s,ini,fin,d['name'],bitline[ini:fin],sectiondata[4]['data'][-1]
        print s,b,sectiondata[4]['data'][d['index']][-1]
    else:
        print "HEYHYEHYE", d.X,b,int(b,2),d.level
        if len(d.level)==1:
            sectiondata[3]['descriptors'][d.level[0]].repetitions=int(b,2)
        elif len(d.level)==2:
            sectiondata[3]['descriptors'][d.level[0]][d.level[1]].repetitions=int(b,2)
        elif len(d.level)==3:
            sectiondata[3]['descriptors'][d.level[0]][d.level[1]][d.level[2]].repetitions=int(b,2)
    lixo=raw_input()
    d=sectiondata[3]['descriptors'].walk()

#for i in range(sectiondata[4]['size']-4-8):
#    sectiondata[4]['data'].append(safe_unpack('>i', f.read(1)))

# Read section 5
sectiondata[5]={'closer':f.read(4)}


for k in sectiondata:
    print "%s" % k
    for kk in sectiondata[k]:
        print "   %s: %s" % (kk,sectiondata[k][kk])

