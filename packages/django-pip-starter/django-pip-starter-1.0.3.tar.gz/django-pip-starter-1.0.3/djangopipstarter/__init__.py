VERSION = (1, 0, 3)

def get_version():
    return ".".join(map(lambda x: str(x), VERSION))
