# -*- coding: gbk -*-


from make_output import *
from make_helper import *

# Ĭ�������ļ�·��
PATH = "D:/xyf/data/"
with open("config.ini", "r") as f:
	for s in f.readlines():
		lst = s.split("=")
		if lst[0] == "data_path":
			PATH = lst[1].strip()
	f.close()
