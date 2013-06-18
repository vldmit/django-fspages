# -*- coding: utf-8 -*-
import posixpath

def find_paths(path, storage, language=None):
    """
    Recursively traverse the storage and return all paths for given language
    """
    if language is not None:
        fullpath = posixpath.join(language, path)
    else:
        fullpath = path
    dirs, files = storage.listdir(fullpath)
    for f in files:
        yield posixpath.join(path, f)
    for d in dirs:
        innerpath = posixpath.join(path, d)
        for p in find_paths(innerpath, storage, language=language):
            yield p
