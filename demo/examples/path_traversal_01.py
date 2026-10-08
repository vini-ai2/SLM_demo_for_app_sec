# Path Traversal evaluation case 1
path = os.path.join(ROOT, filename)
with open(path, 'rb') as stream:
    content = stream.read()
