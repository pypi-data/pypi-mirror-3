# -*- coding: utf-8 -*-

def add_linebreak(iterables):
    ret = []
    for i in iterables:
        if i:
            ret.append("{0}\n".format(i))
        else:
            ret.append(i)
    return ret

def del_linebreak(iterables):
    ret = []
    for i in iterables:
        if i:
            ret.append(i.replace("\n", ""))
        else:
            ret.append(i)
    return ret
