#!/opt/local/bin/python2.7

import biotools.analysis.predict as genepredict
import biotools.analysis.options as options
import threading, sys, os
import Queue as queue

def _run_genepredict(q, infile):
	'''_run_genepredict(queue, infile, args)
This is the target function for threading.Threads to run several
instances of genepredict.run at once. For simplicity of use, we import
genepredict and use it like any other module. However, the GIL slows
the gene prediction down quite a bit if we do this, so if you are so
inclined, you can import subprocess and call the module that way to
speed things up a bit.

This function should not be used on its own.'''

	while 1:
		try: strainf = q.get(False)
		except: break
		strain = strainf.split(os.sep)[-1]
		pos = strain.rfind('.')
		if pos > 1 or (pos == 1 and strain[0] != '.'):
			strain = strain[:pos]

		try: genepredict.run(*[infile, strainf, strain])
		except RuntimeError: pass
		q.task_done()

def run():
	'''run(args)
Run several instances of genepredict.run at once.'''
	args = options.args
	if len(args) < 2:
		options.help()
		raise RuntimeError
	else:
		infile	= args[0]
		strains = args[1:]

		q = queue.Queue()
		for strain in strains:
			q.put(strain)

		for i in range(options.NUM_PROCESSES-1):
			curr = threading.Thread(target=_run_genepredict, args=(q, infile))
			curr.start()

		_run_genepredict(q, infile)
		q.join()

	return (infile, [s.split(os.sep)[-1].split('.')[0] for s in strains])

if __name__ == "__main__":
	import sys
	try: run(sys.argv[1:])
	except: pass
