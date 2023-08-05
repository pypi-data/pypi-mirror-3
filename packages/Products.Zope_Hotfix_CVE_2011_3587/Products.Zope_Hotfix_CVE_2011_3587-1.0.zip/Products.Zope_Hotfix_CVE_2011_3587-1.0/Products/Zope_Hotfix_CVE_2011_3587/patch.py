from types import ModuleType


def install_patch():
    from OFS.misc_ import p_

    for k, v in list(p_.__dict__.items()):
        if isinstance(v, ModuleType):
            del p_.__dict__[k]
