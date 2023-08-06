from distutils.core import setup

setup(name = 'ISIpy',
	  version = '1.0.1',
	  py_modules=['ISI','interspike_interval','simulate_data','demo'],
	  author='Michael Chary', 
	  author_email='michael.chary@mssm.edu',
	  url='http://camelot.mssm.edu/~mac389/personal/code.html',
	  data_files = [('/',['simulated.mat'])],
	  description='Implementation in Python of the pairwise interspike interval distance described in Kreuz et al. (2007)',
	  maintainer='Michael Chary',
	  maintainer_email='michael.chary@mssm.edu',
	  license= 'GNU General Public License 3'
	  )