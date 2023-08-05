from distutils.core import setup
import toolkit_library

setup(
    name = toolkit_library.__name__,
    version = toolkit_library.__version__,
    url = 'http://stackoverflow.com/users/862862/tyler-long',
    license = 'BSD',
    author = toolkit_library.__author__,
    author_email = 'tyler4long@gmail.com',
    description = 'Toolkit Library, full of useful toolkits',
    long_description = open('README').read(),
    packages = ['toolkit_library', ],
    platforms = 'any',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
