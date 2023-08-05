from distutils.core import setup
import infinitedict
setup(name='infinitedict',
    version=infinitedict.__version__,
    description='An infinitely and automatically nesting dictionary.',
    author='Chris Spencer',
    author_email='chrisspen@gmail.com',
    url='https://github.com/chrisspen/infinitedict',
    license='LGPL License',
    py_modules=['infinitedict'],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    platforms=['OS Independent'],)
