#!/usr/bin/env python2
# coding=utf-8

# Last modified: <2012-08-05 19:37:10 Sunday by richard>

# @version 0.1
# @author : Richard Wong
# Email: chao787@gmail.com
def is_type(re_pattern, s):
    m = re_pattern.match(s)
    if m == None or m.span() != (0, len(s)):
        return False
    return True


# org_util.py ended here
