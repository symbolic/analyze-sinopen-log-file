#!D:\Python\Python27\python.exe
#-*- coding: utf-8 -*-

def main():
	src = open("src.txt", 'r')
	dest = open('result.txt', 'w')
	
	oneline = src.readline()
	lastTTC = "0"
	while oneline:
		currentTTC = oneline.split('\t')[3]
		if currentTTC != lastTTC:
			dest.write(oneline)
			lastTTC = currentTTC
			
		oneline = src.readline()
	
	src.close()
	dest.close()
	
if __name__ == '__main__':
	main()