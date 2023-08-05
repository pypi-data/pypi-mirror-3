from distutils.core import setup
import quick_framework

setup(
    name = quick_framework.__name__,
    version = quick_framework.__version__,
    url = 'http://stackoverflow.com/users/862862/tyler-long',
    license = 'BSD',
    author = quick_framework.__author__,
    author_email = 'tyler4long@gmail.com',
    description = """A Python web framework which enable you to develop a web site in minutes""",
    long_description = open('README').read(),
    packages = ['quick_framework', ],
    install_requires = open('REQUIREMENTS').read().splitlines(),
    platforms = 'any',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
