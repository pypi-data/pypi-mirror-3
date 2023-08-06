#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import cseg

s = cseg.Seg()

s.set_charset('utf-8')
s.add_dict('data/dict.utf8.xdb')
s.set_rule('data/rules.utf8.ini')


for l in sys.stdin:
	ret = s.seg(l.strip())
	for r in ret:
		print '%s\t%f\t%s' % r

	ret = s.stat(l.strip())
	for r in ret:
		print '%s\t%f\t%d\t%s' % r

	
#s.feed('我是一只小小鸟')
