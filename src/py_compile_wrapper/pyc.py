# coding=utf-8

import os
import sys
import shutil
import queue
import py_compile


def get_ext(fpath):
    """Get extension from full path of file"""
    return os.path.splitext(fpath)[1]

def get_fname(fpath):
    """Get filename in path"""
    return os.path.basename(fpath)


class CompileWrapper:   # pylint: disable=C0111
    def __init__(self, src_dir, dst_dir, ignore_files=['__pycache__', '.git'],  # pylint: disable=R0913,W1113,W0102
                 ignore_exts=[], force=True):
        self._src_dir = src_dir
        self._dst_dir = dst_dir
        self._ignore_files = ignore_files
        self._ignore_exts = ignore_exts
        self._force = force

    def checking(self):
        """ Checking filesystem """
        if not os.path.isdir(self._src_dir):
            sys.stderr.write('Source dir error')
            exit(-1)
        if os.path.isdir(self._dst_dir):
            if self._force:
                shutil.rmtree(self._dst_dir)
                os.makedirs(self._dst_dir)
            else:
                sys.stderr.write('Dest dir existed')
                exit(-1)

    def _ignore_file_filter(self, fpaths):
        return list(filter(
            lambda fpath: get_ext(fpath) not in self._ignore_exts and \
                          get_fname(fpath) not in self._ignore_files,
            fpaths
        ))

    def _supporting_file_filter(self, fpaths, context):
        return filter(
            lambda fpath: get_ext(fpath) not in ('.py',) and \
                          os.path.isfile(os.path.join(self._src_dir, context, fpath)),
            fpaths
        )

    @staticmethod
    def _source_file_filter(fpaths):
        return filter(
            lambda fpath: get_ext(fpath) in ('.py',),
            fpaths
        )

    def _package_filter(self, fpaths, context):
        return filter(
            lambda fpath: os.path.isdir(os.path.join(
                self._src_dir,
                context, fpath
            )),
            fpaths
        )

    def _move_file(self, src, dst, context):
        abs_src = os.path.join(self._src_dir, context, src)
        abs_dir_dst = os.path.join(self._dst_dir, context)
        if not os.path.isdir(abs_dir_dst):
            os.makedirs(abs_dir_dst)
        shutil.copy(
            abs_src,
            os.path.join(abs_dir_dst, dst)
        )

    @staticmethod
    def _remove_compiler_name(fname: str) -> str:
        subs = fname.split('.')
        del subs[-2]
        return '.'.join(subs)

    def _move_py_cache(self, context):
        py_cache_dir = os.path.join(self._src_dir, context, '__pycache__')
        if os.path.isdir(py_cache_dir):
            dst_dir = os.path.join(self._dst_dir, context)
            if not os.path.isdir(dst_dir):
                os.makedirs(dst_dir)
            bytecode_files = os.listdir(py_cache_dir)
            for fname in bytecode_files:
                shutil.move(
                    os.path.join(py_cache_dir, fname),
                    os.path.join(dst_dir, self._remove_compiler_name(fname))
                )

    def compile(self, verbose=True):
        """Recursive compile source code to bytecode"""
        q = queue.Queue() # pylint: disable=C0103
        q.put('')
        while not q.empty():
            context = q.get()
            candidates = self._ignore_file_filter(os.listdir(
                os.path.join(self._src_dir, context)
            ))

            # process supportting file
            for fname in self._supporting_file_filter(candidates, context):
                try:
                    self._move_file(fname, fname, context)
                except EnvironmentError:
                    sys.stderr.write(f'Error copy {os.path.join(context, fname)}\n')
                else:
                    if verbose:
                        sys.stdout.write(f'Copy file {os.path.join(context, fname)}\n')

            # process source file
            for fname in self._source_file_filter(candidates):
                try:
                    py_compile.compile(os.path.join(self._src_dir, context, fname))
                except py_compile.PyCompileError:
                    sys.stderr.write(f'Compile error {os.path.join(context, fname)}\n')
                else:
                    if verbose:
                        sys.stdout.write(f'Compile file {os.path.join(context, fname)}\n')
                try:
                    self._move_py_cache(context)
                except EnvironmentError:
                    if verbose:
                        sys.stdout.write(f'Copy output fail {context}\n')

            # process package dir
            for pkg in self._package_filter(candidates, context):
                q.put(os.path.join(context, pkg))
