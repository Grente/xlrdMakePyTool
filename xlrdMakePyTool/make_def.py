# -*- coding: gbk -*-



# Ĭ�������ļ�·��
PATH = "./data/"
with open("config.ini", "r") as f:
	for s in f.readlines():
		lst = s.split("=")
		if lst[0] == "data_path":
			PATH = lst[1].strip()
	f.close()
