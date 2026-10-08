# Path Traversal evaluation case 9
path = ROOT + "/" + requested
with open(path, 'rb') as stream:
    content = stream.read()
