# -*- coding: gbk -*-

from make_output import *

import xlrd
import time

OUT_CHARSET = "GBK"

def encode_str(s):
	if isinstance(s, unicode):
		return s.encode(OUT_CHARSET)
	else:
		return s


def decode_str(s):
	return s.decode(OUT_CHARSET)


def parse_int(*args):
	arg = args[0]
	if isinstance(arg, (str, unicode)) and len(arg.strip()) == 0:
		return 0

	try:
		val = int(args[0])
	except:
		try:
			val = int(args[0], 16)
		except:
			raise ParseException("parse_int")

	return val


def parse_hex(*args):
	arg = args[0]
	if isinstance(arg, (str, unicode)) and len(arg.strip()) == 0:
		return 0

	try:
		val = int(args[0], 16)
	except:
		raise ParseException("parse_hex")

	return val


def parse_float(*args):
	arg = args[0]
	if isinstance(arg, (str, unicode)) and len(arg.strip()) == 0:
		return 0.0

	try:
		val = float(args[0])
	except:
		raise ParseException("parse_float")

	return val


def parse_str(*args):
	try:
		val = str(args[0])
	except:
		raise ParseException("parse_str")

	return val


def parse_bool(*args):
	try:
		val = bool(args[0])
	except:
		raise ParseException("parse_bool")

	return val


parser_func = {
	"int": (parse_int, "%d"),
	"hex": (parse_hex, "0x%x"),
	"float": (parse_float, "%.2f"),
	"bool": (parse_bool, "%s"),
	"str": (parse_str, "\"%s\""),
	"string": (parse_str, "\"%s\""),
}

closeprefix = {
	"{": "}",
	"[": "]",
	"(": ")",
}

"""
����˵��
headers = [
	(����, ����˵��, �Զ���ת������(��ѡ), �滻ģ��(��ѡ), ע�ͺ���(��ѡ��Ĭ��Ϊ��ǰֵ))
]

����˵�� = ����ǰ׺ + ������� + ������׺

����ǰ׺	
{				����һ���ֵ䣬���δָ��key��һ����Ϊkey
[				����һ���б�
(				����һ��Ԫ��
+				����ͬ�������кϲ�
-				���н�������
$				ģ����ѡ���Զ���ת���������滻ģ�嶨��˳�򽻻�����ǰ�ֵ䡢�б�Ԫ������Ч
#				����ע�ͣ��ڸ������浥��һ��
&				�������ݲ����ظ����ֵ�keyĬ�ϲ����ظ�
*				ָ��������Ϊ�ֵ��key
!				��ֹ�Զ�����

�������		int,hex,float,bool,string,str

������׺
}				����{Ƕ��
]				����[Ƕ��
)				����(Ƕ��
[				ָ��������[]����
(				ָ��������()����������������1��δָ��ʱ��Ĭ��ʹ��()����
#				����ע�ͣ������ĩβ
!				��ֹ�����Զ�����
!!				ǿ�������Զ�����

�Զ���ת������	�������Ϊlist������кϲ����У��ϲ�������ǰ������ֻ��һ�������ڲ��Ϸ�����ֵ�����׳�ParseException�쳣
֧�ָ�ʽ		�Զ���ת������ | (�Զ���ת������, �����ʽ��)

�滻ģ��		Ŀǰ��֧����ģ�壬��ģ���ݲ�֧�֣�ģ��֧��Ƕ�ף����Բ���ʹ��
֧�ָ�ʽ		���� | (�滻ģ��, ����) | (��һ������, �滻ģ��, ����)

ע�ͺ���		�������Ϊlist��Ϊ����������
"""


def parse_headers(headers, load_headers, load_cfg):
	parse_header = None
	parse_cfg = None
	prefix = ""
	suffix = ""
	spec_str = ""
	spec_suf = ""
	parse_stack = []
	parse_funlag = [""]
	for h in headers:
		s = h[1]
		skip = ""
		while s and s[0] in ("#", "&", "*", "!", "{", "[", "(", "+", "-"):
			if s[0] in ("{", "[", "("):
				if prefix:
					s = s[1:]
					continue
				if not parse_stack:
					parse_stack = [(s[0], load_headers, load_cfg)]
				else:
					top = parse_stack[-1]
					top[1].append([])
					top[2].append([])
					parse_stack.append((s[0], top[1][-1], top[2][-1]))
					parse_funlag.append("")
				parse_header = parse_stack[-1][1]
				parse_cfg = parse_stack[-1][2]
				prefix = s[0]
			elif s[0] in ("#", "&", "*", "!"):
				spec_str += s[0]
			else:
				skip = s[0]
			s = s[1:]

		if skip in ("+", "-"):
			head_name = h[0]
			cfg = (h[0], "", skip, "", spec_str, spec_suf, None, "", ("", "", ""), None)
			parse_header.append(head_name)
			parse_cfg.append(cfg)
			continue

		pops = []
		while s and s[-1] in ("#", "&", "*", "!", "[", "(", ")", "]", "}"):
			if s[-1] in ("[", "("):
				if prefix != "":
					suffix = s[-1]
			elif s[-1] in ("#", "&", "*", "!"):
				if s[-1] in ("#", "!"):
					spec_suf += s[-1]
				else:
					spec_str += s[-1]
			else:
				pops.append(s[-1])
			s = s[:-1]

		if s in parser_func:
			# if prefix == "{" and "&" not in spec_str:
			#	spec_str += "&"
			parse_fun = parser_func[s][0]
			fmt = parser_func[s][1]
			comment_fun = None
			rep_str = ""
			temp_str = ""
			subrep_str = ""
			parse_funidx = 0
			temp_stridx = 1
			for idx, hdata in enumerate(h[2:]):
				if idx == parse_funidx:
					if type(hdata) in (tuple, list):
						if len(hdata) > 0 and hdata[0]:
							parse_fun = hdata[0]
						if len(hdata) > 1 and hdata[1]:
							fmt = hdata[1]
					else:
						if hdata != None:
							parse_fun = hdata
				elif idx == temp_stridx:
					if type(hdata) in (tuple, list):
						if len(hdata) == 1:
							subrep_str, = hdata
						if len(hdata) == 2:
							temp_str, subrep_str = hdata
						elif len(hdata) >= 3:
							rep_str, temp_str, subrep_str = hdata
					else:
						if hdata != None:
							subrep_str = hdata
				elif idx == 2:
					if hdata != None:
						comment_fun = hdata
			templates = (rep_str, temp_str, subrep_str)
			parse_header.append(h[0])
			parse_cfg.append((h[0], s, prefix, suffix, spec_str, spec_suf, parse_fun, fmt, templates, comment_fun))
			prefix = ""
			suffix = ""
			spec_str = ""
			spec_suf = ""
		else:
			return "parse_headers ��֧������ %s" % (s)

		while len(parse_stack) > 1 and pops:
			p = parse_stack[-1][0]
			if closeprefix[p] in pops:
				pops.remove(closeprefix[p])
				parse_stack.pop()
				parse_header = parse_stack[-1][1]
				parse_cfg = parse_stack[-1][2]
				parse_funlag.pop()
			else:
				# error
				break


def output_headers(headers, deep=0):
	row_data = []
	expand = False
	for h in headers:
		if type(h) is list:
			row_data.append(output_headers(h, deep + 1))
			expand = True
		else:
			row_data.append("%s" % (h))

	if not expand:
		return "[" + ", ".join(row_data) + "]"

	s = "["
	newline = False
	for idx, row in enumerate(row_data):
		if type(headers[idx]) is list:
			s += "\n%s" % ("\t" * (deep + 1)) + row
			if idx < len(row_data) - 1:
				s += ","
			newline = True
		else:
			if newline:
				s += "\n%s" % ("\t" * (deep + 1))
				newline = False
			s += row
			if idx < len(row_data) - 1:
				s += ","
	s += "\n%s]" % ("\t" * deep)
	return s


def get_dict_key_idx(load_cfg):
	dkey_idx = 0
	for cfg in load_cfg:
		if type(cfg) is list:
			finddkey = False
			for subcfg in cfg:
				if type(subcfg) is list:
					continue
				head_name, data_type, prefix, suffix, spec_str, spec_suf = subcfg[:6]
				if prefix in ("{", "[", "(") and "*" in spec_str:
					finddkey = True
					break
			if finddkey:
				break
			else:
				dkey_idx += 1
				continue

		head_name, data_type, prefix, suffix, spec_str, spec_suf = cfg[:6]
		if "*" in spec_str:
			break
		elif prefix not in ("+", "-"):
			dkey_idx += 1
	else:
		dkey_idx = 0
	return dkey_idx


def get_key_idx(load_cfg):
	for idx, cfg in enumerate(load_cfg):
		if type(cfg) is list:
			continue
		head_name, data_type, prefix, suffix, spec_str, spec_suf = cfg[:6]
		if prefix in ("{", "[", "("):
			return idx
	else:
		raise ParseException("get_key_idx invalid load_cfg")


def output_datas(fd, load_cfg, deep=0, out_template=None):
	cfg_idx = get_key_idx(load_cfg)
	data_cfg = load_cfg[cfg_idx]
	dkey_idx = get_dict_key_idx(load_cfg)
	sdata = []
	data_template = data_cfg[8][1]
	repeatd = {}
	for idx, rd in enumerate(fd):
		args = []
		row_data = []
		row_template = data_template
		replace_lst = []
		key_val = 0
		expand_lst = []
		for i, d in enumerate(rd):
			repeatd.setdefault(i, [])
			cfg = load_cfg[i]
			if type(cfg) is list:
				head_name, data_type, prefix, suffix, spec_str, spec_suf, parse_fun, fmt, templates, comment_fun = cfg[
					get_key_idx(cfg)]
				min_expand = 3 if data_cfg[2] == "{" else 2
				if (data_template and out_template != None) or len(load_cfg) < min_expand:
					sub_data = output_datas(d, cfg, deep + 1)
				else:
					sub_data = output_datas(d, cfg, deep + 2)
				if "&" in spec_str or (data_cfg[2] == "{" and len(row_data) == dkey_idx and not row_template):
					if sub_data in repeatd[i]:
						msg = "%s %s �ظ�" % (head_name, str(sub_data))
						raise ParseException(msg)
					repeatd[i].append(sub_data)
				row_data.append(sub_data)
				replace_lst.append(templates[0])
				if len(row_data) == dkey_idx + 1:
					key_val = sub_data
				expand_lst.append(len(row_data) - 1)
				continue

			head_name, data_type, prefix, suffix, spec_str, spec_suf, parse_fun, fmt, templates, comment_fun = cfg
			if prefix == "+":
				args.append(d)
				continue
			if prefix == "-":
				continue

			args.append(d)
			try:
				val = parse_fun(*args)
			except ParseException, e:
				msg = "%s Fail %s" % (e.args[0], ", ".join(map(str, args)))
				raise ParseException(msg)
			args = []
			if "&" in spec_str or (data_cfg[2] == "{" and len(row_data) == dkey_idx and not row_template):
				if val in repeatd[i]:
					msg = "%s %s �ظ�" % (head_name, str(val))
					raise ParseException(msg)
				repeatd[i].append(val)
			row_data.append(fmt % val)
			replace_lst.append(templates[2])
			if len(row_data) == dkey_idx + 1:
				key_val = val
			if spec_suf.count("!") == 2:
				expand_lst.append(len(row_data) - 1)

		head_name, data_type, prefix, suffix, spec_str, spec_suf, parse_fun, fmt, templates, comment_fun = data_cfg
		comment = rd[cfg_idx]
		if comment_fun:
			comment = comment_fun(rd)
		comment_pos = 0
		if "#" in spec_str:
			comment_pos = 1
		elif "#" in spec_suf:
			comment_pos = 2

		if row_template:
			if callable(row_template):
				row_template = row_template(zip(row_data, replace_lst), deep)
			else:
				for i, sub_data in enumerate(row_data):
					if replace_lst[i]:
						row_template = row_template.replace(replace_lst[i], sub_data)
			if row_template:
				sdata.append((key_val, row_template, comment, comment_pos))
			continue

		min_expand = 3 if prefix == "{" else 2
		if len(row_data) >= min_expand and suffix not in ("[", "("):
			suffix = "("
		if suffix and spec_suf.count("!") != 1:
			expand = False
			expandon = False
			for exidx in xrange(len(row_data)):
				if exidx == dkey_idx and prefix == "{":
					continue
				if exidx in expand_lst:
					row_data[exidx] = "\n%s" % ("\t" * (deep + 2)) + row_data[exidx]
					expand = True
					expandon = True
				elif expand:
					row_data[exidx] = "\n%s" % ("\t" * (deep + 2)) + row_data[exidx]
					expand = False
			if expandon:
				lastidx = -2 if dkey_idx == len(row_data) - 1 else -1
				row_data[lastidx] = row_data[lastidx] + "\n%s" % ("\t" * (deep + 1))
		if prefix == "{" and len(row_data) >= 2:
			srow = ", ".join(row_data[:dkey_idx] + row_data[dkey_idx + 1:])
			if suffix:
				srow = suffix + srow + closeprefix[suffix]
			srow = srow.replace(", \n", ",\n")
			sdata.append((key_val, "%s : %s" % (row_data[dkey_idx], srow), comment, comment_pos))
		else:
			srow = ", ".join(row_data)
			if suffix:
				if suffix == "(" and len(row_data) == 1:
					srow += ","
				srow = suffix + srow + closeprefix[suffix]
			srow = srow.replace(", \n", ",\n")
			sdata.append((key_val, srow, comment, comment_pos))

	if out_template != None:
		out_template.extend(sdata)
	head_name, data_type, prefix, suffix, spec_str, spec_suf, parse_fun, fmt, templates, comment_fun = data_cfg
	if (len(sdata) > 1 and spec_str.count("!") != 1) or (spec_str.count("!") == 2) or (deep == 0):
		s = "%s\n" % (prefix)
		for key_val, sr, comment, comment_pos in sdata:
			if comment_pos == 1:
				s += "%s  # %s\n" % ("\t" * (deep + 1), comment)
				s += "%s%s,\n" % ("\t" * (deep + 1), sr)
			elif comment_pos == 2:
				s += "%s%s,  # %s\n" % ("\t" * (deep + 1), sr, comment)
			else:
				s += "%s%s,\n" % ("\t" * (deep + 1), sr)
		s += "%s%s" % ("\t" * deep, closeprefix[prefix])
	else:
		s = "%s" % (prefix)
		lssr = []
		for key_val, sr, comment, comment_pos in sdata:
			lssr.append(sr)
		s += ", ".join(lssr)
		if len(sdata) == 1 and prefix == "(":
			s += ","
		s += "%s" % (closeprefix[prefix])
	return s


def _get_resort_idx(real_headers, load_headers):
	idx_lst = []  # ɶ���ģ�
	check_idx_lst = []  # ��ʵ����ֵ
	for h in load_headers:
		if type(h) is list:
			sub = _get_resort_idx(real_headers, h)
			idx_lst.append(sub[0])
			check_idx_lst.extend(sub[1])
		else:
			if h not in real_headers:
				raise ParseException("��[%s]������" % (h))
			idx_lst.append(real_headers.index(h))
			check_idx_lst.append(real_headers.index(h))
	if max(check_idx_lst) - min(check_idx_lst) + 1 != len(check_idx_lst):
		raise ParseException("����(%s)�����в�����" % (output_headers(load_headers)))
	idx_lst.append(min(check_idx_lst))

	return idx_lst, check_idx_lst


def _get_real_deaders(real_headers, idx_lst):
	_get_idx = lambda x: x[-1] if type(x) is list else x
	resort_lst = [(x, _get_idx(x)) for x in idx_lst[:-1]]
	resort_lst.sort(key=lambda x: x[1])
	resort_lst = [x[0] for x in resort_lst]
	real_header_lst = []
	for idx in resort_lst:
		if type(idx) is list:
			real_header_lst.append(_get_real_deaders(real_headers, idx))
		else:
			real_header_lst.append(real_headers[idx])
	return real_header_lst


def check_real_headers(sh, headers, load_headers):
	real_headers = []  # ��ʵ��ͷ��˳��
	head_def = set()  # �Զ����ͷ ������ֹ�ظ�
	for idx, head in enumerate(headers):
		try:
			v = sh.cell_value(0, idx)  # ������Ӧ��ʵ�ʵı�ͷ��
		except:
			raise ParseException("�������������������")
		if type(v) is unicode:
			v = encode_str(v)
		elif type(v) is str:
			pass
		else:
			v = str(v)
		real_headers.append(v)
		if head[0] in head_def:
			raise ParseException("������(%s)�ظ�" % (head[0]))
		head_def.add(head[0])
	# v��xlsʵ�ʵı��ʵ�ʵı�ͷ˳��
	# head[0]���ǵ����ʽ����ı�ͷ˳��

	idx_lst, _ = _get_resort_idx(real_headers, load_headers)  # ��ȡ�Զ����ͷ������ֵ
	real_load_headers = _get_real_deaders(real_headers, idx_lst)
	return real_load_headers, idx_lst


def _resort_data(fd, idx_lst):
	_get_idx = lambda x: x[-1] if type(x) is list else x
	resort_lst = [_get_idx(x) for x in idx_lst[:-1]]
	new_resort_lst = sorted(resort_lst)
	resort_lst = [new_resort_lst.index(x) for x in resort_lst]

	for i in xrange(len(fd)):
		fd[i] = [fd[i][idx] for idx in resort_lst]
		for j, idx in enumerate(idx_lst[:-1]):
			if type(idx) is list:
				_resort_data(fd[i][j], idx)

	return fd


def parse_datas(fd, load_cfg, deep=0, deep_keys={}):
	cfg_idx = get_key_idx(load_cfg)
	data_cfg = load_cfg[cfg_idx]
	dkey_idx = get_dict_key_idx(load_cfg)
	datas = []
	repeatd = {}
	for idx, rd in enumerate(fd):
		args = []
		result = []
		deep_keys[deep] = rd[dkey_idx]
		for i, d in enumerate(rd):
			repeatd.setdefault(i, [])
			cfg = load_cfg[i]
			if type(cfg) is list:
				head_name, data_type, prefix, suffix, spec_str, spec_suf, parse_fun, fmt, templates, comment_fun = cfg[
					get_key_idx(cfg)]
				sub_data = parse_datas(d, cfg, deep + 1, deep_keys)
				if "&" in spec_str or (data_cfg[2] == "{" and len(result) == dkey_idx):
					if sub_data in repeatd[i]:
						skey = "\t".join(str(v[1]) for v in sorted(deep_keys.iteritems(), key=lambda x: x[0]))
						msg = "%s %s %s �ظ�" % (deep_keys.get(0, ""), head_name, str(sub_data))
						raise ParseException(msg)
					repeatd[i].append(sub_data)
				result.append(sub_data)
				continue

			head_name, data_type, prefix, suffix, spec_str, spec_suf, parse_fun, fmt, templates, comment_fun = cfg
			if prefix == "+":
				args.append(d)
				continue
			if prefix == "-":
				continue

			args.append(d)
			try:
				val = parse_fun(*args)
			except ParseException, e:
				msg = "%s Fail %s" % (e.args[0], ", ".join(map(str, args)))
				raise ParseException(msg)
			args = []
			if "&" in spec_str or (data_cfg[2] == "{" and len(result) == dkey_idx):
				if val in repeatd[i]:
					msg = "%s %s %s �ظ�" % (deep_keys.get(0, ""), head_name, str(val))
					raise ParseException(msg)
				repeatd[i].append(val)
			# if prefix in ("{", "[", "("):
			#	result = []
			result.append(val)
		datas.append(result)

	head_name, data_type, prefix, suffix, spec_str, spec_suf, parse_fun, fmt, templates, comment_fun = data_cfg
	if prefix == "{":
		d = {}
		if len(load_cfg) > 2 and suffix not in ("[", "("):
			suffix = "("
		for row_data in datas:
			if suffix == "[":
				d[row_data[dkey_idx]] = row_data[:dkey_idx] + row_data[dkey_idx + 1:]
			elif suffix == "(":
				d[row_data[dkey_idx]] = tuple(row_data[:dkey_idx] + row_data[dkey_idx + 1:])
			else:
				d[row_data[dkey_idx]] = row_data[0 if dkey_idx else 1]
	elif prefix in ("[", "("):
		d = []
		if len(load_cfg) > 1 and suffix not in ("[", "("):
			suffix = "("
		for row_data in datas:
			if suffix == "[":
				d.append(row_data)
			elif suffix == "(":
				d.append(tuple(row_data))
			else:
				d.append(row_data[0])
		if prefix == "(":
			d = tuple(d)
	return d


def load_sheet(sh, headers, begin_row=1):
	blst = []
	for y in xrange(begin_row, sh.nrows):
		x = 0
		lst = []
		for h in headers:
			if type(h) is list:
				lst.append(load_list(sh, 0, x, y, h))
				x += get_col(h)
			else:
				d = sh.cell_value(y, x)
				if x == 0 and isinstance(d, (str, unicode)) and len(d) == 0:
					break
				x += 1
				if isinstance(d, unicode):
					try:
						d = encode_str(d)
					except:
						print "������ַ���, %s(%d, %d)" % (encode_str(sh.name), y + begin_row, x), d.encode("utf-8")
						continue
				lst.append(d)
		if len(lst) > 0:
			blst.append(lst)
	return blst


def load_list(sh, base, xs, ys, headers):
	blst = []
	has_sub_list = sum([1 for h in headers if type(h) is list])
	for y in xrange(ys, sh.nrows):
		bd = sh.cell_value(y, base)
		if y > ys and ((not isinstance(bd, (str, unicode))) or len(bd) > 0):
			return blst

		skip = 0
		x = xs
		lst = []
		for h in headers:
			if type(h) is list:
				lst.append(load_list(sh, xs, x, y, h))
				x += get_col(h)
			else:
				d = sh.cell_value(y, x)
				if isinstance(d, (str, unicode)) and len(d) == 0:
					if has_sub_list and x == xs:
						# ����Ϊ���Ҵ������б�ʱ��Ҫ�˳�����Ϊ�����ѱ����б��ȡ
						break
					skip += 1
				x += 1
				if isinstance(d, unicode):
					d = encode_str(d)
				lst.append(d)
		if len(lst) > 0 and skip < len(headers):
			blst.append(lst)
	return blst


def get_col(h):
	cnt = 0
	for f in h:
		if type(f) is list:
			cnt += get_col(f)
		else:
			cnt += 1
	return cnt


# ��ʹ�ú���
def sheet2pydata(sh, headers, outfile, data_name, comment):
	# ������д��py�ļ�����
	load_headers = []
	load_cfg = []
	err = parse_headers(headers, load_headers, load_cfg)
	if err:
		return err

	if type(sh) is list:
		fd = []
		for sheet in sh:
			real_load_headers, resort_idx_lst = check_real_headers(sheet, headers, load_headers)
			land_data = load_sheet(sheet, real_load_headers)
			fd.extend(_resort_data(land_data, resort_idx_lst))
	else:
		real_load_headers, resort_idx_lst = check_real_headers(sh, headers, load_headers)
		land_data = load_sheet(sh, real_load_headers)
		fd = _resort_data(land_data, resort_idx_lst)  # load_sheet ���ݱ�ͷ������������Ӧ�����ݣ�_resort_data��������

	# ���ֺ�����ƴ����
	s = data_name
	s += " = "
	s += output_datas(fd, load_cfg, 0)

	err = output_file(outfile, s, comment)
	if err:
		return err


def sheet2data(sh, headers, begin_row=1):
	# ��������ʽ����
	load_headers = []
	load_cfg = []
	err = parse_headers(headers, load_headers, load_cfg)
	if err:
		return None, err

	if type(sh) is list:
		fd = []
		for sheet in sh:
			real_load_headers, resort_idx_lst = check_real_headers(sheet, headers, load_headers)
			land_data = load_sheet(sheet, load_headers, begin_row)
			fd.extend(_resort_data(land_data, resort_idx_lst))
	else:
		real_load_headers, resort_idx_lst = check_real_headers(sh, headers, load_headers)
		land_data = load_sheet(sh, load_headers, begin_row)
		fd = _resort_data(land_data, resort_idx_lst)

	return parse_datas(fd, load_cfg)



class ParseException(Exception):
	pass