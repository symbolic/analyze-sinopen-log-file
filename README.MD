# 解析中石化通讯日志
**setup.py:** ***打包成.exe文件，在没有python环境的电脑上运行***

**singleport:** ***test.py test文件***

**sinopec.py:** ***把原始日志按端口号分成多个文件(文件名：report/port_1.log)，提取交易数据到xls文件（文件名：TTC20160614.xls），解析日志信息(文件名：report/port_1_1.log)***

**sinopec2.py:**  ***功能和sinopec.py相同，不同之处在于把一条通讯日志中的2个状态分成了两行日志***

**remove_30.py:**  ***从sinopec.py分成的文件（port_1.log）中，删除轮询日志，使日志文件大幅度减小（（port_1_min.log））***

**remove_line.py:**  ***删除无效行，test文件***

**remove.py:**  ***从src.txt中删除重复的交易信息result.txt***
