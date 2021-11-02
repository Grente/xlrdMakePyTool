# -*- coding: gbk -*-

from make_def import *
from make_helper import *
import xlrd
import time


def make_pydata(bk):
	# 普通组合数据

	sh = bk.sheet_by_name("抽奖概率".decode("GBK"))
	headers = ["奖励ID", "道具ID", "道具数量", "概率"]
	fd = load_sheet(sh, headers)
	out_str = "OUT_DATA = {\n"
	for reward, item, amount, prop in fd:
		out_str += "\t({}), {}, {}): {},\n".format(int(reward), int(item), int(amount), int(prop))
	out_str += "}\n"
	err = output_file(PATH + "testdata.py", out_str, "组合测试数据")
	if err:
		return err


def make_pydata_by_format(bk):
	# 生成py文件
	headers = [
		("道具序号", "{int"),
		("道具ID", "{int"),
		("道具名称", "-"),
		("数量", "int}"),
		("兑换次数", "int"),
		("兑换积分", "int"),
		("称号ID", "(int"),
		("时长", "int"),
	]
	sh = bk.sheet_by_name("道具奖励".decode("GBK"))
	err = sheet2pydata(sh, headers, PATH + "testdata.py", "ITEM_REWARD_DATA", "道具奖励")
	if err:
		return err

	# 使用转换函数_make_time，和注释函数_comment
	def _make_time(tmstring):
		if not tmstring:
			return 0
		return int(time.mktime(time.strptime(tmstring, '%Y-%m-%d %H:%M')))

	def _comment(data):
		return data[2]

	headers = [
		("开服时间", "{int", _make_time),
		("道具序号", "{int#", None, None, _comment),
		("道具id", "int"),
		("道具名", "-"),
		("数量", "int"),
		("积分", "int"),
		("兑换次数", "int"),
		("是否公告", "bool"),
		("公告内容", "str"),
	]
	sh = bk.sheet_by_name("活动奖励".decode("GBK"))
	err = sheet2pydata(sh, headers, PATH + "testdata.py", "ACTIVITY_DATA", "活动奖励数据")
	if err:
		return err

	# 使用模板 重新组合数据
	def _template(data, deep):
		s = "("
		for val, replace in data[:-1]:
			s += "%s, " % val
		s += ") : "
		s += data[-1][0]  # 概率
		return s

	headers = [
		("奖励ID", "{int", None, (_template, None)),
		("道具ID", "int"),
		("道具数量", "int"),
		("概率", "int"),
	]
	sh = bk.sheet_by_name("抽奖概率".decode("GBK"))
	err = sheet2pydata(sh, headers, PATH + "testdata.py", "LUCKY_DRAW_DATA", "抽奖概率数据")
	if err:
		return err

	# 使用模板传参
	def _make_prop_dict(data, deep):
		STR2PROPKEY = {"伤害": "ATT", "真气": "AP", "体质": "HP"}
		s = []
		for row_data, replace_str in data:
			val = int(row_data)
			s.append("\"{}\" : {}".format(STR2PROPKEY[replace_str], val))
		return ", ".join(s)

	headers = [
		("等级", "{int"),
		("技能ID", "int"),
		("技能等级", "int",),
		("伤害", "{int", None, (_make_prop_dict, "伤害")),
		("真气", "int", None, "真气"),
		("体质", "int", None, "体质"),
	]
	sh = bk.sheet_by_name("属性加成".decode("GBK"))
	err = sheet2pydata(sh, headers, PATH + "testdata.py", "PROP_DATA", "属性加成")
	if err:
		return err


def make_data_by_format(bk):
	# 返回数据
	headers = [
		("道具序号", "{int"),
		("道具ID", "{int"),
		("道具名称", "-"),
		("数量", "int}"),
		("兑换次数", "int"),
		("兑换积分", "int"),
		("称号ID", "(int"),
		("时长", "int"),
	]
	sh = bk.sheet_by_name("道具奖励".decode("GBK"))
	return sheet2data(sh, headers)


if __name__ == "__main__":
	bk = xlrd.open_workbook("测试表格.xls")
	make_pydata(bk)
	make_pydata_by_format(bk)
	print make_data_by_format(bk)
