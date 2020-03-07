# coding=utf-8

import os
import sys
import shutil
import py_compile
import argparse
import queue
import typing as T


parser = argparse.ArgumentParser()
parser.add_argument('--src', type=str, help='Directory of project', required=True)
parser.add_argument('--dst', type=str, help='Destination directory for bytecode', required=True)
parser.add_argument('--force', type=bool, help='Force action', default=False)
parser.add_argument('--ignore', type=str, help='Ignore files', default='.git,')
parser.add_argument('--verbose', type=bool, help='Print detail compilation', default=False)


def run():
    args = parser.parse_args()

    src_root = args.src
    dst_root = args.dst
    ignore = args.ignore
    verbose = args.verbose

    if not os.path.exists(src_root):
        sys.stderr.write('Source directory not exist')
        exit(-1)

    if os.path.exists(dst_root):
        if args.force:
            shutil.rmtree(dst_root, ignore_errors=True)
            os.mkdir(dst_root)
        else:
            sys.stderr.write('Destination directory existed')
            exit(-1)
    else:
        os.mkdir(dst_root)


    q = queue.Queue()
    q.put('.')
    while not q.empty():
        rel_path = q.get()
        curr_abs_path = os.path.join(src_root, rel_path)

        elems = list(filter(
            lambda fname: fname not in ignore.split(','),
            os.listdir(curr_abs_path)
        ))

        support_files = filter(
            lambda fname: os.path.splitext(fname)[1] != '.py' \
                          and os.path.isfile(os.path.join(curr_abs_path, fname)),
            elems
        )
        modules = filter(
            lambda fname: os.path.splitext(fname)[1] == '.py',
            elems
        )
        packages = filter(
            lambda fname: os.path.isdir(os.path.join(curr_abs_path, fname)) \
                          and fname is not '__pycache__',
            elems
        )

        # compile source files
        for module in modules:
            py_compile.compile(
                os.path.join(curr_abs_path, module)
            )

        # move to destination directory
        py_cache_dir = os.path.join(src_root, curr_abs_path, '__pycache__')
        if os.path.exists(py_cache_dir):
            if rel_path is '.':
                for fname in os.listdir(py_cache_dir):
                    shutil.move(
                        os.path.join(py_cache_dir, fname),
                        os.path.join(dst_root, rel_path)
                    )
                    sys.stdout.write(f'Compile {os.path.join(py_cache_dir, fname)} to {os.path.join(dst_root, rel_path)}\n')
            else:
                shutil.move(
                    py_cache_dir,
                    os.path.join(dst_root, rel_path)
                )
                sys.stdout.write(f'Compile {py_cache_dir} to {os.path.join(dst_root, rel_path)}\n')
            # remove mark version compiler in bytecode files
            for fname in os.listdir(os.path.join(dst_root, rel_path)):
                part_name = fname.split('.')
                if len(part_name) > 2:
                    del part_name[-2]
                    new_name = '.'.join(part_name)
                    os.rename(
                        os.path.join(dst_root, rel_path, fname),
                        os.path.join(dst_root, rel_path, new_name)
                    )

        # copy supporting files
        for fname in support_files:
            if not os.path.exists(os.path.join(dst_root, rel_path)):
                os.makedirs(os.path.join(dst_root, rel_path))
            shutil.copyfile(
                os.path.join(src_root, rel_path, fname),
                os.path.join(dst_root, rel_path, fname)
            )
            sys.stdout.write(f'Copy {os.path.join(src_root, rel_path, fname)} to {dst_root, rel_path, fname}\n')

        for package in packages:
            q.put(os.path.join(rel_path, package))


__version__ = '1.0.0.dev'
