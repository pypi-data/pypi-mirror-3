#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
	a = 1
except Exception, e:
	print 'fail:', e


try:
	b = 2
finally:
	print 'finally'


try:
	c = 3
#except ValueError, v:
#	print 'value error:', v
finally:
	print 'just do it'
