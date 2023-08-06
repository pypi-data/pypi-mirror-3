from distutils.core import setup

setup(name='fog_client',
	  version='0.0.2',
	  author='Carles Gonzalez',
	  py_modules=['fog', 'cuisine'],
	  requires=['cuisine', 'requests (>=0.13)'],
	  scripts=['fog.py'],
	  data_files=[('/etc/init', ['fog_client.conf'])]
	  )
