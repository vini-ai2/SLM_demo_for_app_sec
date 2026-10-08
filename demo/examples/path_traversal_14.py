# Path Traversal evaluation case 14
path = ROOT + "/" + requested
with open(path, 'rb') as stream:
    content = stream.read()
