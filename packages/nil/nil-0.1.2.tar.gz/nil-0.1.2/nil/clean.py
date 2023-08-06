#coding:utf-8

import os
import fnmatch

def all_file(root, patterns='*.pyc', ignore_dirs=[], \
        single_level=False, logger=None, no_matchs=False):
    """
    root:            需要遍历的目录
    patterns：       需要查找的文件，以, 为分割的字符串
    single_level:    是否只遍历单层目录，默认为否
    """
    patterns = tuple([p.strip() for p in patterns.split(',')])
    for path, subdirs, files in os.walk(root):
        if path.split('/')[-1] in ignore_dirs:
            continue
        for pattern in patterns:
            fs = fnmatch.filter(files, pattern)
            if not fs:
                if logger and no_matchs:
                    logger.debug('no match files in %s' % path)
                elif no_matchs:
                    print 'no match files in %s' % path
                continue
            for name in fs:
                yield os.path.join(path, name)
        if single_level:
            break

def clean(args, logger=None, no_matchs=False):
    filter = args.filter
    ignore_dirs = args.ignore_dirs or []
    path = args.path
    for f in all_file(path, filter, ignore_dirs, logger=logger, \
            no_matchs=no_matchs):
        if logger:
            logger.debug(f)
        else:
            print f
        continue
        try:
            os.remove(os.path.realpath(f))
        except:
            pass

def main():
    import gc
    import time
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Clean your files.')
    parser.add_argument('path', default='.', nargs='?',
                      help="clean path")
    parser.add_argument('--filter', default='*.pyc',
                      help="fliter which file split by ,")
    parser.add_argument('--ignore-dirs', default='',
                      help="ignore some dirs split by ,")
    args = parser.parse_args()
    gc.disable()
    clean(args)
    gc.enable()
