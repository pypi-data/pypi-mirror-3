try:  # setuptools
    from pkg_resources import declare_namespace
    declare_namespace(__name__)
except:  # distutils
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
