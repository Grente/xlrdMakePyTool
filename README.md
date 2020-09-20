# xlrdMakePyTool  
# xlrd游戏配置导表工具  
基于xlrd的超方便的python导表工具，支持python多种数据结构  
****
 
环境：python2.7  
需安装依赖库：  
xlrd  
支持数据格式：python  
 编码：GBK

使用方法：  
----
1、编辑config.ini设置路径  
2、定义转换格式配置说  
3、调用make_helper的sheet2pydata接口生成数据  



定义转换格式配置说明：
----
```
headers = [  
	(列名, 解析说明, 自定义转换函数(可选), 替换模板(可选), 注释函数(可选，默认为当前值))  
]

解析说明 = 解析前缀 + 输出类型 + 解析后缀  

解析前缀	 
{               解析一个字典，如果未指定key第一列作为key  
[				解析一个列表  
(				解析一个元祖  
+				该列同后续的列合并  
-				该列将被忽略  
#				增加注释，在该项上面单独一行  
&				该列内容不能重复，字典key默认不能重复  
*				指定该列作为字典的key  
!				阻止自动换行  

输出类型		int,hex,float,bool,string,str  

解析后缀  
}				结束{嵌套  
]				结束[嵌套  
)				结束(嵌套  
[				指定子项以[]包裹  
(				指定子项以()包裹，当项数大于1且未指定时，默认使用()包裹  
#				增加注释，添加在末尾  
!				阻止子项自动换行  
!!				强制子项自动换行  

自定义转换函数	传入参数为list，如果有合并的列，合并的列在前，否则只有一项，如果存在不合法的数值可以抛出ParseException异常  
支持格式		自定义转换函数 | (自定义转换函数, 输出格式串)  

替换模板		目前仅支持行模板，列模板暂不支持，模板支持嵌套，可以部分使用  
支持格式		替身 | (替换模板, 替身) | (上一级替身, 替换模板, 替身)  

注释函数		传入参数为list，为整个数据列  
```


参考例子：
----

表格：
| 奖励ID | 道具ID | 道具数量 | 
| ----- | ----- | ----- | 
| 1 | 175700 | 1 | 
| 2 | 174049 | 1 | 
| 3 | 174033 | 1 | 

定义转换格式配置：
```
	headers = [
		("道具ID", "(int"),
		("道具ID", "int"),
		("道具数量", "int"),
]
```
实际效果：
```
(
    (1, 175700, 1),
    (1, 174049, 1),
    (1, 174033, 1),
)
```


详情例子参考test.py