#!/usr/bin/python
#-*- coding:utf-8 -*-
from idaapi import *
import idc
import idautils

fo = open("bb.txt", "w")

def FUNC_CFG(func):

	bb_count = 0

	#得到该函数的CFG，接下来我们需要将其转化成可用的形式
	cfg=FlowChart(func)  

	for block in cfg:
		bb_start = hex(block.startEA)
		bb_end = hex(block.endEA)
		if bb_start != bb_end:
			bb_count += 1
			fo.write(bb_start[:-1])
			fo.write(" ")
			fo.write(bb_end[:-1])
			fo.write("\n")
	
	return bb_count


def main():
	bb_count = 0
	f_count = 0
	for func_ea in idautils.Functions():
		print(func_ea,'type',type(func_ea))
		func_name=idc.GetFunctionName(func_ea)
		f=get_func(func_ea)
		f_count += 1
		bb_count+=FUNC_CFG(f)
	print('number of basic blocks:{}\nnumber of functions:{}'.format(bb_count,f_count))
	fo.close()


if __name__=='__main__':
	main()