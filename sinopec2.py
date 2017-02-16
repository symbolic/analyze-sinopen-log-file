#!D:\Python\Python27\python.exe
#-*- coding: utf-8 -*-
from __future__ import division
from xlwt.Workbook import *
from xlwt.Style import *
import os
import math
import sys
import re
import string
import shutil

port_string = []
nozzle_list = []

class oneline_item():	#数据结构
	"""read one line """
	def __init__(self):
		self.date = ''	#日期
		self.time = ''	#时间
		self.type = ''	#发送 接收
		self.port = ''	#端口号
		self.len = ''	#长度
		self.data = ''	#数据

def power(base, n):				#16进制转10进制：base = 256,
	if n == 1:
		return 1
	return base*power(base, n-1)

def hex_decimal(hex, n = 0):		#16进制转换成10进制，n为小数点个数, 返回值str
	temp = hex.split(' ')
	b = 0
	for i in range(len(temp)):
		b += string.atoi(temp[i], 16) * power(256, len(temp)-i)

	if n:
		return str(b/power(10, n+1))
	else:
		return str(b)

def bcd_decimal(hex, n = 0):		#BCD转换成10进制，n为小数点个数, 返回数值
	temp = hex.split(' ')
	b = 0
	for i in range(len(temp)):
		b += int(temp[i]) * power(100, len(temp)-i)
		
	if n:
		return b/power(10, n+1)
	else:
		return b

def time_second(time):			#时间转换成秒， 返回值int
	second = 0
	time_list = time.split(':')
	for i in range(len(time_list)):
		second += int(time_list[i])*power(60, len(time_list)-i)

	return second

def time_span(time1, time2):	#计算时间间隔，返回值int

	return math.fabs(time_second(time2) - time_second(time1))	

def trade_type(type):			#交易类型字符串
	a = bin(int(type, 16))
	type_length = len(a) - 2
	base = extend = ''

	if type[1] == '0' :
		base = '正常加油'
	if type[1] == '1' :
		base = '逃卡'
	if type[1] == '2' :
		base = '错卡'
	if type[1] == '3' :
		base = '补扣'
	if type[1] == '4' :
		base = '补充'
	if type[1] == '5' :
		base = '员工上班'
	if type[1] == '6' :
		base = '员工下班'
	if type[1] == '7' :
		base = '非卡'
	if type[1] == '8' :
		base = '油价接收'
	if type[1] == '9' :
		base = '卡片交易出错'	

	if type_length == 5:
		extend = '扣款签名有效'

	if type_length == 7:
		if a[4] == '1' :
			extend = '使用油机黑（白）名单，扣款签名有效'
		else:
			extend = '使用后台黑（白）名单，扣款签名有效'

	if type_length == 8:
		if (a[3] == '0') & (a[5] == '0'):
			extend = '卡错，使用后台黑（白）名单'
		if (a[3] == '0') & (a[5] == '1'):
			extend = '卡错，使用后台黑（白）名单，扣款签名有效'
		if (a[3] == '1') & (a[5] == '0'):
			extend = '卡错，使用油机黑（白）名单'
		if (a[3] == '1') & (a[5] == '1'):
			extend = '卡错，使用油机黑（白）名单，扣款签名有效'
	if type_length > 4:
		return extend + '，' + base
	else:
		return base

def check_format(oneline):				#格式检查
	pattern1 = re.compile(r'[^\w\s,.:;()]')
	a = len(oneline.split(','))
	if pattern1.search(oneline):			#包含有非法字符
		#print 'regex error:' + oneline
		return 1

	if a != 6:			#段数不够
		#print 'segment != 6:' + oneline
		return 1
	
	if (len(oneline) < 40) :			#长度太短，跳过
		#print 'length < 40:' + oneline
		return 1

	return 0

def port_list():		#获取端口列表
	fp_src = open(sys.argv[1], 'r')
	if fp_src:
		print 'open source file success'
	else:
		print 'open source file fail'

	oneline = fp_src.readline()

	while oneline:		
		if check_format(oneline):
			oneline = fp_src.readline()
			if oneline:
				continue
			else:
				break

		a = oneline_item()
		string = oneline.split(',')
		a.port = string[3]
		#print string[0:2]
		#print a.port
		now_port = a.port.split(':')[1]

		if now_port in port_string:		#端口已记录
			oneline = fp_src.readline()
			if oneline:
				continue
			else:
				break
		else:
			port_string.append(now_port)		#添加到端口列表
			oneline = fp_src.readline()
			if oneline:
				continue
			else:
				break

	port_string.sort()						#端口号列表排序
	fp_src.close()
	print 'the port list will be sorted'
	print port_string

def sort_port():		#按照端口号分类 argv.log ——> a.log
	fp_prt = []
	IsFirstLine = {}
	fp_src = open(sys.argv[1], 'r')
	if os.path.isdir(sys.argv[1].split('.')[0]):
		newpath = os.mkdir(sys.argv[1].split('.')[0] + '(2)')
		os.chdir(sys.argv[1].split('.')[0] + '(2)')
	else:
		newpath = os.mkdir(sys.argv[1].split('.')[0])
		os.chdir(sys.argv[1].split('.')[0])
		
	for a in range(len(port_string)):
		filename = open('port_' + port_string[a]+'.log', 'w')
		fp_prt.append(filename)		#文件描述符保存到列表中
		IsFirstLine[port_string[a]] = '0'	#每个端口都判断起始行是否有效
		
	pattern2 = re.compile(r'data: FA')
	oneline = fp_src.readline()

	while oneline:
		if check_format(oneline):
			oneline = fp_src.readline()
			if oneline:
				continue
			else:
				break

		if len(oneline) >= 40:		#数据有效
			for a in range(len(port_string)):
				if port_string[a] == oneline.split(',')[3].split(':')[1] :
					if IsFirstLine[port_string[a]] == '0':
						match2 = pattern2.search(oneline)
						if match2:					#是否data: FA开头
								IsFirstLine[port_string[a]] = '1'	#过了第一有效行，置1
								#print IsFirstLine
						else:
							oneline = fp_src.readline()	#无效数据，跳过
							continue

					if IsFirstLine[port_string[a]] == '1':
						fp_prt[a].write(oneline)	#写入相应的文件
						
				else:
					continue

		oneline = fp_src.readline()

	for a in range(len(port_string)):	#文件结尾写 换行
		fp_prt[a].write('\n')
		fp_prt[a].close()
	fp_src.close()
	
def command_line(index):		#多行合并成一行 a.log——>aa.log
	pattern1 = re.compile(r'\d\d')
	starter = 'data: FA'				
	fp_prt0 = open('port_' + index + '.log', 'r')
	fp_dest = open('port_' + index + '_1' + '.log', 'w')

	oneline = fp_prt0.readline()
	send_str = oneline_item()				#发送字符串
	recv_str = oneline_item()				#接收字符串
	is_send_firstline = 0					#发送首行
	is_recv_firstline = 0					#接收首行
	while oneline:
		string = oneline.split(',')
		if 'Send:' in oneline:						#读取的是send字符串
			if is_send_firstline == 0:				#首行
				if starter in oneline:
					send_str.date = string[0]
					send_str.time = string[1]
					send_str.type = string[2]
					send_str.port = string[3]
					send_str.len = string[4]
					send_str.data = string[5][0:-1]
					send_length = int(send_str.len.split(':')[1])
				else:
					oneline = fp_prt0.readline()
					continue
			else:											#不是首行
				if time_span(send_str.time, string[1]) <=2 :	#时间一致
					send_length += int(string[4].split(':')[1])
					send_str.data += string[5].split(':')[1][0:-1]
				else:
					is_send_firstline = 0
					continue
			if send_length < 6:			#数据中不包含长度
				is_send_firstline = 1
				
			else:						#数据中包含长度
				length_string1 = send_str.data.split(':')[1][13:15]		#数据长度高位
				length_string2 = send_str.data.split(':')[1][16:18]		#数据长度低位
				match1 = pattern1.search(length_string1)
				match2 = pattern1.search(length_string2)
				if (match1 != None) & (match2 != None):					#数据长度都是BCD
					total_length = int(length_string1)*100 + int(length_string2) + 8
					if total_length < 260:									#长度是否超限
						if send_length >= total_length:						#命令行完整
							fp_dest.write(send_str.date+','+send_str.time+','+send_str.type+','+send_str.port+','+send_str.data + '\n')
							is_send_firstline = 0
						else:
							is_send_firstline = 1
					else:
						is_send_firstline = 0
						
				else:					#长度超限，读取下一行
					is_send_firstline = 0
										
		if 'Recv:' in oneline:						#读取的是recv字符串
			if is_recv_firstline == 0:				#首行
				if starter in oneline:
					recv_str.date = string[0]
					recv_str.time = string[1]
					recv_str.type = string[2]
					recv_str.port = string[3]
					recv_str.len = string[4]
					recv_str.data = string[5][0:-1]
					recv_length = int(recv_str.len.split(':')[1])
				else:
					oneline = fp_prt0.readline()
					continue 
			else:												#不是首行
				if time_span(recv_str.time, string[1]) <=2 :	#时间一致
					recv_length += int(string[4].split(':')[1])
					recv_str.data += string[5].split(':')[1][0:-1]
				else:
					is_recv_firstline = 0
					continue
			if recv_length < 6:			#数据中不包含长度
				is_recv_firstline = 1
				
			else:						#数据中包含长度
				length_string1 = recv_str.data.split(':')[1][13:15]		#数据长度高位
				length_string2 = recv_str.data.split(':')[1][16:18]		#数据长度低位
				match1 = pattern1.search(length_string1)
				match2 = pattern1.search(length_string2)
				if (match1 != None) & (match2 != None):					#数据长度都是BCD
					total_length = int(length_string1)*100 + int(length_string2) + 8
					if	total_length < 260:									#判断长度是否超限
						if recv_length >= total_length:						#命令行完整
							fp_dest.write(recv_str.date+','+recv_str.time+','+recv_str.type+','+recv_str.port+','+recv_str.data + '\n')
							is_recv_firstline = 0
						else:
							is_recv_firstline = 1
					else:					#长度超限，读取下一行
						is_recv_firstline = 0
						
				else:
					oneline = fp_prt0.readline()
					is_recv_firstline = 0
					
				
		oneline = fp_prt0.readline()

	fp_prt0.close()
	fp_dest.close()

def real_data(oneline):
	string = oneline.split(',')
	date = string[0] + ','
	time = string[1] + ','
	transfer = string[2] + ','
	port = string[3] + ','
	data1 = string[4].split(':')[0] + ':'
	data2 = string[4].split(':')[1]
	data_id = data2[25:27]

	if data2[19:24] == '31 02':
		operate1 = operate2 = ''
		if data_id == '01':		#A卡插入
			operate1 = date + time + transfer + port + data1 + data2[:13] + '00 21 31 01 01 ' + data2[28:82] + '01 02\n'
			data_id2 = data2[82:84]
			if data_id2 == '01':	#B卡插入
				operate2 = date + time + transfer + port + data1 + data2[:13] + '00 21 31 01 01 '+ data2[85:139] + '02 02\n'
			if data_id2 == '02':	#B加油中
				operate2 = date + time + transfer + port + data1 + data2[:13] + '00 13 31 01 02 '+ data2[85:115] + '02 02\n'
				
			return operate1 + operate2

		if data_id == '02':		#A卡加油
			operate1 = date + time + transfer + port + data1 + data2[:13] + '00 21 31 01 02 ' + data2[28:58] + '01 02\n'
			data_id2 = data2[58:60]
			if data_id2 == '01':	#B卡插入
				operate2 = date + time + transfer + port + data1 + data2[:13] + '00 21 31 01 01 '+ data2[61:115] + '02 02\n'
			if data_id2 == '02':	#B加油中
				operate2 = date + time + transfer + port + data1 + data2[:13] + '00 13 31 01 02 '+ data2[61:91] + '02 02\n'
				
			return operate1 + operate2

	return oneline

def check_line():
	pattern2 = re.compile(r'data: FA')
	regex = re.compile(r'FA FA')
	errorfile = open('error.log', 'w')
	
	for index in range(len(port_string)):
		sourcefile = open('port_' + port_string[index] + '_1' + '.log', 'r')
		filename = open('port_' + port_string[index]  + '.log', 'w')
		errorfile.write('*' * 20 + '\n')

		oneline = sourcefile.readline()
		if len(oneline) < 35:
			continue
		a = oneline_item()
		string1 = oneline.split(',')			#读取首行，保存日期和时间
		a.date = string1[0]
		a.time = string1[1]
		First_line = 1
		
		while oneline:
			match2 = pattern2.search(oneline)
			if match2:
				result, number = re.subn(regex, 'FA', oneline) 	#替换所有的FA FA
												#对2条实时信息数据的处理，1行变2行
				filename.write(real_data(result))
			oneline = sourcefile.readline()
			if First_line: #第一行
				if time_span(a.time, '00:00:00') > 6:	#时间相差超过6秒
					errorfile.write('port: ' + port_string[index] + '\t\t' + '00:00:00' + '————' + a.time + '\t无数据\n')	#写入故障日志
					First_line = 0
					
			if oneline:
				string2 = oneline.split(',')		#读取下一行，保存日期和时间
				
				b = oneline_item()
				b.date = string2[0]
				b.time = string2[1]
				if time_span(a.time, b.time) > 6:	#时间相差超过6秒
					errorfile.write('port: ' + port_string[index] + '\t\t' + a.time + '————' + b.time + '\t无数据\n')	#写入故障日志
				a = b
				
			else:
				if time_span(a.time, '23:59:59') > 6:	#时间相差超过6秒
					errorfile.write('port: ' + port_string[index] + '\t\t' + a.time + '————' + '23:59:59' + '\t无数据\n')	#写入故障日志
				break

		
		sourcefile.close()
		filename.close()
	
	errorfile.write('*' * 20)
	
	errorfile.close()

def case300(data):				#加油机对PC机普通查询
	if bcd_decimal(data[13:18], 0) != 1 :
		return 'data error\n'
	if len(data.split(' '))  < 10 :
		return 'length error\n'

	operate = ''
	data_list = data.split(' ')
	operate = '命令字: ' + data_list[7] + '（加油机对PC机普通查询）\n'
	return operate

def case31(data):				#加油机发送实时信息命令
	if bcd_decimal(data[13:18], 0) < 2 :
		return 'data error\n'
	operate = '\n'
	operate2 = operate1 = ''
	data_list = data.split(' ')
	count = data_list[8]
	data_id = data_list[9]
	nozzle = data_list[10]
	#nozzle = str(string.atoi(data_list[10], 16))
	if count == '00':			#信息数量 = 1
		operate ='命令字: ' + data_list[7] + '（加油机发送实时信息，无卡插入）\n'
		return operate
	if count == '01':			#信息数量 = 1
		if data_id == '01':		#卡插入
			operate ='命令字: ' + data_list[7] + '(卡插入);枪号：' + hex_decimal(nozzle, 0) + ';卡号：' + data[34:63] + ';卡状态：' + data[64:69] + ';卡余额：' + hex_decimal(data[70:81], 2) + '\n'
			return operate			
		if data_id == '02':		#抬枪或加油中
			operate ='命令字: ' + data_list[7] + '加油中;枪号：' + hex_decimal(nozzle, 0) + ';结算单位：' + data[31:33] + ';数额：' + hex_decimal(data[34:42], 2) + ';升数：' + hex_decimal(data[43:51],2) + ';价格：' + hex_decimal(data[52:57],2) + '\n'
			return operate

	if count == '02':			#信息数量 = 2
		if data_id == '01':		#A卡插入
			operate1 ='命令字: ' + data_list[7] + '(卡插入);枪号：' + hex_decimal(nozzle, 0) + ';卡号：' + data[34:63] + ';卡状态：' + data[64:69] + ';卡余额：' + hex_decimal(data[70:81],2) + '\n'
			data_id2 = data[82:84]
			if data_id2 == '01':	#B卡插入
				operate2 = '(卡插入);枪号：' + hex_decimal(data[85:87], 0) + ';卡号：' + data[91:120] + ';卡状态：' + data[121:126] + ';卡余额：' + hex_decimal(data[127:138],2) + '\n'
			if data_id2 == '02':	#B加油中
				operate2 = '加油中;枪号：' + hex_decimal(data[85:87], 0) + ';结算单位：' + data[88:90] + ';数额：' + hex_decimal(data[91:99], 2) + ';升数：' + hex_decimal(data[100:108], 2)  + ';价格：' + hex_decimal(data[109:114],2) + '\n'
			
			return operate1 + operate2

		if data_id == '02':		#A加油中
			operate1 ='命令字: ' + data_list[7] + '加油中;枪号：' + hex_decimal(nozzle, 0) + ';结算单位：' + data[31:33] + ';数额：' + hex_decimal(data[34:42], 2) + ';升数：' + hex_decimal(data[43:51],2) + ';价格：' + hex_decimal(data[52:57],2) + '\n'
			data_id2 = data[58:60]
			if data_id2 == '01':	#B卡插入
				operate2 = '命令字: ' + data_list[7] + '(卡插入);枪号：' + hex_decimal(data[61:63], 0) + ';卡号：' + data[67:96] + ';卡状态：' + data[97:102] + ';卡余额：' + hex_decimal(data[103:114],2) + '\n'
			if data_id2 == '02':	#B加油中
				operate2 = '命令字: ' + data_list[7] + '加油中;枪号：' + hex_decimal(data[61:63], 0) + ';结算单位：' + data[64:66] + ';数额：' + hex_decimal(data[67:75],2) + ';升数：' + hex_decimal(data[76:84],2) + ';价格：' + hex_decimal(data[85:90],2) + '\n'
			
			return operate1 + operate2

	return operate

def case320(data):				#加油机发送成交数据
	if bcd_decimal(data[13:18], 0) < 96 :
		return 'data error\n'
	operate = ''
	operate = '枪号：' + hex_decimal(data[223:225], 0) + ',POS-TTC：' + hex_decimal(data[22:33], 0)  + ',交易时间：' + data[37:57] + ',交易类型：' + trade_type(data[34:36]) + ',卡号：' + data[58:87] + ',余额：' + hex_decimal(data[88:99],2) + ',金额：' + hex_decimal(data[100:108],2) + ',单价：' + hex_decimal(data[241:246],2) + ',升数：' + hex_decimal(data[232:240],2) + ',油品：' + data[226:231] + ',升累计：' + hex_decimal(data[250:261],2) + '\n'	
	return operate

def case330(data):				#加油机向PC机申请下载数据
	data_list = data.split(' ')
	if len(data_list) < 12:
		return 'length error\n'
	else:
		content = data_list[8]

		if content == '00':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载基础黑名单）\n'

		if content == '01':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载新增黑名单）' + ';基础黑名单版本号：' + hex_decimal(data[25:-7], 0) + '\n'

		if content == '02':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载新删黑名单）' + ';基础黑名单版本号：' + hex_decimal(data[25:-7], 0) + '\n'

		if content == '03':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载白名单）\n'

		if content == '04':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载油品油价表）\n'

		if content == '05':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载油站通用信息）\n'

		if content == '06':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载私有数据）\n'

		if content == '07':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载程序）\n'

def case340(data):				#P加油机申请下载数据
	data_list = data.split(' ')
	if bcd_decimal(data[13:18], 0) < 5:
		return 'data error\n'
	else:
		content = data_list[8]
		offset = hex_decimal(data[25:30], 0) 
		seg = hex_decimal(data[31:33], 0)

		if content == '00':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载基础黑名单）' + ';段偏移：' + offset + ';段数：' + seg + '\n'

		if content == '01':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载新增黑名单）' + ';段偏移：' + offset + ';段数：' + seg + '\n'

		if content == '02':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载新删黑名单）' + ';段偏移：' + offset + ';段数：' + seg + '\n'

		if content == '03':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载白名单）' + ';段偏移：' + offset + ';段数：' + seg + '\n'

		if content == '04':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载油品油价表）' + ';段偏移：' + offset + ';段数：' + seg + '\n'

		if content == '05':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载油站通用信息）' + ';段偏移：' + offset + ';段数：' + seg + '\n'

		if content == '06':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载私有数据）' + ';段偏移：' + offset + ';段数：' + seg + '\n'

		if content == '07':
			return '命令字: ' + data_list[7] + '（加油机向PC机申请下载程序）' + ';段偏移：' + offset + ';段数：' + seg + '\n'

def case350(data):				#加油机申请解灰
	if bcd_decimal(data[13:18], 0) < 25:
		return 'length error\n'
	else:
		operate = ''
		data_list = data.split(' ')
		card_no = data[22:51]
		balance = data[52:63]
		ctc_no = data[64:69]
		ds = data[70:72]
		time = data[73:93]

		operate = '命令字: ' + data_list[7] + '（加油机申请解灰）'+';卡号：' + card_no + ';余额：' + hex_decimal(balance, 2) + ';CTC：' + hex_decimal(ctc_no, 0) + ';扣款来源：' + ds + ';时间：' + time +'\n'
		return operate

def case360(data):				#加油机申请查询黑/白名单
	data_list = data.split(' ')
	card_no = data[22:51]

	return '命令字: ' + data_list[7] + '（加油机向PC机查询黑/白名单）'+';卡号：' + card_no +'\n'

def case380(data):				#加油机上送累计数
	length = len(data.split(' ')) - 1
		
	if	length < 15:
		return 'length error\n'
	else:
		data_list = data.split(' ')
		count = data_list[8]
		number = int(count)
		if length < 10 + 5*number:
			return 'length error\n'
		
		b = []
		seq = ';'
		base = '命令字: ' + data_list[7] + '（读取加油机累计数）' 
		b.append(base)
		for i in range(number):
			cnt = 25 + i*15
			extend = '枪号：' + hex_decimal(data[cnt:2+cnt], 0) + ';升累计：' + hex_decimal(data[3+cnt:14+cnt],2)
			b.append(extend)

		return seq.join(b) + '\n'

def case3A0(data):				#加油机上送加油机信息
	if bcd_decimal(data[13:18], 0) < 39 :
		return 'data error\n'
	data_list = data.split(' ')
	m_info = data[22:57]
	prov_code = data[58:60]
	city_code = data[61:63]
	sup_code = data[64:75]
	s_id = data[76:87]
	time = data[88:108]
	count = data[109:111]
	number = int(count)
	
	b = []
	seq = ','
	base_start = '命令字: ' + data_list[7] + '（加油机上送加油机信息）' + ';厂家信息：' + m_info + ';省代号：' + prov_code + ';地市代码：' + city_code + ';上级单位代号：' + sup_code + ';加油站ID：' + s_id + ';加油机时间：' + time + ';枪号：'
	b.append(base_start)
	for i in range(number):
		cnt = 112 + i*3
		extend = hex_decimal(data[cnt:2+cnt], 0)
		b.append(extend)
	base_end = ';基础黑名单版本号：' + hex_decimal(data[cnt+3:cnt+5], 0) + ';新增黑名单版本：' + hex_decimal(data[cnt+6:cnt+8], 0) + '\n'

	return base_start + seq.join(b) + base_end

def case3B(data):				#加油机内部出错
	data_list = data.split(' ')
	return '命令字: ' + data_list[7] + '（加油机内部出错）'+';数据：' + data[25:-7] + '\n' 

def case3C(data):				#通讯接受方对发送方的通讯确认
	data_list = data.split(' ')
	data_id = data_list[8]
	flag = data_list[9]
	result = '通讯错\n'
	if bin(int(flag, 16))[-1:] == '0' :
		result = '接受无误\n'
	
	return '命令字: ' + data_list[7] + '（通讯接受方对发送方的通讯确认）'+';通讯的命令字：' + data_id + ';成功标志：' + result

def case3F(data):
	length = len(data.split(' ')) - 1
		
	if	length < 8 + 5:
		return 'length error\n'

	return '命令字: ' +  data[19:21] + '（加油机上无相应的记录）' + ';POS-TTC：' +  hex_decimal(data[22:-7], 0) + '\n'

def case301(data):				#PC机对加油机普通查询
	if bcd_decimal(data[13:18], 0) != 17 :
		return 'data error\n'
	operate = ''
	data_list = data.split(' ')
	operate = '命令字: ' + data_list[7] + '（PC机对加油机普通查询）'+';时间：' + data[22:42] + ';基础黑名单版本号：' + hex_decimal(data[43:48], 0) + ';新增黑名单版本：' + hex_decimal(data[49:51], 0) + ';新删黑名单版本：' + hex_decimal(data[52:54], 0) + ';白名单版本号：' +  hex_decimal(data[55:57], 0) + ';油品油价版本：' + hex_decimal(data[58:60], 0) + ';油站通用信息版本：' + hex_decimal(data[61:63], 0) + ';加油机初始化数据更新标志：' + data[64:66] + ';加油机程序下载更新标记：' + data[67:69] + '\n'
	return operate

def case321(data):				#PC机回应成交数据
	if bcd_decimal(data[13:18], 0) != 2 :
		return 'data error\n'

	data_list = data.split(' ')
	result = data_list[8]
	if bin(int(result, 16))[-1:] == '0' :			#b0 = 0:正确; b0 = 1:T-MAC错
		return '命令字：' + data_list[7] + '(PC机回应成交数据),结果：正确\n'
	else:
		return '命令字：' + data_list[7] + '(PC机回应成交数据),结果：T-MAC错\n'

def case331(data):
	data_list = data.split(' ')
	data_len = hex_decimal(data[22:33], 0)
	content = data_list[12]

	if content == '00':
		return '命令字: ' + data_list[7] + '（PC机发送需要下载：基础黑名单）;长度：' + data_len + '\n'

	if content == '01':
		return '命令字: ' + data_list[7] + '（PC机发送需要下载：新增黑名单）;长度：' + data_len + '\n'

	if content == '02':
		return '命令字: ' + data_list[7] + '（PC机发送需要下载：新删黑名单）;长度：' + data_len + '\n'

	if content == '03':
		return '命令字: ' + data_list[7] + '（PC机发送需要下载：白名单）;长度：' + data_len + '\n'

	if content == '04':
		return '命令字: ' + data_list[7] + '（PC机发送需要下载：油品油价表）;长度：' + data_len + '\n'

	if content == '05':
		return '命令字: ' + data_list[7] + '（PC机发送需要下载：油站通用信息）;长度：' + data_len + '\n'

	if content == '06':
		return '命令字: ' + data_list[7] + '（PC机发送需要下载：私有数据）;长度：' + data_len + '\n'

	if content == '07':
		return '命令字: ' + data_list[7] + '（PC机发送需要下载：程序）;长度：' + data_len + '\n'			  #PC机发送需要下载

def case341(data):				#（PC机发送需要下载）
	content_string = ''
	data_list = data.split(' ')
	content = int(data_list[8])
	offset = hex_decimal(data[25:30], 0)
	seg = hex_decimal(data[31:33], 0)

	if content == 0:
		content_string = '（PC机发送需要下载：基础黑名单）'
	if content == 1:
		content_string = '（PC机发送需要下载：新增黑名单）'
	if content == 2:
		content_string = '（PC机发送需要下载：新删黑名单）'
	if content == 3:
		content_string = '（PC机发送需要下载：白名单）'
	if content == 4:
		content_string = '（PC机发送需要下载：油品油价表）'
	if content == 5:
		content_string = '（PC机发送需要下载：油站通用信息）'
	if content == 6:
		content_string = '（PC机发送需要下载：私有数据）'
	if content == 7:
		content_string = '（PC机发送需要下载：下载程序）'

	base = '命令字: ' + data_list[7] + content_string + ';段偏移：' + offset + ';段数：' + seg + ';'
	extend = ''
	b = []
	if content < 4 :			#下载黑白名单
		if seg == '1':
			if bcd_decimal(data[13:18], 0) == 21:
				extend = '版本号：' + hex_decimal(data[34:39], 0) + ';生效日期：' + data[40:51] + ';截止日期：' + data[52:63] +  ';(黑名单)有效区域：' + data[64:69] + ';名单数量：' + hex_decimal(data[70:81], 0) + '\n'
				return base + extend
			else:
				return 'length error\n'
		if  hex_decimal(seg, 0) > 1 :
			seq = ','
			a = int(seg)*16//10
			for i in range(a):
				cnt = 34 + i*30
				card_number = data[cnt:cnt+29]
				b.append(card_number) 

			return base + '卡号：' + seq.join(b) + '\n'
		if seg == '0':
			return 

	if content == 4:			#油品油价表
		price_str21 = [] 		#新油品油价总记录
		price_str22 = []		#每一条油品价格列表
		
		if bcd_decimal(data[13:18], 0) < 32:
			return 'length error\n'
		ver = '版本号：' +  hex_decimal(data[34:36], 0)
		data_time = ';生效时间：' + data[37:54]
		field_num = int(hex_decimal(data[55:57], 0))
		cnt = 58
		for i in range(field_num):					#当前油品油价记录
			price_str11 = [] 		#当前油品油价总记录
			
			nozzle = '\n枪号:' + hex_decimal(data[cnt:cnt+2], 0)
			oil_type = ',油品代码：' + data[cnt+3:cnt+8]
			den = ',密度：' + data[cnt+9:cnt+20]
			price_no = ';价格数目：' + hex_decimal(data[cnt+21:cnt+23], 0) 
			price_no_int = int(hex_decimal(data[cnt+21:cnt+23], 0))
			for j in range(price_no_int):
				cnt_base = cnt+24+j*3
				oil_price = hex_decimal(data[cnt_base:cnt_base+5], 2)
				price_str11.append(nozzle + oil_type + ',当前价格：' + oil_price)
				
			price_str21.append(' '.join(price_str11))
			cnt = cnt_base + 6
		extend1 = ' '.join(price_str21)
		
		for i in range(field_num):					#当前油品油价记录
			price_str12 = [] 		#当前油品油价总记录
					
			nozzle = '\n枪号:' + hex_decimal(data[cnt:cnt+2], 0)
			oil_type = ',油品代码：' + data[cnt+3:cnt+8]
			den = ',密度：' + data[cnt+9:cnt+20]
			price_no = ';价格数目：' + hex_decimal(data[cnt+21:cnt+23], 0) 
			price_no_int = int(hex_decimal(data[cnt+21:cnt+23], 0))
			for j in range(price_no_int):
				cnt_base = cnt+24+j*3
				oil_price = hex_decimal(data[cnt_base:cnt_base+5], 2)
				price_str12.append(nozzle + oil_type + ',新价格：' + oil_price)
				
			price_str22.append(' '.join(price_str12))
			cnt = cnt_base + 6
		extend2 = ' '.join(price_str22)

		return base + ver + data_time + extend1 + extend2 + '\n'

	if content == 5:			#油站通用信息
		ver = '版本号：' +  hex_decimal(data[34:36], 0)
		prov_code = ';省代码：' + data[37:39]
		city_code = ';地市代码：' + data[40:42]
		sup_code = ';上级单位代码：' + data[43:54]
		s_id = ';加油站ID：' + data[55:66]
		pos_p = ';通讯终端逻辑编号：' + hex_decimal(data[67:69], 0)
		number = ';枪数：' + hex_decimal(data[70:72], 0)
		number_int = int(hex_decimal(data[70:72], 0))
		comm_info = []
		for i in range(number_int):
			cnt = 73 + i*3
			extend = hex_decimal(data[cnt:2+cnt], 0)
			comm_info.append(extend)

		return base + ver + prov_code + city_code + sup_code + s_id + pos_p + number + ':' + ','.join(comm_info) + '\n'	

def case351(data):				#PC机回复灰卡查询结果
	data_list = data.split(' ')
	flag = data_list[8]
	card_no = data[25:54]
	balance = data[55:66]
	amount = data[67:75]
	ctc_no = data[76:81]
	ds = data[82:84]
	time = data[85:105]
	gmac = data[106:117]
	psam_tid = data[118:135]
	psam_ttc = data[136:147]

	if bin(int(flag, 16))[-1:] == '0' :
		return '命令字: ' + data_list[7] + '（PC机回复灰卡查询结果）;结果：匹配'+';卡号：' + card_no + ';余额：' + hex_decimal(balance, 2) +';交易额：' + hex_decimal(amount, 2) + ';CTC：' + hex_decimal(ctc_no, 0) + ';扣款来源：' + ds + ';时间：' + time + ';解灰认证码：' + gmac + ';PSAM应用编号：' + psam_tid + ';PSAM的TTC：' + hex_decimal(psam_ttc, 0) + '\n'
	
	else:
		return '命令字: ' + data_list[7] + '（PC机回复灰卡查询结果）;结果：不匹配\n'

def case361(data):				#PC机黑/白名单查询结果
	data_list = data.split(' ')
	flag = data_list[8]
	card_type = data_list[11]
	
	if bin(int(flag, 16))[-1:] == '0' :			#匹配
		if card_type == '01':	#用户卡不能加油
			return '命令字: ' + data_list[7] + '（PC机黑/白名单查询结果）;结果：匹配（用户卡不能加油）\n'
		if (card_type == '04')|(card_type == '05')|(card_type == '06'):	#内部卡可以能加油
			return '命令字: ' + data_list[7] + '（PC机黑/白名单查询结果）;结果：匹配（内部卡可以加油）\n'

	else:
		if card_type == '01':	#用户卡可以加油
			return '命令字: ' + data_list[7] + '（PC机黑/白名单查询结果）;结果：不匹配（用户卡可以加油）\n'
		if (card_type == '04')|(card_type == '05')|(card_type == '06'):	#内部卡可以能加油
			return '命令字: ' + data_list[7] + '（PC机黑/白名单查询结果）;结果：不匹配（内部卡不能加油）\n'

def case381(data):				#读取加油机累计数
	
	return '命令字: ' + data[19:21] + '（读取加油机累计数）\n'

def case3A1(data):				#PC机读取加油机信息
	
	return '命令字: ' +  data[19:21] + '（PC机读取加油机信息）\n'

def case3E(data):				#PC机主动读取加油记录
	
	return '命令字: ' +  data[19:21] + '（PC机主动读取加油记录）' + ';POS-TTC：' + data[22:-7] + '\n'

def cmd0(command, data):		#油机发送
	if command == '30':
		return case300(data)

	if command == '31':
		return case31(data)

	if command == '32':
		return case320(data)

	if command == '33':
		return case330(data)

	if command == '34':
		return case340(data)

	if command == '35':
		return case350(data)

	if command == '36':
		return case360(data)

	if command == '38':
		return case380(data)

	if command == '3A':
		return case3A0(data)

	if command == '3B':
		return case3B(data)

	if command == '3C':
		return case3C(data)

	if command == '3F':
		return case3F(data)

	else:
		return 'unknown\n'

def cmd1(command, data):		#油机接收
	if command == '30':
		return case301(data)

	if command == '32':
		return case321(data)

	if command == '33':
		return case331(data)

	if command == '34':
		return case341(data)

	if command == '35':
		return case351(data)

	if command == '36':
		return case361(data)

	if command == '38':
		return case381(data)

	if command == '3A':
		return case3A1(data)

	if command == '3C':
		return case3C(data)

	if command == '3E':
		return case3E(data)


	else:
		return 'unknown\n'
	
def analyze_cmd(type, data):	#type:	0-油机发送;	1—油机接收
	operate = ''
	data_list = data.split(' ')
	command = data_list[7]
	if type == 0:
		operate = cmd0(command, data)

	else:
		operate = cmd1(command, data)

	return operate

def analyze_line(oneline):
	end = ''
	snd_rcv = 1
	direction = ' 管控——>油机，'
	a = oneline_item()
	string = oneline.split(',')
	a.date = string[0]
	a.time = string[1]
	a.type = string[2]
	a.port = string[3]
	a.data = string[4].split(':')[1]

	if a.type == 'Recv:':
		snd_rcv = 0				#0-油机发送;	1—油机接收
		direction = ' 油机——>管控，'

	length_string1 = a.data[13:15]
	length_string2 = a.data[16:18]
	total_length = int(length_string1)*100 + int(length_string2) + 9
	
				
	if len(a.data.split(' ')) == total_length:
		result = analyze_cmd(snd_rcv, a.data)
		end = '时间：' + a.date + ' ' + a.time + direction + str(result)
	else:
		end = '时间：' + a.date + ' ' + a.time + direction + 'data length is error\n'
		
	return end

def analyze():
	for index in range(len(port_string)):
		print 'port: ' + port_string[index] + ' will be handled with'
		sourcefile = open('port_' + port_string[index] + '.log', 'r')	#源文件a.log
		filename = open('port_' + port_string[index] + '_1' + '.log', 'w')	#解析后的日志aa.log
		oneline = sourcefile.readline()
		while oneline:
			#print 'oneline = ', oneline
			filename.write(oneline)					#写入原始数据
			handled_with = analyze_line(oneline)	#解析数据
			#print 'handled_with = ', handled_with
			filename.write(handled_with)			#写入解析数据
			oneline = sourcefile.readline()

		#print 'port = ', port_string[index], 'analyze finished'
		#print 'will be analyze the next file'
		sourcefile.close()
		filename.close()

def analyze_transaction():						#分析交易数据
	trade_file1 = open('transaction1.log', 'w')	#存放原始交易数据
	trade_file2 = open('transaction2.log', 'w')	#存放原始数据及解析数据
	
	for index in range(len(port_string)):
		nozzle_list.append([])
		sourcefile = open('port_' + port_string[index] + '.log', 'r')
		
		oneline = sourcefile.readline()		
		while oneline:
			a = oneline_item()
			a.data = oneline.split(',')[4].split(':')[1]
			a.type = oneline.split(',')[2]
			data_list = a.data.split(' ')
			command = data_list[7]
			if command == '32':				#油机上送交易记录数据
				if a.type == 'Recv:':
					if bcd_decimal(a.data[13:18], 0) < 96 :
						break
					nozzle = int(hex_decimal(data_list[75], 0))
					#if nozzle != 255:
					if nozzle_list[index].count(nozzle):
						pass
					else:
						nozzle_list[index].append(nozzle)
						nozzle_list[index].sort()
							
			oneline = sourcefile.readline()
		
		sourcefile.close()
	print nozzle_list

	for index in range(len(port_string)):
		print 'Next will analyze port: ' + port_string[index] + '...'
			
		for nozzle in nozzle_list[index]:
			print 'analyze nozzle: ' + str(nozzle) + '...'
			trade_file1.write('*'*10 + ' nozzle: ' + str(nozzle) + '\n')
			trade_file2.write('*'*10 + ' nozzle: ' + str(nozzle) + '\n')
		
			sourcefile = open('port_' + port_string[index] + '.log', 'r')
			oneline = sourcefile.readline()		
			while oneline:
				a = oneline_item()
				a.data = oneline.split(',')[4].split(':')[1]
				a.type = oneline.split(',')[2]
				data_list = a.data.split(' ')
				command = data_list[7]
				if command == '32':				#油机上送交易记录数据
					if a.type == 'Recv:':
						if bcd_decimal(a.data[13:18], 0) < 96 :
							handled_with = analyze_line(oneline)	#解析数据
							trade_file2.write(handled_with)			#写入解析数据
							break
						nozzle_number = int(hex_decimal(data_list[75], 0))
						if nozzle == nozzle_number:
							trade_file1.write(oneline)
							trade_file2.write(oneline)
							handled_with = analyze_line(oneline)	#解析数据
							trade_file2.write(handled_with)			#写入解析数据
										
				oneline = sourcefile.readline()
				
		sourcefile.close()
	
	trade_file1.close()	
	trade_file2.close()
		
def ttc_excle():
	header = ['Port', 'Nozzle', 'POS-TTC', 'PSAM-TTC', 'PC-Time', 'Oil-Time', 'Card', 'T-Type', 'Balance', 'Liter', 'Unit', 'Amount', 'Total', 'G-Code']
	fp_src = open('transaction1.log', 'r')
	oneline = fp_src.readline()
	wb = Workbook()
			
	col = 0
	while oneline:
		if 'nozzle:' in oneline:						#枪号行
			col = 0
			ws0 = wb.add_sheet('nozzle ' + oneline[19:-1])			#增加sheet
			for row in xrange(len(header)):
				ws0.write(col, row,  header[row])
			col += 1

			oneline = fp_src.readline()
			if oneline:
				continue
			else:
				break

		else:				#交易行
			trade = []									#保存交易数据
			data = oneline.split(',')[4].split(':')[1]
			
			Port = oneline.split(',')[3].split(':')[1]
			Nozzle =  hex_decimal(data[223:225], 0)		#枪号
			TTC = hex_decimal(data[22:33], 0)
			PSAM_TTC = hex_decimal(data[199:210], 0)
			year = ''.join(data[37:42].split(' ')) + ' '
			date = '-'.join(data[43:48].split(' ')) + ' '
			time = ':'.join(data[49:57].split(' '))
			PC_Time = oneline.split(',')[0] + ' ' + oneline.split(',')[1]
			Oil_Time = year + date + time  					#时间格式 yyyy mm-dd HH:MM:SS
			Card =  ''.join(data[58:87].split(' '))		#删掉卡号的空格
			Type = data[34:36]
			Balance = hex_decimal(data[88:99],2)		#卡余额，2位小数
			Liter = hex_decimal(data[232:240],2) 		#升数，2位小数
			Unit =  hex_decimal(data[241:246],2)		#单价，2位小数
			Amount = hex_decimal(data[100:108],2) 		#金额，2位小数
			Total = hex_decimal(data[250:261],2) 		#总累计，2位小数
			OilName = data[226:231]

			trade.append(Port)
			trade.append(Nozzle)		#构造交易数据列表
			trade.append(TTC)
			trade.append(PSAM_TTC)
			trade.append(PC_Time)
			trade.append(Oil_Time)
			trade.append(Card)
			trade.append(Type)
			trade.append(Balance)
			trade.append(Liter)
			trade.append(Unit)
			trade.append(Amount)
			trade.append(Total)
			trade.append(OilName)
			
			for row in xrange(len(header)):			#表格写入数据
				ws0.write(col, row,  trade[row])
			
			oneline = fp_src.readline()
			if oneline:			#行号+1
				col += 1
				continue

			else:
				break

	print "Storing..."
	fp_src.close()
	wb.save('TTC' + sys.argv[1].split('.')[0] + '.xls')	

def report():
	os.mkdir('.\\report')
	
	shutil.copy('transaction1.log', './report')
	os.remove('transaction1.log')
	shutil.copy('transaction2.log', './report')
	os.remove('transaction2.log')
	
	shutil.copy('TTC' + sys.argv[1].split('.')[0] + '.xls', './report')
	os.remove('TTC' + sys.argv[1].split('.')[0] + '.xls')
	
	shutil.copy('error.log', './report')
	os.remove('error.log')

def readme():
	fp = open('readme.txt', 'w')
	fp.write('*' * 60 + '\n\nReadme: \n')
	fp.write('Version: 1.0.0.4-2\n')
	fp.write( 'port_a.log: 按端口号分类的文件（a为端口号）\n')
	fp.write( 'port_a_1.log: port_a.log解析后的文件（a为端口号）\n')
	fp.write( 'transaction1.log: 所有的交易数据\n')
	fp.write( 'transaction2.log: 解析后的交易数据\n')
	fp.write( 'TTC****.xls: .xls格式的交易数据\n')
	fp.write( '其他问题请联系E_mail: willardmoogle@hotmail.com \n')
	fp.write( '*' * 60)
	fp.close()
	
	shutil.copy('readme.txt', './report')
	os.remove('readme.txt')

def remove30(port):		#过滤文件，删除所有的30
	fp_src = open(port, 'r')
	if fp_src:
		#print 'open source file success'
		fp_dest = open(port.split('.')[0]+'_min.log', 'w')
	else:
		print 'open source file fail'

	oneline = fp_src.readline()

	while oneline:
		#print oneline
		
		a = oneline_item()
		string = oneline.split(',')
		a.port = string[3]
		a.data = string[4].split(':')[1]
		command = a.data.split(' ')[7]
		length_high = a.data.split(' ')[5]
		length_low = a.data.split(' ')[6]
		#print 'aaaa'+command+'aaaa\n'
		
		if command != '30':		#不是轮询数据
			if (length_high != '00') | (length_low != '02') | (command != '31'):
				fp_dest.write(oneline)
		oneline = fp_src.readline()
		if oneline:
			continue
		else:
			break
		
	fp_src.close()
	fp_dest.close()
	print 'Remove 30 data from ' + port + ' finished.\n'
		
	
def main():

	if len(sys.argv) != 2:
		command = sys.argv[0].split('\\')[len(sys.argv[0].split('\\')) - 1]
		print 'Usage: ' + command + ' file.log'
		sys.exit()
		
	version = 'Version: 1.0.0.5\n'
	print 'New feature: remove all "30 data" and "00 02 31 00 data"\n'
	print '****** Analyze sinopec log file ******\n' + version
	print 'getting the port list...'
	port_list()

	print 'Trans Log files to port_file...'
	sort_port()							#20120102.log -> port_0.log
	
	print 'Multiple lines merged into a single line...'
	for i in range(len(port_string)):
		print 'will be read next file...'
		command_line(port_string[i])	#port_0.log -> port_0_1.log

	print 'will be check the start of the line again'
	
	check_line()						#port_0_1.log -> port_0.log
	
	print 'Removing all "30" | "00 02 31 00" data line...\n'
	for index in range(len(port_string)):
		#print 'Removing all "30" | "00 02 31 00"\n'
		remove30('port_' + port_string[index] + '.log')#port_0.log -> port_0_min.log
		os.remove('port_' + port_string[index] + '.log')
		shutil.copy('port_' + port_string[index] + '_min.log', 'port_' + port_string[index] + '.log')
		os.remove('port_' + port_string[index] + '_min.log')
	print 'Removing all "30" | "00 02 31 00, finished."\n'
		

	analyze()							#源文件：port_0.log；解析后的文件：port_0_1.log

	print 'analyze_transaction ...'
	analyze_transaction()				#原始交易数据：transaction1.log；解析后的交易数据：transaction2.log

	print 'save trade to excel...'
	ttc_excle()							#生成交易报表 TTC_20120102.xls
	
	print 'waiting to move files to report folder...'
	report()							#拷贝报表文件到 report 目录

	print 'Analyze log file finished'

	readme()
	
	print '\n' +  '*' * 60 + '\n\nReadme: \n'
	print 'port_a.log: classify files by port_number(a = port_no.)\n'
	print 'port_a_1.log: analyzed files(a = port_no.)\n'
	print 'transaction1.log: all the transaction data\n'
	print 'transaction2.log: all the transactions data that have been analyzed\n'
	print 'TTC****.xls: transaction data that has been exportd into .xls format\n'
	print '*' * 60 

if __name__ == '__main__':
	main()