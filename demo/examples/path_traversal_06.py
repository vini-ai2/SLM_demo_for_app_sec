# Path Traversal evaluation case 6
path = os.path.join(ROOT, filename)
with open(path, 'rb') as stream:
    content = stream.read()
