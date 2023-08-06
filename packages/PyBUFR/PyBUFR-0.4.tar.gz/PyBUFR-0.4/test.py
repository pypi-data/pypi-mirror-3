#!/usr/bin/env python
# -*- coding: Latin-1 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import bufr
#filename = './test_data/aoml.bufr'
filename = './aoml.bufr'
f=open(filename,'r')
import pdb; pdb.set_trace()
header =f.read(20)
print header
#filename = './data/kars_dt.075509'
#f=open(filename,'r')
#f.read(39)
#filename = './data/wmo_sarep.bufr'
#f=open(filename,'r')


<<<<<<< local
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

=======
>>>>>>> other
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
<<<<<<< local
#descriptorstable = bufr.readdescriptor('/home/castelao/work/projects/BUFR/others/bufr_000340/bufrtables/B0000000000000007000.TXT')
#descriptorstable = bufr.descriptorstable()
=======
#descriptorstable = bufr.readdescriptor('/Users/castelao/work/projects/python/pybufr/old/BUFR/others/bufr_000340/bufrtables/B0000000000000007000.TXT')
# ====
#filename = './old/BUFR/pybufr/data/wmo_sarep.bufr'
filename = './test_data/sbuv2.bufr'
f=open(filename,'r')
>>>>>>> other

<<<<<<< local
=======
# ====
sectiondata={}

# Read section 0
sectiondata[0]=bufr.section0(f)

# Read section 1
sectiondata[1]=bufr.section1v4(f)

# Read section 2
if (sectiondata[1]['optionalsec'] != 0):
    sectiondata[2] = bufr.section2(f)

# ============================================================================
# ==== Read section 3
# ============================================================================

# Looks like a good first approach, but still needs:
#    - Think about an array index. I believe is the best way to reference were to store the output data
#    - Think about a rewind system for the walk. Maybe simply save a copy, of the data when the walk is called, and when the rewind is called, it only overload the copied data.
#    - Still missing how to deal with the repetitions (class 1).

# Read section 3
sectiondata[3] = bufr.section3(f)


import pdb; pdb.set_trace()

#import itertools

#x=bufr.DescriptorsTable()
x=bufr.TableB()
for F, X, Y in sectiondata[3]['FXY']:
    if F != 0:
        print F, X, Y
    else:
        print x[F][X][Y]


#class level0(UserList):
#    def __init__(self):
#        UserList.__init__(self)
#	return

class Descriptor0(UserDict):
    #def __init__(self,data):
    def __init__(self,F,X,Y):
        self.F=F
        self.X=X
        self.Y=Y
        self.data=globals()['descriptorstable'][F][X][Y]
        self.showed=False
        self.repetitions=1
        self.n=0
        return
    def walk(self):
        if self.showed==False:
            self.showed=True
            return self
        else:
            self.showed=False
            return
    def reset(self):
        self.showed=False
        return
	
#class WalkingList(UserList):
#    #def __init__(self):
#    def __init__(self,data=None):
#        UserList.__init__(self)
#	if data!=None:
#            self.data=data
#	self.i=-1
#	print "Merda: i",self.i
#	return
#    def walk(self):
#        self.i+=1
#	if self.i<len(self):
#	    return self.data[self.i]
#	return 

class Descriptors(UserList):
    def __init__(self,F=None,X=None,Y=None):
    #def __init__(self):
        UserList.__init__(self)
        #self.data=WalkingList()
        self.i=0
        self.repetitions=1
        self.n=0
        if (F != None) & (X != None) & (Y != None):
            self.append(F,X,Y)
        self.dataind=-1
        return
    def load(self,descriptorslist):
        """
        """
        i=0
        while i<len(descriptorslist):
            F,X,Y = descriptorslist[i] 
            #print "Processing: %s, %s, %s" % (F,X,Y)
            #print F,X,Y,(globals()['descriptorstable'][F][X][Y])
            if (F==0):
                self.data.append(Descriptor0(F,X,Y))
                self.dataind+=1
                print "self.dataind: ",self.dataind
                self.data[-1]['index']=self.dataind
                print self.data[-1]
            elif (F==1):
                tmp=Descriptors()
                tmp.dataind=self.dataind
                tmp.F=F
                tmp.X=X
                tmp.Y=Y
                if tmp.Y>0:
                    sublist=descriptorslist[i+1:i+1+X]
                    tmp.repetitions=Y
                    i+=X
                elif tmp.Y==0:
                    sublist=descriptorslist[i+2:i+2+X]
                    tmp.repfactor=Descriptor0(descriptorslist[i+1][0],descriptorslist[i+1][1],descriptorslist[i+1][2])
                    tmp.repetitions=None
                    i+=1+X
                for f,x,y in sublist:
                    if f==1:
                        print "Library not ready for hierarcheal repetitions"
                        self.data=None
                        return
                tmp.load(sublist)
                self.dataind=tmp.dataind
                self.data.append(tmp)
            elif (F==3):
                tmp=Descriptors()
                tmp.dataind=self.dataind
                tmp.F=F
                tmp.X=X
                tmp.Y=Y
                tmp.load(globals()['descriptorstable'][F][X][Y])
                self.dataind=tmp.dataind
                self.data.append(tmp)
            i+=1
        return
    def walk(self):
        #print "self.i: %s" % (self.i)
        output=self.data[self.i].walk()
        #print "output:",output
        #print "i:",i
        if (output == None):
            #print "i: %s, len(data): %s" % (self.i,len(self.data))
            if self.i<(len(self.data)-1):
                self.i+=1
                #self.n+=1
                if (self.data[self.i].F == 1) & (self.data[self.i].Y == 0) & ((self.data[self.i].n == 0)):
                    output = self.data[self.i].repfactor
                else:
                    output=self.data[self.i].walk()
            #if self.n<self.repetitions:
            #    self.i=0
            #if (self.i<len(self.data)):
            #    output=self.data[self.i].walk()
            else:
                self.n+=1
                if (self.n<self.repetitions):
                    self.reset()
                    output=self.data[self.i].walk()
                else:
                    output=None
        #else:
        #    #self.i+=1
        #    #print "I'm out"
        return output
    def reset(self):
        """ Reset the counter
        """
        self.data[self.i].reset()
        self.i=0
        return

#a=Descriptors()
#a.load(descriptorslist)

#    def append(self,F,X,Y):
#	#self.i=0
#	if (F==0):
#	    #self.data.append(WalkingList(globals()['descriptorstable'][F][X][Y]))
#	    #self.data.append(Descriptor0(globals()['descriptorstable'][F][X][Y]))
#	    #self.data.append(Descriptor0(F,X,Y))
#	    tmp=(Descriptor0(F,X,Y))
#	    #self.data.append((globals()['descriptorstable'][F][X][Y]))
#        elif (F==1):
#	    # Replicator class
#	    # X is the number of the following fields that should be replicated
#	    # Y if > 0 is the number of repetitions
#	    #   if = 0 means a delayed replicaton, and a class 0 31 should be the following field.
#	    print "Hey!!! F=1!!!"
#	    #self.nfields=X
#	    tmp=Descriptors()
#	    tmp.F=F
#	    tmp.X=X
#	    tmp.Y=Y
#	    self.insiderepetition=True
#	    #if Y==0:
#	    #    # Need to read n on the next field
#	    #    pass
#	    #else:
#	    #    self.n=Y
#	elif (F==3):
#	    tmp=Descriptors()
#	    tmp.F=F
#	    tmp.X=X
#	    tmp.Y=Y
#	    for f,x,y in globals()['descriptorstable'][F][X][Y]:
#	        print f,x,y
#	        #tmp.append(Descriptors(f,x,y))
#	        tmp.append(f,x,y)
#	    #self.data.append(tmp)
#	if self.insiderepetition==True
#	    #self.tmp.append(tmp)
#	    #if len(self.tmp)==self.tmp.X:
#	    #    self.insiderepetition==False
#	    #	self.data.append(self.tmp)
#	    self.data[-1].append(tmp)
#	else:
#            self.data.append(tmp)
#	return
#    def parser(self,descriptorlist):
#        for i,[F,X,Y] in enumerate(descriptorlist):
#	    print "i: %i" % i
#	    if F==0:
#	        #self.data.append(Descriptor0(globals()['descriptorstable'][F][X][Y]))
#		self.append(F,X,Y)
#            elif F==1:
#	        if Y>0:
#		    start=i+1
#		    end=i+1+X
#                elif Y==0:
#		    start=i+2
#		    end=i+2+X
#                tmp=Descriptors()
#                tmp.parser(descriptorlist[start:end])
#                print "tmp",tmp
#	    elif F==3:
#	        ##tmp=[]
#	        #tmp=Descriptors()
#	        #for f,x,y in globals()['descriptorstable'][F][X][Y]:
#	        #    #tmp.append(Descriptors(f,x,y))
#	        #    tmp.append(f,x,y)
#		#self.data.append(tmp)
#		self.append(F,X,Y)
#        return
#    def walk(self):
#        output=self.data[self.i].walk()
#	#print "output:",output
#	#print "i:",i
#	if (output == None):
#	    self.i+=1
#	    if (self.i<len(self.data)):
#                output=self.data[self.i].walk()
#            else:
#	        output=None
#	return output
	
# To test:
#filename = '/home/castelao/work/projects/BUFR/others/bufr_000340/data/wmo_sarep.bufr'
#f=open(filename,'r')
#lixo=f.read(30)

# x=Descriptor(3,1,1)
# x.walk()
# x.walk()
	    

#class Descriptors:
#    def __init__(self,descriptors):
#        self.descriptors=descriptors
#        self.i=-1
#        return
#    def walk(self):
#        self.i+=1
#        return self.descriptors[self.i]


sectiondata[3]={}
sectiondata[3]['sec3size'] = safe_unpack('>i',f.read(3))
sectiondata[3]['reserved'] = safe_unpack('>i', f.read(1))
sectiondata[3]['nsubsets'] = safe_unpack('>i', f.read(2))
sectiondata[3]['xxxx'] = safe_unpack('>i', f.read(1))

n_descriptors = (sectiondata[3]['sec3size']-7)/2
sectiondata[3]['descriptors']=Descriptors()
tmp=[]
for i in range(n_descriptors):
    FX = safe_unpack('>i', f.read(1))
    F = FX/64
    X = FX%64
    Y = safe_unpack('>i', f.read(1))
    #sectiondata[3]['descriptors'].append([FX,F,X,Y])
    #sectiondata[3]['descriptors'].append(F,X,Y)
    tmp.append([F,X,Y])
    print F,X,Y
    #if F == 0:
    #    print descriptorstable[F][X][Y]
sectiondata[3]['descriptors'].load(tmp)
>>>>>>> other
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

