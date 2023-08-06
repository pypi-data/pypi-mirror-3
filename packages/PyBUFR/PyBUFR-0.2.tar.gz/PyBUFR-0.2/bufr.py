#!/usr/bin/env python
# -*- coding: Latin-1 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import struct
#from UserDict import UserDict
from UserDict import IterableUserDict

##############################################################################
#### SECTION 0
##############################################################################
class section0(IterableUserDict):
    """A class to read the section 0 of a BUFR file
    """
    def __init__(self,f):
        """
        """
        self.f = f
        self.data={}
        self.data['ident'] = self.f.read(4)
        self.data['size'] = _unpack_int(self.f.read(3))
        self.data['version'] = _unpack_int(self.f.read(1))
        return

##############################################################################
#### SECTION 1
##############################################################################
class section1v3(IterableUserDict):
    """A class to read the section 1 of a BUFR file version 3

       Updated following the description on 
         http://www.wmo.int/pages/prog/www/WMOCodes/Operational/BUFR/FM94REG-11-2007.pdf
         , which don't agree with the previous reference that I used.
    """
    def __init__(self,f):
        """
        """
        self.f = f
        self.data={}
        self.read()
        return
    def read(self):
        self.data['sec1size'] = _unpack_int(self.f.read(3))        # 1-3
        self.data['mastertablenumber'] = _unpack_int(self.f.read(1))   # 4
        self.data['originatedsubcenter'] = _unpack_int(self.f.read(1))        # 5
        self.data['originatedcenter'] = _unpack_int(self.f.read(1))    # 6
        self.data['updateversion'] = _unpack_int(self.f.read(1))  # 7
        self.data['optionalsec'] = _unpack_int(self.f.read(1))    # 8    Atention here!!!
        self.data['datacategory'] = _unpack_int(self.f.read(1))   # 9 (Table A)
        self.data['datasubcategory'] = _unpack_int(self.f.read(1)) # 10
        #self.data['localsubcategory'] = _unpack_int(self.f.read(1))   #
        self.data['mastertableversion'] = _unpack_int(self.f.read(1)) # 11
        self.data['localtableversion'] = _unpack_int(self.f.read(1))  # 12
        # ====================================================================
        year = _unpack_int(self.f.read(1))            # 13
        if year==100: year=0
        self.data['year'] = 2000+year
        # ====================================================================
        self.data['month'] = _unpack_int(self.f.read(1))          # 14
        self.data['day'] = _unpack_int(self.f.read(1))               # 15
        self.data['hour'] = _unpack_int(self.f.read(1))              # 16
        self.data['minute'] = _unpack_int(self.f.read(1))            # 17
        n_reserved = self.data['sec1size'] - 17
        self.data['localuse'] = _unpack_int(self.f.read(n_reserved)) # 18-
        return

class section1v4(IterableUserDict):
    """A class to read the section 1 of a BUFR file version 4
    """
    def __init__(self,f):
        """
        """
        self.f = f
        self.data={}
        self.read()
        return
    def read(self):
        self.data['sec1size'] = _unpack_int(self.f.read(3))        # 1-3
        self.data['mastertablenumber'] = _unpack_int(self.f.read(1))   # 4
        self.data['originatedcenter'] = _unpack_int(self.f.read(2))    # 5-6
        self.data['originatedsubcenter'] = _unpack_int(self.f.read(2))        # 7-8
        self.data['updateversion'] = _unpack_int(self.f.read(1))  # 9
        self.data['optionalsec'] = _unpack_int(self.f.read(1))    # 10    Atention here!!!
        self.data['datacategory'] = _unpack_int(self.f.read(1))   # 11 (Table A)
        self.data['datasubcategory'] = _unpack_int(self.f.read(1))    # 12
        self.data['localsubcategory'] = _unpack_int(self.f.read(1))   # 13
        self.data['mastertableversion'] = _unpack_int(self.f.read(1)) # 14
        self.data['localtableversion'] = _unpack_int(self.f.read(1))  # 15
        self.data['year'] = _unpack_int(self.f.read(2))            # 16-17
        self.data['month'] = _unpack_int(self.f.read(1))          # 18
        self.data['day'] = _unpack_int(self.f.read(1))               # 19
        self.data['hour'] = _unpack_int(self.f.read(1))              # 20
        self.data['minute'] = _unpack_int(self.f.read(1))            # 21
        self.data['second'] = _unpack_int(self.f.read(1))            # 22
        n_missing=self.data['sec1size']-22
        if n_missing>0:
            self.data['localuse'] = self.f.read(n_missing)
        return



##############################################################################
#### Descriptor tables
##############################################################################


class DescriptorsTable(IterableUserDict):
    """
        This class should return the descriptor definitions on demand.

        The basic tables should be readed from the start, when it's loaded,
         but the specific tables shouldn't be readed every time, but
         automatically when are requested.

        Maybe the auto initially loaded tables should be reduced to really
         few of them, or none.

        !!!ATENTION!!! Work on error parser messages. Should show when a 
           descriptor is not available, like (3,15,99).
    """
    def __init__(self,path='./descriptors'):
        """
        """
        self.path=path
        self.data={0:{},1:{},2:{},3:{}}
        return
    def __getitem__(self, key):
        if len(key)==2:
            F,X = key
            return self.data[F][X]
        F,X,Y = key
        #print 'here',F,X,Y
        if X not in self.data[F]:
            self._readdescriptor(F,X)
        return self.data[F][X][Y]
    def _readdescriptor(self,F,X):
        """
        """
        import string
        import os
        import re
        filename = os.path.join(self.path,"%s_%s.txt" % (F,string.zfill(X,2)))
        print "Loading the file: %s" % filename
        f=open(filename)
        for line in f:
            #print line
            #fields = line.split('\t')
            fields = (re.sub('\n','',line)).split('\t')
            #fields=[line[1:7],line[8:72].strip(),line[73:98].strip(),int(line[98:101]),int(line[102:114]),int(line[115:118])]
            F=int(fields[0][0:1])
            X=int(fields[0][2:4])
            Y=int(fields[0][5:8])
            #print F,X,Y
            if X not in self.data[F]:
                self.data[F][X]={}
            if F == 0:
                #if Y not in descriptors[F][X]:
                #    descriptors[F][X]={}
                #self.data[F][X][Y] = {'mnemonic':fields[4],'unit':fields[5],'scale':fields[1],'reference':fields[2],'bitwidth':fields[3]}
                try:
                    #self.data[F][X][Y] = {'descriptor':fields[0],'scale':int(fields[1]),'reference':fields[2],'bitwidth':int(fields[3]),'mnemonic':fields[4],'unit':fields[5],'description':fields[6]}
                    self.data[F][X][Y] = {'descriptor':fields[0],'scale':fields[1],'reference':int(fields[2]),'bitwidth':int(fields[3]),'mnemonic':fields[4],'unit':fields[5],'description':fields[6]}
                except:
                    print "Not able to load: ",fields
            elif F == 3:
                # Temporary ugly solution
                if re.search("[ABCD]",fields[2]):
                    self.data[F][X][Y] = {'description':fields[1],'fields':[[d[0],int(d[2:4]),int(d[5:8])] for d in fields[2].split(' ')],'mnemonic':fields[3]}
                else:
                    self.data[F][X][Y] = {'description':fields[1],'fields':[[int(d[0]),int(d[2:4]),int(d[5:8])] for d in fields[2].split(' ')],'mnemonic':fields[3]}
        return

##############################################################################
#### SECTION 3
##############################################################################
from UserDict import UserDict
from UserDict import IterableUserDict
from UserList import UserList


descriptorstable = DescriptorsTable()

#filename = './data/wmo_sarep.bufr'
#f=open(filename,'r')
#lixo=f.read(30)

# Looks like a good first approach, but still needs:
#    - Think about an array index. I believe is the best way to reference were to store the output data
#    - Think about a rewind system for the walk. Maybe simply save a copy, of the data when the walk is called, and when the rewind is called, it only overload the copied data.
#    - Still missing how to deal with the repetitions (class 1).

#import itertools

class Descriptor0(UserDict):
    def __init__(self,F,X,Y):
        self.F, self.X, self.Y = F,X,Y
        self.data=globals()['descriptorstable'][F,X,Y]
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

class Descriptors(UserList):
    #def __init__(self,F=None,X=None,Y=None,pos=[0]):
    #def __init__(self,F=None,X=None,Y=None):
    def __init__(self,F=None,X=None,Y=None,level=[]):
        UserList.__init__(self)
        self.i=0
        self.repetitions=1
        self.n=0
        if (F != None) & (X != None) & (Y != None):
            self.append(F,X,Y)
        self.dataind=-1
        import copy
        self.level = copy.copy(level)
        self.level.append(-1)
        print "Level: ",self.level
        return
    def load(self,descriptorslist):
        """
        """
        i=0
        while i<len(descriptorslist):
            F,X,Y = descriptorslist[i]
            print "Processing: %s, %s, %s" % (F,X,Y)
            self.level[-1]+=1
            if (F==0):
                print F,X,Y
                self.data.append(Descriptor0(F,X,Y))
                self.dataind+=1
                self.data[-1]['index']=self.dataind
                import copy
                self.data[-1].level=copy.copy(self.level)
                print "Level: ",self.data[-1].level
            elif (F==1):
                tmp=Descriptors(level=self.level)
                tmp.dataind=self.dataind
                tmp.F,tmp.X,tmp.Y = F,X,Y
                if tmp.Y>0:
                    sublist=descriptorslist[i+1:i+1+X]
                    tmp.repetitions=Y
                    i+=X
                elif tmp.Y==0:
                    sublist=descriptorslist[i+2:i+2+X]
                    tmp.repfactor=Descriptor0(descriptorslist[i+1][0],descriptorslist[i+1][1],descriptorslist[i+1][2])
                    tmp.repfactor.level=copy.copy(self.level)
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
                #tmp=Descriptors()
                #import copy
                #level=copy.copy(self.level)
                #level.append(-1)
                #tmp=Descriptors(level=level)
                tmp=Descriptors(level=self.level)
                #tmp.level+=1
                tmp.dataind=self.dataind
                tmp.F,tmp.X,tmp.Y = F,X,Y
                tmp.load(globals()['descriptorstable'][F,X,Y]['fields'])
                self.dataind=tmp.dataind
                self.data.append(tmp)
            i+=1
        return
    def walk(self):
        output=self.data[self.i].walk()
        if (output == None):
            if self.i<(len(self.data)-1):
                self.i+=1
                if (self.data[self.i].F == 1) & (self.data[self.i].Y == 0) & ((self.data[self.i].n == 0)):
                    output = self.data[self.i].repfactor
                else:
                    output=self.data[self.i].walk()
            else:
                self.n+=1
                if (self.n<self.repetitions):
                    self.reset()
                    output=self.data[self.i].walk()
                else:
                    output=None
        return output
    def reset(self):
        """ Reset the counter
        """
        for i in range(len(self.data)):
            self.data[i].reset()
        self.i=0
        return

#a=Descriptors()
#a.load(descriptorslist)

#    def append(self,F,X,Y):
#   #self.i=0
#   if (F==0):
#       #self.data.append(WalkingList(globals()['descriptorstable'][F][X][Y]))
#       #self.data.append(Descriptor0(globals()['descriptorstable'][F][X][Y]))
#       #self.data.append(Descriptor0(F,X,Y))
#       tmp=(Descriptor0(F,X,Y))
#       #self.data.append((globals()['descriptorstable'][F][X][Y]))
#        elif (F==1):
#       # Replicator class
#       # X is the number of the following fields that should be replicated
#       # Y if > 0 is the number of repetitions
#       #   if = 0 means a delayed replicaton, and a class 0 31 should be the following field.
#       print "Hey!!! F=1!!!"
#       #self.nfields=X
#       tmp=Descriptors()
#       tmp.F=F
#       tmp.X=X
#       tmp.Y=Y
#       self.insiderepetition=True
#       #if Y==0:
#       #    # Need to read n on the next field
#       #    pass
#       #else:
#       #    self.n=Y
#   elif (F==3):
#       tmp=Descriptors()
#       tmp.F=F
#       tmp.X=X
#       tmp.Y=Y
#       for f,x,y in globals()['descriptorstable'][F][X][Y]:
#           print f,x,y
#           #tmp.append(Descriptors(f,x,y))
#           tmp.append(f,x,y)
#       #self.data.append(tmp)
#   if self.insiderepetition==True
#       #self.tmp.append(tmp)
#       #if len(self.tmp)==self.tmp.X:
#       #    self.insiderepetition==False
#       #   self.data.append(self.tmp)
#       self.data[-1].append(tmp)
#   else:
#            self.data.append(tmp)
#   return
#    def parser(self,descriptorlist):
#        for i,[F,X,Y] in enumerate(descriptorlist):
#       print "i: %i" % i
#       if F==0:
#           #self.data.append(Descriptor0(globals()['descriptorstable'][F][X][Y]))
#       self.append(F,X,Y)
#            elif F==1:
#           if Y>0:
#           start=i+1
#           end=i+1+X
#                elif Y==0:
#           start=i+2
#           end=i+2+X
#                tmp=Descriptors()
#                tmp.parser(descriptorlist[start:end])
#                print "tmp",tmp
#       elif F==3:
#           ##tmp=[]
#           #tmp=Descriptors()
#           #for f,x,y in globals()['descriptorstable'][F][X][Y]:
#           #    #tmp.append(Descriptors(f,x,y))
#           #    tmp.append(f,x,y)
#       #self.data.append(tmp)
#       self.append(F,X,Y)
#        return
#    def walk(self):
#        output=self.data[self.i].walk()
#   #print "output:",output
#   #print "i:",i
#   if (output == None):
#       self.i+=1
#       if (self.i<len(self.data)):
#                output=self.data[self.i].walk()
#            else:
#           output=None
#   return output

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



class section3(IterableUserDict):
    """A class to read the section 3 of a BUFR file
    """
    def __init__(self,f):
        """
        """
        self.f = f
        self.data={}
        self.read()
        return
    def read(self):
        self.data={}
        self.data['sec3size'] = safe_unpack('>i',self.f.read(3))
        self.data['reserved'] = safe_unpack('>i', self.f.read(1))
        self.data['nsubsets'] = safe_unpack('>i', self.f.read(2))
        self.data['xxxx'] = safe_unpack('>i', self.f.read(1))

        n_descriptors = (self.data['sec3size']-7)/2
        self.data['descriptors']=Descriptors()
        tmp=[]
        for i in range(n_descriptors):
            FX = safe_unpack('>i', self.f.read(1))
            F = FX/64
            X = FX%64
            Y = safe_unpack('>i', self.f.read(1))
            #sectiondata[3]['descriptors'].append([FX,F,X,Y])
            #sectiondata[3]['descriptors'].append(F,X,Y)
            tmp.append([F,X,Y])
            #print F,X,Y
            #if F == 0:
            #    print descriptorstable[F][X][Y]

        #Read the rest of the section non used bytes. Should be 0 or 1 bytes.
        trash=self.f.read((self.data['sec3size']-7)%2)
        print tmp
        self.data['descriptors'].load(tmp)
        return
##############################################################################
#### Unreviewed
##############################################################################

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
#
def Denary2Binary(n):
    '''convert denary integer n to binary string bStr'''
    bStr = ''
    if n < 0: raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    return bStr



def _unpack_int(bytes):
    """Unpack an integer bytes sequence.

       From the bytes length the type of integer is deduced,
        and extra bytes are appended to fit the required size.
    """
    n=len(bytes)
    if n<=4:
        output = struct.unpack('>i','\x00'*(4-n)+bytes)
    elif (n>4) & (n<=8):
        output = struct.unpack('>q','\x00'*(8-n)+bytes)
    return output[0]



# Looks like a good first approach, but still needs:
#    - Think about an array index. I believe is the best way to reference were to store the output data
#    - Think about a rewind system for the walk. Maybe simply save a copy, of the data when the walk is called, and when the rewind is called, it only overload the copied data.
#    - Still missing how to deal with the repetitions (class 1).

from UserList import UserList
from UserDict import UserDict
#import itertools


#class level0(UserList):
#    def __init__(self):
#        UserList.__init__(self)
#	return

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
        while (nbits>len(self.bitline)):
            #self.bitline+=int2bin(safe_unpack('>i', self.f.read(1)))
            #print dir(self.f)
            self.n+=1
            if (self.n>=self.size):
                print "Trying to read more then was supposed"
                return
            x=self.f.read(1)
            #print "x: %s" % x
            self.bitline+=int2bin(safe_unpack('>i', x))
        output=self.bitline[:nbits]
        self.bitline=self.bitline[nbits:]
        return output


# Need to change it. Should read variable by variable.
#rownbits=8
#for i in range(sectiondata[4]['size']-4):
#    bitline+=f.read(1)
#    bitline+=int2bin(safe_unpack('>i', f.read(1)))

def datatype(unit):
    """
    """
    datatypes={'NUMERIC':'int',
     'YEAR':'int',
     'MONTH':'int',
     'DAY':'int',
     'HOUR':'int',
     'MINUTE':'int',
     'SECOND':'int',
     'DEGREE':'int',
     'CCITTIA5':'str',
     'CCITT IA5':'str',
     'M/S':'int',
     'Numeric':'int',
     'Degree (North +, South -)':'int',
     'Degree (East +, West -)':'int',
     }
    if unit in datatypes.keys():
        return datatypes[unit]
    else:
        return unit


