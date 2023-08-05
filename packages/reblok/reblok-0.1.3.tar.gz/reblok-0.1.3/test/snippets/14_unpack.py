#!/usr/bin/env python
# -*- coding: utf8 -*-

def func1():
	global b
	c= [0,1,2]
	(a, b, c[0]) = (10, 11, 12)

def func2():
	global b
	l = ((1,2), (3,4))

	for (a, b) in l:
		c = 0

func1(); func2()
