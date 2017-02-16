# -*- coding: utf-8 -*-
#fa c0 00 31 00 01 30 78 1e
def remove30():
	fp = open('temp1.txt')
	fp2 = open('temp2.txt', 'w')
	line = fp.readline()
	if len(line) >= 10:
		line = line.split(': ')
	while line and (len(line) != 0):
		i = 1
		while i < len(line):
			fp2.write(line[i])
			i += 1
		
		line = fp.readline()
		if len(line) >= 10:
			line = line.split(': ')

	fp.close()
	fp2.close()


if __name__ == '__main__':
	remove30()