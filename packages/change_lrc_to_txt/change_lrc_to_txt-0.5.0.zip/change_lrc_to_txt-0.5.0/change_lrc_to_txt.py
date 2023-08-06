try:
	data = open('Track 3-01-02.lrc', 'r+')
	for each_line in data:
		try:
			(rubbish, content) = each_line.split(']', 1)
			print(content, end='', file=data)
		except ValueError:
			pass
	data.close()
except IOError:
	pass