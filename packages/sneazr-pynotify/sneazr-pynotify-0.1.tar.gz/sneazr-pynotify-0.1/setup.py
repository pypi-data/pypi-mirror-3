from setuptools import setup, find_packages

setup(
    name='sneazr-pynotify',
    version = '0.1',
    py_modules=['sneaze_pynotify'],
    author = 'Teodor Pripoae',
    author_email = 'toni@netbaiji.com',
    description = 'Have nosetests notify to pynotify(fork of sneazr)',
    keywords = 'nose tests pynotify',
    url = 'http://github.com/teodor-pripoae/sneazr-pynotify',
    setup_requires=['setuptools-git'],
    tests_require=['nose'],
    install_requires=[
        'nose',
    ],
    packages=find_packages(),
    include_package_data=True,
    entry_points = {
        'nose.plugins.0.10': ['sneazr-pynotify = sneaze_pynotify:SneazrPyNotify']
    }
)
