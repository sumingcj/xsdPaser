import os
import logging
import config
from shutil import copyfile
logging.basicConfig(level=logging.INFO #设置日志输出格式
                    ,filename="demo.txt" #log日志输出的文件位置和文件名
                    ,filemode="w" #文件的写入格式，w为重新写入文件，默认是追加
                    ,format="%(asctime)s - %(name)s - %(levelname)-9s - %(filename)-8s : %(lineno)s line - %(message)s" #日志输出的格式
                    # -8表示占位符，让输出左对齐，输出长度都为8位
                    ,datefmt="%Y-%m-%d %H:%M:%S" #时间输出的格式
                    )
head = '    <xb:namespace uri="##local">'
tail = '    </xb:namespace>'
confighead = '<xb:config xmlns:xb="http://www.bea.com/2002/09/xbean/config">'
configtail = '</xb:config>'
element_form_default='qualified'
def readFile(path):
    logging.info(path)
    draft=""
    filepaths=""
    files=os.listdir(path)
    for af in files:
        if not os.path.isdir(af):
            split=af.split(".")
            name=split[0].lower()+split[1]
            if len(split[2])>3:
                name=name+split[2][-1:]
            middle='       <xb:package>org.cppm.'+name+'</xb:package>'
            draft=draft+"\n"+head+'\n'+middle+'\n'+tail
            target_namespace = 'http://www.' + name + '.cppm.org'
            filepath = path +'/'+ af
            donepath = done +split[0]+'/'
            filepaths=filepaths+' '+donepath+af
            oldStr=""
            with open(filepath, "r", encoding="utf-8") as f:
                for l in f:
                    if l.startswith("<xs:schema"):
                        index=l.index(">")
                        nl=l[0:index]+"\n"+'xmlns="'+target_namespace+'"'+' targetNamespace="'+target_namespace+'"'+' elementFormDefault="qualified"'+'>'
                        oldStr=oldStr+nl+"\n"
                    else:
                        oldStr=oldStr+l
            logging.info('文件名：'+af)
            logging.info('文件内容：'+oldStr)
            if not os.path.exists(donepath):
                os.mkdir(donepath)
            with open(donepath+'/'+af, "w", encoding="utf-8") as f:
                f.write(oldStr)
    draft=confighead+draft+'\n'+configtail
    with open(configPath+"cppm_"+split[0].lower()+".xsdconfig", "w", encoding="utf-8") as f:
        f.write(draft)
    return filepaths


# #原报文文件位置
# path='C:/Users/Administrator/Desktop/draft/auto/un/'
# #修改后文件位置
# done='C:/Users/Administrator/Desktop/draft/auto/done/'
# #xsdconfigs文件位置
# configPath='C:/Users/Administrator/Desktop/draft/auto/xsdconfigs/'
# #XMLtoJAR脚本 文件位置
# scriptPath='C:/Users/Administrator/Desktop/draft/auto/script/'
# scriptName='XMLtoJAR脚本.txt'
#原报文文件位置
path=config.path
#修改后文件位置
done=config.done
#xsdconfigs文件位置
configPath=config.configPath
#XMLtoJAR脚本 文件位置
scriptPath=config.scriptPath
scriptName=config.scriptName
xmlBean=config.xmlBean

def doDraft():
    # 初始化文件
    if not os.path.exists(path):
        os.mkdir(path)
    if not os.path.exists(done):
        os.mkdir(done)
    if not os.path.exists(configPath):
        os.mkdir(configPath)
    if not os.path.exists(scriptPath):
        os.mkdir(scriptPath)

    dfs=os.listdir(path)
    # drafts = ['CAS', 'CBS', 'CCM', 'CES', 'CHS', 'CIM', 'CPP', 'CPR', 'DFB', 'MEM', 'NCP', 'NCS',
    #           'PAM', 'PKM', 'SDN', 'shcpe']
    scripts = ""
    for df in dfs:
        filepaths = readFile(path + df)
        script = 'scomp -src build/src -out build/cppm_' + df.lower() + '2.0.jar  ' + filepaths + '   -compiler D:/Java/jdk1.6.0_45/bin/javac ' + configPath + 'cppm_' + df.lower() + '.xsdconfig;'
        scripts = scripts + script + '\n'
    logging.info(scripts)
    with open(scriptPath + scriptName, "w", encoding="utf-8") as f:
        f.write(scripts)
    with open(scriptPath + 'XMLtoJAR.bat', "w", encoding="utf-8") as f:
        src = 'echo on'+'\n'
        src += 'cd '+xmlBean+'\n'
        src += scripts+'\n'
        src+='pause'
        f.write(src)


def doSplit(path):
    set={}
    filenames = os.listdir(path)
    for filename in filenames:
        rin=filename[:-4]
        if set.get(rin[:-4]) :
            if int(set.get(rin[:-4])[-1])<int(rin[-3:]):
                set.update({rin[:-4]:rin[-3:]})
        else:set.setdefault(rin[:-4],rin[-3:])
    return set

downPath =config.downPath
upPath = config.upPath
save = config.save
def doUndone():
    down = doSplit(downPath)
    up = doSplit(upPath)
    if not os.path.exists(save):
        os.makedirs(save)
    sp = '.'
    pre = '.xsd'
    keys = list(up.keys())
    print(keys)
    for k, v in down.items():
        fi = k.split(sp)[0]
        if not os.path.exists(save + fi):
            os.mkdir(save + fi)
        fn = k + sp + v
        if up.get(k):
            ufn = k + sp + up.get(k)
            keys.remove(k)
            copyfile(downPath + fn + pre, save + fi + '/' + fn + '02' + pre)
            copyfile(upPath + ufn + pre, save + fi + '/' + ufn + '01' + pre)
        else:
            copyfile(downPath + fn + pre, save + fi + '/' + fn + pre)
    for k in keys:
        ufn = k + sp + up.get(k)
        fi = k.split(sp)[0]
        if not os.path.exists(save + fi):
            os.mkdir(save + fi)
        copyfile(upPath + ufn + pre, save + fi + '/' + ufn + pre)


if __name__ == '__main__':
    doUndone()
    doDraft()