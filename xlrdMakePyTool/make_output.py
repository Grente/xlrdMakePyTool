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
	:param filename: 文件名
	:param output: 输出的数据
	:param key_txt: 文本关键字
	:param badd: 新增标志，是否在原文件修改数据
	:param file_template: 表头
	:return:
	'''
	if key_txt is None:
		prefix = "# 自动生成开始，不要手动修改"
		suffix = "# 自动生成完毕，不要手动修改"
	else:
		prefix = "# %s自动生成开始，不要手动修改" % key_txt
		suffix = "# %s自动生成完毕，不要手动修改" % key_txt
	badd = _get_add_flag(filename, badd)  # 是否在原文件修改数据

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

		# 真正开始写内容
		file = open(filename, "wb")
		file.write(msg)
		file.close()
		file = open(filename, "rU")

	msg = file.read()
	file.close()

	# 根据key_txt查找位数位置
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
			return "%s格式有误，无法导出数据<%s>" % (filename, prefix)
	else:
		msg = _gen_output(msg[:s + len(prefix)], output, msg[e:])
		file = open(filename, "wb")
		file.write(msg)
		file.close()
