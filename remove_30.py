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

def port_list():		#过滤文件，删除所有的30
	fp_src = open(sys.argv[1], 'r')
	if fp_src:
		print 'open source file success'
		fp_dest = open(sys.argv[1].split('.')[0]+'_min.log', 'w')
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
	print 'finished.\n'
		
	
def main():

	if len(sys.argv) != 2:
		command = sys.argv[0].split('\\')[len(sys.argv[0].split('\\')) - 1]
		print 'Remove 30 data from port log file'
		print 'Usage: ' + command + ' port_*.log'
		sys.exit()
		
	version = 'Version: 1.0.0.1'
	print '\n****** Analyze port log file ******\n' + version
	print 'Please waitting...'
	port_list()

if __name__ == '__main__':
	main()