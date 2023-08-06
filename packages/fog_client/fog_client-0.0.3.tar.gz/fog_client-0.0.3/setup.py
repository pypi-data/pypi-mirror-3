from distutils.core import setup

setup(name='fog_client',
	  version='0.0.3',
	  author='Carles Gonzalez',
	  py_modules=['fog_lib', 'cuisine'],
	  requires=['cuisine', 'requests (>=0.13)'],
	  scripts=['fog_client.py'],
	  data_files=[('/etc/init', ['fog_client.conf'])]
	  )
