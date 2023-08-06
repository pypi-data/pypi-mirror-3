from distutils.core import setup

setup(
    name='plastclient',
    version='0.1.1dev',
    license='FreeBSD',
    packages=['plastclient',],
    author='Asbjorn Enge',
    author_email='asbjorn@smartm.no',
    url='http://www.smartm.no',
    description='.',
    long_description=open('README.rst').read(),
    install_requires=[
        "oauth2",
    ],
)
