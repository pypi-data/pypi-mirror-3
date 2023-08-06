# $Id: queues.py,v 1.6 2012/07/09 11:30:55 irees Exp $
"""EMEN2 process and message queues
"""

import time
import random
import subprocess
import threading
import Queue


try:
	import multiprocessing
	CPU_COUNT = multiprocessing.cpu_count()
except:
	CPU_COUNT = 1



##### Subprocess queues #####

# threading.Thread style
class ProcessWorker(object):
	def __init__(self, queue):
		self.queue = queue

	def run(self):
		while True:
			priority, name, task = self.queue.get()
			if task is None:
				self.queue.add_task(None)
				return
			print "ProcessWorker:", task
			a = subprocess.Popen(task)
			returncode = a.wait()
			self.queue.task_done()
			
			

class ProcessQueue(Queue.LifoQueue):
	"""A queue of processes to run."""
	worker = ProcessWorker
	
	def add_task(self, task, priority=0, name=None):
		"""Add a task to the queue. Highest priority is 0, lowest priority is 1000. Default is 100."""
		if task:
			task = tuple(task)

		if priority < -100 or priority > 100:
			raise ValueError, "Highest priority is -100, lowest priority is 100"

		if name in [i[1] for i in self.queue]:
			raise ValueError, "Task name already in queue: %s"%name

		print "ProcessQueue: Adding task %s with priority %s to queue: %s"%(name, priority, task)
		return self.put((priority, name, task))

	def end(self):
		"""Allow all queued jobs to complete, then exit."""
		return self.put((101, None))

	def stop(self):
		"""Allow running jobs to complete, then exit."""
		return self.put((-101, None))

	def start(self, processes=1):
		for i in range(processes):
			worker = self.worker(self)
			t = threading.Thread(target=worker.run)
			t.daemon = True
			t.start()
			

processqueue = ProcessQueue()
processqueue.start(processes=CPU_COUNT)


if __name__ == "__main__":
	pq = ProcessQueue()
	for i in range(20):
		pq.add_task(['touch', '%s.txt'%i])
	pq.start()
	pq.join()
	# pq.end()


__version__ = "$Revision: 1.6 $".split(":")[1][:-1].strip()