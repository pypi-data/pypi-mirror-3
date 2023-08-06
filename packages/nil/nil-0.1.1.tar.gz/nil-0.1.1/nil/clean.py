#coding:utf-8

import os
import fnmatch

def all_file(root, patterns = '*', ignore_dirs = None, single_level = False, yield_folders = False):
    """
    root:            需要遍历的目录
    patterns：       需要查找的文件，以；为分割的字符串
    single_level:    是否只遍历单层目录，默认为否
    yield_folders:   是否包含目录本身，默认为否
    """
    patterns = patterns.split(';')
    if ignore_dirs: ignore_dirs = ignore_dirs.split(',')
    for path, subdirs, files in os.walk(root):
        if ignore_dirs:
            for dir in ignore_dirs:
                if not dir in subdirs:
                    continue
                subdirs.remove(dir)
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern.strip()):# 去除pattern两端的空格
                    yield os.path.join(path, name)
        if single_level:
            break

def clean(args, logger=None):
    filter = args.filter
    ignore_dirs = args.ignore_dirs
    path = args.path
    for filter in filter.split(','):
        for file in all_file(path, filter, ignore_dirs):
            if logger:
                logger.debug(file)
            else:
                print file
            try:
                os.remove(os.path.realpath(file))
            except:
                pass

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Clean your files.')
    parser.add_argument('path', default='.', nargs='?',
                      help="clean path")
    parser.add_argument('--filter', default='*.pyc',
                      help="fliter which file split by ,")
    parser.add_argument('--ignore-dirs', default='',
                      help="ignore some dirs split by ,")
    args = parser.parse_args()
    clean(args)

