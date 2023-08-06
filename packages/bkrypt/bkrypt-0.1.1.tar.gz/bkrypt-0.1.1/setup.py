"""
bkrypt: Easy Password wrapper around BCrypt.
"""
import os
from setuptools import setup


def get_version():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'bkrypt/version.py')) as f:
        VERSION = None
        exec(f.read())
        return VERSION
    raise RuntimeError('No version info found.')


setup(
    name='bkrypt',
    version=get_version(),
    url='https://github.com/nvie/bkrypt',
    license='BSD',
    author='Vincent Driessen',
    author_email='vincent@3rdcloud.com',
    description='bkrypt: Easy Password wrapper around BCrypt.',
    long_description=__doc__,
    packages=['bkrypt'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=['py-bcrypt'],
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        #'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Other Environment',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Security :: Cryptography',
        'Topic :: Utilities',
    ]
)
