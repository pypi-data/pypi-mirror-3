def parse(ipt):
	mode = 0
	headers = []
	curr = None
	results = []
	length = 0
	
	def sh(sn, qn, l):
		return {
			'subject': {
				'name':  sn,
				'start': None,
				'end':   None,
				'sequence': ''
			},
			'query': {
				'name':  qn.split()[0],
				'start': None,
				'end':   None,
				'sequence': ''
			},
			'length':  l
		}

	def ra(sh):
		for res in ('subject', 'query'):
			sh[res]['start']  = int(sh[res]['start'])
			sh[res]['end']    = int(sh[res]['end'])
			sh[res]['length'] = abs(sh[res]['end'] - \
			                    sh[res]['start'] + 1)
		results.append(sh)
	
	for line in ipt:
		line = line.strip()
		if not line:
			if mode == 4:
				mode = 5
			continue

		if mode == 0:
			if line[:6] == 'Query=':
				mode  = 1
				qname = line[6:].strip()
				#self.headers = headers
			else:
				headers.append(line)
	
		elif mode == 1:
			if line[0] == '>':	
				mode = 3
				subheaders = sh(line[1:], qname, length)
			elif line[:6] == 'Length' or \
					(line[0] == '(' and line.endswith('letters)')):
				if line[:7] == 'Length=':
					length = int(''.join(line[7:].strip().split(',')))
				else:
					length = int(''.join(line[1:-8].strip().split(',')))
				mode  = 2
			elif line[:6] == 'Query=':
				qname = line[6:].strip()
			else:
				qname += line
	
		elif mode == 2:
			if line[0] == '>':
				mode = 3
				subheaders = sh(line[1:], qname, length)
			elif line[:6] == 'Query=':
				qname = line[6:].strip()
				mode = 1

		elif mode == 3:
			if line[:5] == 'Score':
				subheaders['subject']['name'] = subheaders['subject']['name'].split()[0]
				for pairs in (a.strip() for a in line.split(',')):
					l, r = tuple(a.strip() for a in pairs.split('=')[:2])
					subheaders[l.lower()] = r
				mode = 4
			else:
				subheaders['subject']['name'] += line
	
		elif mode == 4:
			for pairs in (a.strip() for a in line.split(',')):
				l, r = tuple(a.strip() for a in pairs.split('=')[:2])
				subheaders[l.lower()] = r
	
		elif mode == 5:
			if   line[:6] == 'Query=':
				mode  = 1
				qname = line[6:].strip().split()[0]
				ra(subheaders)
				continue
			elif line[0] == '>':
				ra(subheaders)
				subheaders = sh(line[1:], qname, length)
				mode = 3
				continue
			elif line[:5] == 'Score':
				ra(subheaders)
				subheaders = sh(subheaders['subject']['name'], qname, length)
				for pairs in (a.strip() for a in line.split(',')):
					l, r = tuple(a.strip() for a in pairs.split('=')[:2])
					subheaders[l.lower()] = r
				mode = 4
				continue
			elif line[:5] == 'Sbjct': curr = 'subject'
			elif line[:5] == 'Query': curr = 'query'
			else: continue
	
			_, start, seq, end = line.split()
			subheaders[curr]['start']     = subheaders[curr]['start'] or start
			subheaders[curr]['end']       = end
			subheaders[curr]['sequence'] += ''.join(seq.split('-')).upper()

	ra(subheaders)

	return results
