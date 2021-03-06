from pyp2rpm import settings
from pyp2rpm import name_convertor

def name_for_python_version(name, version):
    return name_convertor.NameConvertor.rpm_versioned_name(name, version)

def script_name_for_python_version(name, version):
    if version == settings.DEFAULT_PYTHON_VERSION:
        return name
    else:
        return 'python{0}-{1}'.format(version, name)

def sitedir_for_python_version(name, version):
    if version == settings.DEFAULT_PYTHON_VERSION:
        return name
    else:
        return name.replace('python', 'python{0}'.format(version))

def python_bin_for_python_version(name, version):
    if version == settings.DEFAULT_PYTHON_VERSION:
        return name
    else:
        return name.replace('__python', '__python3')

def macroed_pkg_name(name):
    if name.startswith('python-'):
        return 'python-%{pypi_name}'
    else:
        return '%{pypi_name}'

def module_to_path(name, module):
    module = module.replace(".", "/")
    if name == module:
        return "%{pypi_name}"
    else:
        return module

__all__ = [name_for_python_version,
           script_name_for_python_version,
           sitedir_for_python_version,
           python_bin_for_python_version,
           macroed_pkg_name,
           module_to_path]
