import importlib


def resolver_loader(classpath):
    # 将全路径类名切割获得类名及类路径
    ret, cls_name = classpath.rsplit(".", maxsplit=1)
    # 导入文件模块
    m = importlib.import_module(ret)
    # 通过getattr()获取模块内容，获取类名
    m_class = getattr(m, cls_name)
    obj = m_class()
    return obj