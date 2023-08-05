import ctypes

for lib in ('libpq.so.5', 'libpq.so'):
    try:
        c = ctypes.CDLL(lib)
    except OSError:
        continue
    break
else:
    raise OSError('Cannot load libpq.so')
