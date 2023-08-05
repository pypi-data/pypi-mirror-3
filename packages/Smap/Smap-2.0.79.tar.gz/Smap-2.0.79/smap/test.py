
import re
import timeit

split_pat = re.compile('/+')
def split_path(path):
    path = split_pat.split(path)
    return filter(lambda x: len(x), path)

def join_path(path):
    return '/' + '/'.join(path)

norm_path = lambda x: join_path(split_path(x))
norm_path2 = lambda x: split_pat.sub('/', x)
def norm_path3(x):
    x = x.replace('//', '/')
    x = x.replace('//', '/')
    x = x.replace('//', '/')
    return x
p = '/foo/bar/abz//foop'

print norm_path(p), norm_path2(p)

print timeit.timeit(lambda: norm_path(p))
print timeit.timeit(lambda: norm_path2('/foo/bar/abz//foop'))
print timeit.timeit(lambda: norm_path3('/foo/bar/abz//foop'))
