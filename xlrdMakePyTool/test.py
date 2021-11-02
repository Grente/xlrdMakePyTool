# -*- coding: gbk -*-

from make_def import *
from make_helper import *
import xlrd
import time


def make_pydata(bk):
	# ��ͨ�������

	sh = bk.sheet_by_name("�齱����".decode("GBK"))
	headers = ["����ID", "����ID", "��������", "����"]
	fd = load_sheet(sh, headers)
	out_str = "OUT_DATA = {\n"
	for reward, item, amount, prop in fd:
		out_str += "\t({}), {}, {}): {},\n".format(int(reward), int(item), int(amount), int(prop))
	out_str += "}\n"
	err = output_file(PATH + "testdata.py", out_str, "��ϲ�������")
	if err:
		return err


def make_pydata_by_format(bk):
	# ����py�ļ�
	headers = [
		("�������", "{int"),
		("����ID", "{int"),
		("��������", "-"),
		("����", "int}"),
		("�һ�����", "int"),
		("�һ�����", "int"),
		("�ƺ�ID", "(int"),
		("ʱ��", "int"),
	]
	sh = bk.sheet_by_name("���߽���".decode("GBK"))
	err = sheet2pydata(sh, headers, PATH + "testdata.py", "ITEM_REWARD_DATA", "���߽���")
	if err:
		return err

	# ʹ��ת������_make_time����ע�ͺ���_comment
	def _make_time(tmstring):
		if not tmstring:
			return 0
		return int(time.mktime(time.strptime(tmstring, '%Y-%m-%d %H:%M')))

	def _comment(data):
		return data[2]

	headers = [
		("����ʱ��", "{int", _make_time),
		("�������", "{int#", None, None, _comment),
		("����id", "int"),
		("������", "-"),
		("����", "int"),
		("����", "int"),
		("�һ�����", "int"),
		("�Ƿ񹫸�", "bool"),
		("��������", "str"),
	]
	sh = bk.sheet_by_name("�����".decode("GBK"))
	err = sheet2pydata(sh, headers, PATH + "testdata.py", "ACTIVITY_DATA", "���������")
	if err:
		return err

	# ʹ��ģ�� �����������
	def _template(data, deep):
		s = "("
		for val, replace in data[:-1]:
			s += "%s, " % val
		s += ") : "
		s += data[-1][0]  # ����
		return s

	headers = [
		("����ID", "{int", None, (_template, None)),
		("����ID", "int"),
		("��������", "int"),
		("����", "int"),
	]
	sh = bk.sheet_by_name("�齱����".decode("GBK"))
	err = sheet2pydata(sh, headers, PATH + "testdata.py", "LUCKY_DRAW_DATA", "�齱��������")
	if err:
		return err

	# ʹ��ģ�崫��
	def _make_prop_dict(data, deep):
		STR2PROPKEY = {"�˺�": "ATT", "����": "AP", "����": "HP"}
		s = []
		for row_data, replace_str in data:
			val = int(row_data)
			s.append("\"{}\" : {}".format(STR2PROPKEY[replace_str], val))
		return ", ".join(s)

	headers = [
		("�ȼ�", "{int"),
		("����ID", "int"),
		("���ܵȼ�", "int",),
		("�˺�", "{int", None, (_make_prop_dict, "�˺�")),
		("����", "int", None, "����"),
		("����", "int", None, "����"),
	]
	sh = bk.sheet_by_name("���Լӳ�".decode("GBK"))
	err = sheet2pydata(sh, headers, PATH + "testdata.py", "PROP_DATA", "���Լӳ�")
	if err:
		return err


def make_data_by_format(bk):
	# ��������
	headers = [
		("�������", "{int"),
		("����ID", "{int"),
		("��������", "-"),
		("����", "int}"),
		("�һ�����", "int"),
		("�һ�����", "int"),
		("�ƺ�ID", "(int"),
		("ʱ��", "int"),
	]
	sh = bk.sheet_by_name("���߽���".decode("GBK"))
	return sheet2data(sh, headers)


if __name__ == "__main__":
	bk = xlrd.open_workbook("���Ա��.xls")
	make_pydata(bk)
	make_pydata_by_format(bk)
	print make_data_by_format(bk)
