
def get_object_prim_path(obj):
    tree = [obj]
    while obj.parent:
        obj = obj.parent
        tree.append(obj)

    return "/"+"/".join(map(lambda x: x.name.split(".")[0], tree[::-1]))


def get_object_root(obj):
    while obj.parent:
        obj = obj.parent
    return obj