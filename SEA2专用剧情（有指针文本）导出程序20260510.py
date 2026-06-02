
from asyncio.windows_events import NULL

import sys
import easygui as gui

#定义变量,个人习惯而已
tbl_file_name=".\SEA2-J.TBL.txt"
#rom_file_name=".\SEA2-C-法雷奥解压缩.sfc"

dictTBL={}     #TBL码表
lstOffset=[]  #每段文本的偏移量,同一个大段中,下一个列表数值就是前一个文本的字节数
section_offset=0       #对话大段的编号

#定义保存文本指针的地址范围;
diag=((0x0E948F,0x0E9DD3,0x1F,0X2,".\SEA2-C-1法雷奥解压缩专用.sfc")\
     ,(0x0E9DD3,0x0EA543,0x48,0X2,".\SEA2-C-2卡特琳娜解压缩专用.sfc")\
     ,(0x0EA543,0x0EA989,0xb,0X2,".\SEA2-C-3奥托解压缩专用.sfc")\
     ,(0x0EA989,0x0EAB7D,0x18,0X2,".\SEA2-C-4恩斯特解压缩专用.sfc")\
     ,(0X0EAB7D,0x0EAE1F,0x25,0X2,".\SEA2-C-5皮耶德解压缩专用.sfc")\
     ,(0x0EAE1F,0x0EB5A3,0x36,0X2,".\SEA2-C-6阿兰解压缩专用.sfc")\
    )
#第0项是：第一个文本指针的开始地址
#第1项是：最后一个文本指针的结束地址(包含最后一个文本指针)
#第2项是：最后一段文本字节数
#第3项是：每个文本指针的字节数
#第4项是：对应的文件名

ifadres=False

choice=gui.choicebox(msg='请选择需要导出的内容', title='SFC大航海时代2导出文本(hlken-20240523)', choices=\
    ("法雷尔"\
    ,"卡特琳娜"\
    ,"奥托"\
    ,"恩斯特"\
    ,"皮耶德"\
    ,"阿兰"\
    )) 
if choice=='法雷尔0E948F':
    txt_file_name=r".\法雷尔.txt"
    ifadres=True
    choice=0
elif choice=='卡特琳娜':
    txt_file_name=r".\卡特琳娜.txt"
    choice=1
    ifadres=True
elif choice=='奥托':
    txt_file_name=r".\奥托.txt"
    choice=2
    ifadres=True
elif choice=='恩斯特':
    txt_file_name=r".\恩斯特.txt"
    choice=3
    ifadres=True
elif choice=='皮耶德':
    txt_file_name=r".\皮耶德.txt"
    choice=4
    ifadres=True
elif choice=='阿兰':
    txt_file_name=r".\阿兰.txt"
    choice=5
    ifadres=True
else:
    sys.exit(0)

diag_bytes=diag[choice][3]                  #文本地址字节数
diag_start_adres=diag[choice][0]            #保存文本偏移地址的位置
diag_no_start=0x0                           #对话文本开始编号
diag_no_max=(diag[choice][1]-diag[choice][0])//diag_bytes    #对话文本最大编号
diag_no_max_len=diag[choice][2]             #对话文本最大编号那句话的字节数，需要手工算出来，默认0
rom_file_name=diag[choice][4]


print('******************************************\n\
本程序是导出程序,用于导出SFC大航海时代2日版的文本\n\
导出')
print("TBL文件:"+tbl_file_name)
print("ROM文件:"+rom_file_name)
print("导出文件:"+txt_file_name)
print('******************************************')

with open(tbl_file_name,encoding="utf-16") as tbl_file:
    for line in tbl_file:
        if line.split(sep='≡')[1][1]=='\n':
            dictTBL[int(line.split(sep='≡')[0],16)]=line.split(sep='≡')[1][:1]
        else:
            dictTBL[int(line.split(sep='≡')[0],16)]=line.split(sep='≡')[1][:-1]

#创建并清空TXT
with open(txt_file_name, "w") as txt_file:
    pass

#从0x37e000开始读取每段对话的偏移量
with open(rom_file_name,mode='r+b') as rom_file:
    for diag_num in range(diag_no_start,diag_no_max):   #包括最后一句文本
        rom_file.seek(diag_start_adres+diag_num*diag_bytes)      #计算文本指针地址
        read_data=int.from_bytes(rom_file.read(diag_bytes),byteorder="little")   #取得文本指针（SFC地址格式）
        lstOffset.append(read_data)    #记录每段文本指针到列表

    for diag_num in range(diag_no_start,diag_no_max):
        if diag_bytes == 3 :                           #如果文本指针是3字节
            read_adres=lstOffset[diag_num]-0XC00000    #文本指针（SFC格式）转换成ROM格式
        else:
            read_adres=lstOffset[diag_num]+0x230000    #如果文本指针是2字节，默认加0X230000，以后可以再改

        rom_file.seek(read_adres)
        if diag_num != diag_no_max-1:
            read_line=rom_file.read(int(lstOffset[diag_num+1]-lstOffset[diag_num]))     #判断读多少字节
        else:
            read_line=rom_file.read(diag_no_max_len)        #最后一句话的字节
        bytes_flag=NULL    #双字节标志
        line=''
        line_len=0
        read_index=0
        jiaming=0x1b480000  #预设假名为平假名

        while read_index < len(read_line):
            read_bytes=read_line[read_index]          #先读出第一个字节
            if read_bytes in range(0x80,0XA0):        #当第一个字节是汉字（0X80-0X9F）
                byte_all=read_bytes*0x100 + read_line[read_index+1]
                read_index=read_index+2
            elif read_bytes in range(0xA6,0XDE):    #当第一个字节是假名（0XA6-0XDD)
                if read_line[read_index+1]==0xDE or read_line[read_index+1]==0xDF : #当第二字节是DE或DF
                    #若第二字节是0XDE或0XDF，则判断为双字节
                    byte_all=jiaming+read_bytes*0X100+read_line[read_index+1]
                    read_index=read_index+2
                else:
                    #若第二字节非0XDE或0XDF，则判断为单字节
                    byte_all=jiaming+read_bytes
                    read_index=read_index+1
            elif read_bytes == 0X1B :
                #此处处理0X1B，双字节
                if read_line[read_index+1]==0X4B:
                    jiaming=0x1b4b0000  #设置为片假名
                elif read_line[read_index+1]==0X48 :
                    jiaming=0x1b480000  #设置为平假名
                #else :     #如果需要处理其它可以在此插入
                read_index=read_index+2
                continue    #退出循环不用再查了
            elif read_bytes == 0x25 :
                if read_line[read_index+1] in (0X2d,0x2e,0x4c): #0X252d为3字节
                    byte_all=read_bytes*0x10000 + read_line[read_index+1]*0x100+read_line[read_index+2]
                    read_index=read_index+3
                elif read_line[read_index+1] ==0X30 : #0x2530,30=(字符0)，则25为1字节
                    byte_all==read_bytes
                    read_index=read_index+1
                elif read_line[read_index+1] in range(0x31,0x3a): #0x25XX,XX=(字符1-9)，则25为3字节
                    byte_all=read_bytes*0x10000 + read_line[read_index+1]*0x100+read_line[read_index+2]
                    read_index=read_index+3
                elif read_line[read_index+1] in range(0x61,0x7b): #0x25XX,XX=(字符a-z)，则25为1字节
                    byte_all=read_bytes
                    read_index=read_index+1
                else :      #其它情况，0x25默认是2字节
                    byte_all=read_bytes*0x100 + read_line[read_index+1]
                    read_index=read_index+2
            else:
                #剩余单字节字符
                byte_all=read_bytes
                read_index=read_index+1
            try:
                line=line+dictTBL[byte_all]
            except:
                if byte_all==0x0a:
                    line=line+'{'+hex(byte_all)+'}\n'
                else:
                    line=line+'{'+hex(byte_all)+'}'            
        with open(txt_file_name,mode='a',encoding="utf-16") as txt_file:
            if ifadres:
                txt_file.writelines('---日文开始---\n'+hex(diag_num)+','+hex(diag_start_adres+diag_num*diag_bytes)+','+hex(read_adres)+','+str(len(read_line))+'\n'+line+'\n---日文结束---\n')
                txt_file.writelines('---中文开始---\n'+hex(diag_num)+','+hex(diag_start_adres+diag_num*diag_bytes)+','+hex(read_adres)+','+str(len(read_line))+'\n'+line+'\n---中文结束---\n\n\n\n')
            else:
                txt_file.writelines(hex(diag_num)+','+hex(read_adres)+','+str(len(read_line))+','+line+'\n')
