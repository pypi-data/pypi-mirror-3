VERSION = (1, 0, 2)

def get_version():
    return ".".join(map(lambda x: str(x), VERSION))
