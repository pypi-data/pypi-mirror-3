#coding:utf-8

import os
import fnmatch

def all_file(root, patterns='*.pyc', ignore_dirs={}, \
        single_level=False, logger=None, no_matchs=False):
    """
    root:            需要遍历的目录
    patterns：       需要查找的文件，以, 为分割的字符串
    single_level:    是否只遍历单层目录，默认为否
    """
    patterns = tuple([p.strip() for p in patterns.split(',')])
    ignore_dir = ''
    for path, subdirs, files in os.walk(root):
        if ignore_dir and path.startswith(ignore_dir):
            log('ignore subdir %s' % path, logger)
            continue
        if ignore_dirs.get(os.path.basename(path), None):
            log('ignore dir %s' % path, logger)
            ignore_dir = path
            continue
        for pattern in patterns:
            fs = fnmatch.filter(files, pattern)
            if not fs:
                if no_matchs: log('no match files in %s' % path, logger)
                continue
            for name in fs:
                yield os.path.join(path, name)
        if single_level:
            break

def log(msg, logger=None):
    if logger:
        logger.debug(msg)
    else:
        print msg

def clean(args, logger=None, no_matchs=False):
    filter = args.filter
    if args.ignore_dirs:
        ignore_dirs = dict([(d.strip(), 1) for d in args.ignore_dirs.split(',') if d])
    path = args.path
    for f in all_file(path, filter, ignore_dirs, logger=logger, \
            no_matchs=no_matchs):
        log(f, logger)
        try:
            os.remove(os.path.realpath(f))
        except Exception, e:
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
