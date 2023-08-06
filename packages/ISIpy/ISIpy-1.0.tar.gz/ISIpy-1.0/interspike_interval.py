class interspike_interval(object):
	def __init__(self, start, stop, interspike_interval):
		self.start = start
		self.stop = stop
		self.interspike_interval = interspike_interval
	
	def display(self):
		print '-----------------------------'
		print 'Interval starts at',self.start,'lasts for',self.interspike_interval,'and ends at',self.stop
		print '-----------------------------'