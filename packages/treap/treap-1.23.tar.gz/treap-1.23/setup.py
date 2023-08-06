
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

version = '1.23'

setup(
    name='treap',
    py_modules=[ 
		'treap', 'duptreap', 
		'py_treap', 'py_duptreap', 
		'pyx_treap', 'pyx_duptreap', 
		'py_treap_node', 'py_duptreap_node', 
		'nest',
		],
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
	 	Extension("pyx_treap_node", ["pyx_treap_node.c"]), 
		Extension("pyx_duptreap_node", ["pyx_duptreap_node.c"]),
		],
    version=version,
    description='Python implementation of treaps',
    long_description='''
A set of python modules implementing treaps is provided.

Treaps perform most operations in O(log2n) time, and are innately sorted.
They're very nice for keeping a collection of values that needs to
always be sorted, or for optimization problems in which you need to find
the p best values out of q, when p is much smaller than q.

Modules are provided for both treaps that enforce uniqueness, and treaps that allow duplicates.

Pure python versions are included, as are Cython-enhanced versions for performance.

Release 1.22 is pylint'd and is known to run on at least CPython 2, CPython 3 and Pypy 1.4.1.
''',
	author='Daniel Richard Stromberg',
	author_email='strombrg@gmail.com',
	url='http://stromberg.dnsalias.org/~dstromberg/treap/',
	platforms='Cross platform',
	license='Apache v2',
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Programming Language :: Cython",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 3",
		],
	)

