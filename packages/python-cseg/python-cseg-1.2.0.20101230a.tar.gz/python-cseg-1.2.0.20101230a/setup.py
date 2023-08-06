from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

scws_files = [
		'charset.c', 
		'crc32.c', 
		'darray.c', 
		'lock.c',
		'pool.c',
		'rule.c',
		'scws.c',
		'xdb.c',
		'xdict.c',
		'xtree.c'
		]

sourcefiles = ['cseg.pyx']
sourcefiles.extend(['contrib/%s' % i for i in scws_files])

cseg_module = Extension(
		'cseg',
		include_dirs = ['contrib'],
		library_dirs = [],
		libraries = [],
		sources = sourcefiles
		)

setup(
		name = 'python-cseg',
		version = '1.2.0.20101230a',
		description = 'Python binding to Simple Chinese Word Segmentation (SCWS)',
		author = 'Chris Chou',
		author_email = 'm2chrischou@gmail.com',
		url = 'https://bitbucket.org/mongmong/python-cseg',
    	cmdclass = {'build_ext': build_ext},
    	ext_modules = [cseg_module],
		classifiers = [
			'Programming Language :: Python',
			'Programming Language :: C',
			'Development Status :: 3 - Alpha',
			'Natural Language :: Chinese (Simplified)',
			'Natural Language :: Chinese (Traditional)',
			'Topic :: Text Processing :: Linguistic'
			],
		data_files = [
			('/opt/etc/python-cseg', [
				'data/dict.xdb', 
				'data/dict.utf8.xdb',
				'data/dict_cht.utf8.xdb',
				'data/rules.ini',
				'data/rules.utf8.ini',
				'data/rules_cht.utf8.ini'
				])
			]
)

