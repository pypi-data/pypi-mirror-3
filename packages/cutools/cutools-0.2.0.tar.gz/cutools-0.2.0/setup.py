from setuptools import setup, find_packages
from cutools import VERSION

def readfile(rfile):
    try:
        with open(rfile, 'r') as f:
            return f.read()
    except:
        return ''

setup(
    name='cutools',
    version='0.2.0',
    description='Check local modifications in upstream branch',
    long_description=readfile('README.rst') + '\n' + readfile('CHANGES'),
    author='Eduard Carreras',
    author_email='ecarreras@gmail.com',
    url='https://github.com/ecarreras/cutools',
    license=readfile('LICENSE'),
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    platforms=['Any'],
    scripts=[],
    entry_points={
        'console_scripts': [
            'cugit = cutools.cli.cugit:app.cmdline'
        ]
    },
    provides=['cutools'],
    install_requires=['clint', 'plumbum', 'subcmd'],
)
