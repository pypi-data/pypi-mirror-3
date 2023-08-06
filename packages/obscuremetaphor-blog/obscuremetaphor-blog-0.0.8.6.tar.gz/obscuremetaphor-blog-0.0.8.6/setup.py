import os
from distutils.core import setup
from omblog import VERSION
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

core_packages = [
    'omblog',
]
for package in core_packages:
    for dirpath, dirnames, filenames in os.walk(package):
        # Ignore dirnames that start with '.'
        for i, dirname in enumerate(dirnames):
            if dirname.startswith('.'): del dirnames[i]
        if '__init__.py' in filenames:
            packages.append('.'.join(fullsplit(dirpath)))
        elif filenames:
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name="obscuremetaphor-blog",
    version=VERSION,
    license = 'BSD 3 Clause',
    description='A speedy django blog',
    author='Obscure Metaphor',
    author_email='hello@obscuremetaphor.co.uk',
    package_data = {
        'omblog' : [
            'templates/omblog/*.html',
            'static/omblog/css/*',
            'static/omblog/js/*',
            'static/omblog/img/*',
            'static/omblog/font/*',
        ]
    },
    packages=packages,
    data_files=data_files,
    install_requires = ['beautifulsoup4',
                        'django-picklefield',
                        'pygments',
                        'markdown']
)
