from distutils.core import setup

setup(name='fog_client',
	  version='0.0.1',
	  author='Carles Gonzalez',
	  py_modules=['fog'],
	  requires=['cuisine', 'requests (>=0.13)'],
	  scripts=['fog.py'],
	  data_files=[('/etc/init', ['fog_client.conf'])]
	  )
