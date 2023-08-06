# tail-call-optimizer

"""

#
#    Copyright (C) 2012  Moritz MOlle
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# the betterrerer version
# Version 0.20120223
#
# no tailcall-marker needed anymore. this finds the tailcall in the bytecode by itself
# (in this example only CALL_FUNCTION, but this can easily extended to
# CALL_FUNCTION_KW, CALL_FUNCTION_VAR and CALL_FUNCTION_KW_VAR
#
# written by mokrates
# http://sourceforge.net/users/mokrates

"""

import dis
import new

def tailopt(f):
	"""
Usage:
@tailopt
def myfun(...):
	...

Description:
Analyses the compiled code of myfun and optimizes tailcalls within
"""
	def modify_assembler(codestring):
		codelist = [ord(c) for c in codestring]
		
		# filter CALL_FUNCTION
		for i in xrange(0,len(codelist)-4):
			if (codelist[i] == dis.opmap['CALL_FUNCTION'] and
				codelist[i+3] == dis.opmap['RETURN_VALUE'] ):
				codelist[i] = dis.opmap['BUILD_TUPLE']
				codelist[i+1] = codelist[i+1] + 1
				
		return reduce(str.__add__, ( chr(x) for x in codelist ))
	
	def recreate_modified_func(func):
	
		f=func.func_code
	
		codestring=modify_assembler(f.co_code)
	
		code = new.code(f.co_argcount, f.co_nlocals, f.co_stacksize, f.co_flags, codestring, 
			f.co_consts, f.co_names,
	        	f.co_varnames, f.co_filename, f.co_name, f.co_firstlineno, f.co_lnotab)
	
		newfunc = new.function(code, func.func_globals, func.func_name, func.func_defaults, func.func_closure)
	
		return newfunc
	
	
	def taildecor(*args, **kwargs):
		res = mod_f(*args, **kwargs)
		while (isinstance(res, tuple) and 
		    len(res) > 0 and
		    callable(res[0])):
		    
		    if ('_taildecor_mod_f' in dir(res[0])):
		    	res = res[0]._taildecor_mod_f(*res[1:])
		    else:
		    	return res[0](*res[1:])

		return res

	mod_f = recreate_modified_func(f)
	taildecor._taildecor_mod_f = mod_f
	return taildecor

if __name__ == '__main__':
	
	# example
	
	@tailopt
	def fak(still, acc=1):
		if (still==1): return str(acc)
		else: return fak(still-1, acc * still)
	
	print fak(10000)
