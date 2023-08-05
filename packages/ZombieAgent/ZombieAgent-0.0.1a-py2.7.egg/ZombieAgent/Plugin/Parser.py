def shellquote(s):
	return "'" + s.replace("'", "'\\''") + "'"

def parse_cli_params(params):
	params_out = {}
	
	for pair in params:
		pair = _escape_split('=', pair)
		
		key = pair[0]
		value = True
		
		if len(pair) == 2:
			value = pair[1]
		
		params_out[key] = value
	
	return params_out

def _escape_split(sep, argstr):
	"""
	Allows for escaping of the separator: e.g. task:arg='foo\, bar'
	
	It should be noted that the way bash et. al. do command line parsing, those
	single quotes are required.
	"""
	escaped_sep = r'\%s' % sep
	
	if escaped_sep not in argstr:
		return argstr.split(sep)
	
	before, _, after = argstr.partition(escaped_sep)
	startlist = before.split(sep)  # a regular split is fine here
	unfinished = startlist[-1]
	startlist = startlist[:-1]
	
	# recurse because there may be more escaped separators
	endlist = _escape_split(sep, after)
	
	# finish building the escaped value. we use endlist[0] becaue the first
	# part of the string sent in recursion is the rest of the escaped value.
	unfinished += sep + endlist[0]
	
	return startlist + [unfinished] + endlist[1:]  # put together all the parts