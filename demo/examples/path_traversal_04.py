# Path Traversal evaluation case 4
path = ROOT + "/" + requested
with open(path, 'rb') as stream:
    content = stream.read()
