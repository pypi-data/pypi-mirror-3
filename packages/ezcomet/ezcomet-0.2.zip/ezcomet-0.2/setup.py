from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(
    name='ezcomet',
    version='0.2',
    license='MIT',
    author='EZComet.com',
    author_email='bornstub@gmail.com',
    description='The Python API of EZComet.com Ajax/Comet service',
    url='http://ezcomet.com/tools/python_sdk',
    zip_safe=False,
    include_package_data=True,
    packages=['ezcomet'],
    install_requires=[
        'httplib2',
    ],
    entry_points = """\
    [console_scripts]
    ezcomet_write = ezcomet:main
    """
)
