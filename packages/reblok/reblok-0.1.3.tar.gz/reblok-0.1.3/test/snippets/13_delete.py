#!/usr/bin/env python
# -*- coding: utf8 -*-

c = 3.14
def func1(b):
	a = 23
	del a
	del b
	global c; del c

func1(42)
