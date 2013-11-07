#encoding=utf8
#py3.2

import struct
import sys
import os

#用法，三种功能，对应三行“XXX=True”的行。
#想使用哪种功能就让另外两行=False

SingleFile=True
BmpFile=r'F:\Download\trial_title.bmp' #请在引号内输入bmp文件名，带全路径

MultiFile=False
MultiName=r'C:\00config' #这里对应的是C:\00config+000.bmp C:\00config+001.bmp ...等文件
    #它们将会被转换为C:\00config.mgr

DirCvt=True
OriDir=r'D:\chinesize\Stuff\Pics\old' #这里填入待转换的Bmp目录
NewDir=r'D:\chinesize\Stuff\Pics\new' #这里填入保存转换后的Mgr用的目录

def LzssPack(stm):
    news=bytearray(int(len(stm)/32*35))
    isrc=0
    idest=0
    while isrc<len(stm):
        if len(stm)-isrc>32:
            news[idest]=0x1f
            idest+=1
            news[idest:idest+32]=stm[isrc:isrc+32]
            isrc+=32
            idest+=32
        elif len(stm)-isrc>0:
            cnt=len(stm)-isrc
            news[idest]=cnt-1
            idest+=1
            news[idest:idest+cnt]=stm[isrc:isrc+cnt]
            idest+=cnt
            isrc+=cnt
    return news[0:idest]

def PackBmp(stm):
    lenO=len(stm)
    newstm=LzssPack(stm)
    lenN=len(newstm)
    hdr=struct.pack('II',lenO,lenN)
    return hdr+newstm

def PackToMgr(bmps):
    if len(bmps)==1:
        hdr=b'\x01\x00'
        return hdr+bmps[0]
    hdr0=struct.pack('H',len(bmps))
    hdr1=bytearray()
    buff=bytearray()
    curoff=2+len(bmps)*4
    for bmp in bmps:
        hdr1+=struct.pack('I',curoff)
        curoff+=len(bmp)
        buff+=bmp
    return hdr0+hdr1+buff

def printhelp():
    print(r'''将bmp转换为mgr

用法: Bmp2Mgr </p | /ps | /d> [/o]

    /p      指定要压缩单个bmp文件。
    /ps     指定要压缩一组bmp文件，每个文件名以'+XXX'为后缀。
            本选项只能指定+XXX之前的部分。
    /d      指定要压缩的目录。

    /o      指定输出文件名或路径，若不指定则通常为当前路径。

    示例：
    Bmp2Mgr /p=title.bmp /o="C:\title1.mgr"
    将当前目录下的title.bmp压缩，并保存为C:\title1.mgr
    
    Bmp2Mgr /ps=00config
    将当前目录下的00config+000.bmp 00config+001.bmp ...
    等文件压缩，并保存为00config.mgr
    
    Bmp2Mgr /d="C:\Program Files\game\system"
    将该目录中每个文件压缩，分别输出mgr文件。''')

def ParseOptions(argv):
    paras={}
    for para in argv:
        if para.startswith('/p='):
            paras['pic']=para[3:]
        elif para.startswith('/ps='):
            paras['pics']=para[4:]
        elif para.startswith('/o='):
            paras['output']=para[3:]
        elif para.startswith('/d='):
            paras['picdir']=para[3:]
        elif para=='/help' or para=='/?':
            paras['help']=True
    return paras

##if len(sys.argv)<2:
##    printhelp()
##    sys.exit()
##paras=ParseOptions(sys.argv[1:])
##if 'help' in paras:
##    printhelp()
##    sys.exit()

if SingleFile==True:
    fname=BmpFile
    if not fname.endswith('.bmp'):
        print('必须是bmp后缀的文件！')
        sys.exit()
    fs=open(fname,'rb')
    stm=fs.read()
    newstm=PackToMgr([PackBmp(stm)])

    fs=open(BmpFile.replace('.bmp','.mgr'),'wb')
    fs.write(newstm)
    fs.close()
    print('Success')
elif MultiFile==True:
    name=MultiName
    if name.find('.bmp')!=-1:
        print('ps参数使用方法错误！')
        sys.exit()
    bmps=[]
    i=0
    while True:
        fname=name+'+%03d.bmp'%i
        i+=1
        if not os.path.exists(fname):
            break
        fs=open(fname,'rb')
        bmps.append(PackBmp(fs.read()))
        print(fname+' Processed')
        fs.close()
    if len(bmps)==0:
        print('对应文件不存在！')
        sys.exit()
    fs=open(MultiName+'.mgr','wb')
    fs.write(PackToMgr(bmps))
    fs.close()
    print('Success')
elif DirCvt==True:
    files=os.listdir(OriDir)
    newpath=NewDir
    compressed=[]
    for f in files:
        if not f.endswith('.bmp'): continue
        p=f.find('+')
        if p!=-1:
            mname=f[0:p]
            if mname in compressed:
                continue
            bmps=[]
            i=0
            while True:
                fname=mname+'+%03d.bmp'%i
                i+=1
                if not os.path.exists(os.path.join(OriDir,fname)):
                    break
                fs=open(os.path.join(OriDir,fname),'rb')
                bmps.append(PackBmp(fs.read()))
                fs.close()
            if len(bmps)==0:
                continue
            fs=open(os.path.join(newpath,mname+'.mgr'),'wb')
            fs.write(PackToMgr(bmps))
            fs.close()
            compressed.append(mname)
            print(mname+' '+str(len(bmps))+' files Processed')
        else:
            fs=open(os.path.join(OriDir,f),'rb')
            bmps=[PackBmp(fs.read())]
            newstm=PackToMgr(bmps)
            fs=open(os.path.join(newpath,f.replace('.bmp','.mgr')),'wb')
            fs.write(newstm)
            fs.close()
            print(f+' Processed')
    print('All Success')
else:
    print('使用方法错误')
    
