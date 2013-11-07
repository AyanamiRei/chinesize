#py32

import sys
import os
import zlib
import struct

import bytefile

fname='game.pak'
fpath='game'
newname='game1.pak'

entries=[]
pos=0
def TraverseDir(cur_root, count):
    global pos,entries
    for i in range(count):
        if entries[pos][4] & 0x20:
            entries[pos][0]=cur_root+'\\'+entries[pos][0]
            pos+=1
        elif entries[pos][4] & 0x10:
            pos+=1
            TraverseDir(cur_root+'\\'+entries[pos-1][0],entries[pos-1][3])
        else:
            print("Unknown Type.")
            sys.exit()
                        
def MakeEntries(idx,ents):
    while idx.tell()<len(idx):
        off, unclen, complen, flags=struct.unpack('QQQI24x',idx.read(52))
        name=idx.readstr().decode('932')
        entries.append([name,off,complen,unclen,flags])


fs=open(fname,'rb')
magic, hdr1len, hdr2len, dircount, idxuncomprlen, idxcomprlen=struct.unpack(\
    "<4sH10xI4xIII4x",fs.read(0x28))
if (magic!=b'PAK\0') or (hdr1len!=0x10) or (hdr2len!=0x18):
    print("Format Error!")
    sys.exit()

idx=fs.read(idxuncomprlen)

idx=zlib.decompress(idx, -15)

MakeEntries(bytefile.ByteIO(idx),entries)
TraverseDir('.',dircount)

