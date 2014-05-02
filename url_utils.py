def join(path1, path2):
    if path1[-1] == '/':
        path1 = path1[:-1]
    if path2[0] == '/':
        path2 = path2[1:]
    path = path1 + '/' + path2
    return path

