# -*- coding: gbk -*-

import os
import re

FILE_TEMPLATE = """# -*- coding: gbk -*-"""


def _get_add_flag(filename, badd):
	return True


def _gen_output(prefix, output, suffix):
	msg = prefix
	if not output.startswith("\n") and not output.startswith("\r\n") and not prefix.endswith(
			"\n") and not prefix.endswith("\r\n"):
		msg += "\n"
	msg += output
	if not output.endswith("\n") and not output.endswith("\r\n") and not suffix.startswith(
			"\n") and not suffix.startswith("\r\n"):
		msg += "\n"
	msg += suffix
	return msg


def _enable_new_file(filename):
	return True


def output_file(filename, output, key_txt=None, badd=None, file_template=None):
	'''
	:param filename: �ļ���
	:param output: ���������
	:param key_txt: �ı��ؼ���
	:param badd: ������־���Ƿ���ԭ�ļ��޸�����
	:param file_template: ��ͷ
	:return:
	'''
	if key_txt is None:
		prefix = "# �Զ����ɿ�ʼ����Ҫ�ֶ��޸�"
		suffix = "# �Զ�������ϣ���Ҫ�ֶ��޸�"
	else:
		prefix = "# %s�Զ����ɿ�ʼ����Ҫ�ֶ��޸�" % key_txt
		suffix = "# %s�Զ�������ϣ���Ҫ�ֶ��޸�" % key_txt
	badd = _get_add_flag(filename, badd)  # �Ƿ���ԭ�ļ��޸�����

	try:
		file = open(filename, "rU")
	except IOError:
		if not _enable_new_file(filename):
			return

		dirname = os.path.dirname(filename)
		if not os.path.exists(dirname):
			os.makedirs(dirname)

		if not file_template:
			file_template = FILE_TEMPLATE
		msg = file_template + "\n\n" + prefix + "\n" + suffix + "\n"

		# ������ʼд����
		file = open(filename, "wb")
		file.write(msg)
		file.close()
		file = open(filename, "rU")

	msg = file.read()
	file.close()

	# ����key_txt����λ��λ��
	s = msg.find(prefix)
	e = msg.find(suffix, s)
	if s == -1 or e == -1:
		if badd:
			msg += "\n"
			msg += prefix
			msg = _gen_output(msg, output, suffix)
			msg += "\n"
			file = open(filename, "wb")
			file.write(msg)
			file.close()
		else:
			return "%s��ʽ�����޷���������<%s>" % (filename, prefix)
	else:
		msg = _gen_output(msg[:s + len(prefix)], output, msg[e:])
		file = open(filename, "wb")
		file.write(msg)
		file.close()
