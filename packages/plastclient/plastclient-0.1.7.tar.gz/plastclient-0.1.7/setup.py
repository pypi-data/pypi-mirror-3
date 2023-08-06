from distutils.core import setup

setup(
    name='plastclient',
    version='0.1.7',
    license='FreeBSD',
    packages=['plastclient',],
    author='Asbjorn Enge',
    author_email='asbjorn@smartm.no',
    url='http://www.smartm.no',
    description='Plastclient is an API wrapper for Plast.',
    long_description=open('README.txt').read(),
    install_requires=[
        "oauth2",
    ],
)
