#coding:utf-8

import os
import fnmatch

def all_file(root, patterns = '*', single_level = False, yield_folders = False):
    """
    root:            需要遍历的目录
    patterns：       需要查找的文件，以；为分割的字符串
    single_level:    是否只遍历单层目录，默认为否
    yield_folders:   是否包含目录本身，默认为否
    """
    patterns = patterns.split(';')
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern.strip()):# 去除pattern两端的空格
                    yield os.path.join(path, name)
        if single_level:
            break

def clean(filter, args, logger=None):
    path = args[0] if len(args) == 1 else '.'
    for filter in filter.split(','):
        for file in all_file(path, filter):
            if logger:
                logger.debug(file)
            else:
                print file
            try:
                os.remove(os.path.realpath(file))
            except:
                pass

def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] <path>")
    parser.add_option('--filter', default='*.pyc',
                      help="fliter which file split by ,")
    options, args = parser.parse_args()
    clean(options.filter, args)

