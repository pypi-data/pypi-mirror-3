###################################################################################
#
#            Ad Hoc Unification Procedure
#
###################################################################################
#
import synt, pattern

bvarnum = 0
subst = {}
shadow = {}
schematch = {}
givenvars= []
groundlist = []

def shadow_extend(var, image):
	global shadow
# Given R a transitive, strictly anti-symmetric relation and
# S a relation whose domain is a singleton we form the
# transitive closure of (R \cup S), if this is strictly anti-symmetric
# and return 0 otherwise.  
	if var not in shadow:
		shadow[var] = [[var]]
	for y in shadow[var][0]:
		if y in image:
			return 0
	new_image = []
	for x in shadow:
		if x in image:
			for y in shadow[x][1:]:
				if y == var:
					return 0
				if y not in image and y not in new_image and y not in shadow[var]:
					new_image.append(y)
	image.extend(new_image)
	for x in shadow:
		if var in shadow[x]:
			for y in image:
				if y in shadow[x][0]:
					return 0
				if y not in shadow[x]:
					shadow[x].append(y)
	for y in image:
		if y not in shadow[var]:
			shadow[var].append(y)

def main_unifier(forms, instances, givens,debug=False):
# Variables and schemators except those in givenvars
# are matched.  If no match is found 0 is returned.
# 
# subst gives irreversible substitutions 
# 
# shadow records each match as well as other 
# variables and schemators which occur in 
# irreversible substitutions.  Each value is
# a list:
# [ [eqvar1, eqvar2, eqvar3 ...], subvar1, subvar2...]
# The values of both subst and shadow are exactly the
# same for all of eqvar1, eqvar2 ...
#   
	global bvarnum,subst,schematch,shadow,givenvars,groundedvars
	bvarnum = 0
	subst = {}
	schematch = {}
	shadow = {}
	givenvars = givens
	groundedvars = givenvars[:]

	schemcond = {}
	forms = forms[:]
	instances = instances[:]
	usedflags = 0
	while forms or schematch:
		rang = range(len(forms))
		groundedvars = newgroundlist()
		j = -1

		if debug:
			print "Top"
			print "givenvars =",givenvars
			print "Forms and Instances at top"
			for t in range(len(forms)):
				print t,
				synt.pprint(forms[t])
				print t,
				synt.pprint(instances[t])
			print "Subst at top "
			for t in subst:
				print t,':'
				synt.pprint(subst[t])
			print "Schematch ="
			for t in schematch:
				print t,':'
				synt.pprint(schematch[t])
			print "schemcond = ", schemcond
			print "shadow ="
			for t in shadow:
				print t,':'
				synt.pprint(shadow[t])
#

		for i in rang: # Equals Do Match 
			if forms[i] == instances[i]:
				j = i
				break
		if j != -1:
			del forms[j]
			del instances[j]
			continue


		for i in rang: # Bound Variables must match
			if type(forms[i]) is str and pattern.bvar.match(forms[i]):
				if type(instances[i]) is not list:
					return 0
				if instances[i][0][0] != 42:
					return 0
				if instances[i][1] in givenvars:
					return 0
			if type(instances[i]) is str and pattern.bvar.match(instances[i]):
				if type(forms[i]) is not list:
					return 0
				if forms[i][0][0] != 42:
					return 0
				if forms[i][1] in givenvars:
					return 0

		for i in rang: # Given Variable or Constant Must Match
			if(forms[i] in givenvars or (type(forms[i])is str  \
           and synt.symtype(forms[i]) not in [10,11])):
				if type(instances[i]) is str :
					if synt.symtype(instances[i]) not in [10,11]:
						return 0
					if instances[i] in givenvars:
						return 0
				elif type(instances[i]) is list :
					if instances[i][0][0] not in [42,43]:
						return 0
					if instances[i][1] in givenvars:
						return 0

		for i in rang: # Given Variable or Constant Must Match
			if(instances[i] in givenvars or 
            (type(instances[i])is str  \
              and synt.symtype(instances[i]) not in [10,11])):
				if type(forms[i]) is str :
					if synt.symtype(forms[i]) not in [10,11]:
						return 0
					if forms[i] in givenvars:
						return 0
				elif type(forms[i]) is list :
					if forms[i][0][0] not in [42,43]:
						return 0
					if forms[i][1] in givenvars:
						return 0

		for i in rang: # Match Given Schematic Expressions 
			if type(forms[i]) == type(instances[i]) is list :
				if forms[i][0][0] in [42,43] and instances[i][0][0] in [42,43]:
					if forms[i][1]in givenvars and instances[i][1] in givenvars: 
						if instances[i][1] == forms[i][1]:
							j = i
							break
						else:
							return 0
				elif forms[i][0][0] in [42,43]:
					if forms[i][1] in givenvars:
						return 0
				elif instances[i][0][0] in [42,43]:
					if instances[i][1] in givenvars:
						return 0
		if j != -1:
			forms.extend(forms[j][2:])
			instances.extend(instances[j][2:])
			del forms[j]
			del instances[j]
			continue

		for i in rang: # Match Basic Forms (non-commutative)
			if type(forms[i]) == type(instances[i]) is list :
				if forms[i][0][0] in [42,43] or instances[i][0][0] in [42,43]:
					pass
				elif '' != synt.cmop(forms[i]) == synt.cmop(instances[i]):
					pass
				elif synt.cmop(forms[i]) or synt.cmop(instances[i]):
					return 0
				elif len(forms[i]) != len(instances[i]):
					return 0
				elif forms[i][0] != instances[i][0]:
					return 0
				else:
					j = i
					break
		if j != -1:
			fbvlist = synt.indvlist(forms[j])
			ibvlist = synt.indvlist(instances[j])
#			print "fbvlist ", forms[j],  " = ", fbvlist
#			print "ibvlist ", instances[j], " = ", ibvlist
			if len(fbvlist) != len(ibvlist):
				return 0
			nlist = newbvlist(len(fbvlist)) 
			newform = synt.indvsubst(nlist, fbvlist, forms[j])
			newinstance = synt.indvsubst(nlist, ibvlist,instances[j])
			forms.extend(newform[1:])
			instances.extend(newinstance[1:])
			del forms[j]
			del instances[j]
			continue


		for i in rang: # Defined schemator
			if type(forms[i])is list :
				if forms[i][0][0] in [42,43]:
					if forms[i][1] in subst:
						j = i
						break
		if j != -1:
			w = subst[forms[j][1]]
			forms[j] = schemsubst(w,forms[j])
			continue
				
		for i in rang: # Defined schemator
			if type(instances[i])is list :
				if instances[i][0][0] in [42,43]:
					if instances[i][1] in subst:
						j = i
						break
		if j != -1:
			w = subst[instances[j][1]]
			instances[j] = schemsubst(w,instances[j])
			continue


		for i in rang:  # Match shadowed variables 
			if forms[i] in shadow.keys() and instances[i] in shadow.keys():
				j = i
				break
		if j != -1: 
			if shadow[instances[j]][0] != shadow[forms[j]][0]:
				for x in shadow[instances[j]][1:]:
					if x in forms[j][0]:
						return 0
					if x not in shadow[forms[j]]:
						shadow[forms[j]].append(x)
				for x in shadow[instances[j]][0]:
					if x in shadow[forms[j]]:
						return 0
					if x not in shadow[forms[j]][0]:	
						shadow[forms[j]][0].append(x)
					shadow[x] = shadow[forms[j]]
				if forms[j] in subst and instances[j] in subst:
					forms.append(subst[forms[j]])
					instances.append(subst[instances[j]])
					for x in shadow[instances[j]][0]:
						subst[x] = subst[forms[j]]
				elif forms[j] in subst:
					for x in shadow[instances[j]][0]:
						subst[x] = subst[forms[j]]
				elif instances[j] in subst:
					for x in shadow[forms[j]][0]:
						subst[x] = subst[instances[j]]
			del forms[j]
			del instances[j]
			continue

		for i in rang:  # Match shadowed variable 
			if forms[i] in shadow.keys():
				if type(instances[i]) is list  and\
					instances[i][0][0] in [42,43] and instances[i][1] not in givenvars:
					pass
				else:
					j = i
					break
		if j != -1: 
			if type(instances[j]) is str and synt.symtype(instances[j]) in [10,11,14,15]:
				if instances[j] in givenvars or synt.symtype(instances[j]) in [14,15]:
					if forms[j] in subst:
						forms.append(subst[forms[j]])
						instances.append(instances[j])
					else:
						for x in shadow[forms[j]][0]:
							subst[x] = instances[j]
				else:
					if instances[j] in shadow[forms[j]]:
						return 0
					shadow[forms[j]][0].append(instances[j])
					shadow[instances[j]] = shadow[forms[j]]
					if forms[j] in subst:
						subst[instances[j]] = subst[forms[j]]			
			else:
				nb = synt.nblist(instances[j])
				r= shadow_extend(forms[j], nb)
				if r == 0:return 0
#				for x in nb:
#					if x in shadow[forms[j]][0]:
#						return 0
#					elif pattern.bvar.match(x):
#						return 0
#					elif x not in shadow[forms[j]]:
#						shadow[forms[j]].append(x)
#
#New stuff starts here:
#
#				for y in shadow:
#					if y in nb:
#						for z in shadow[y]:
#							if z == shadow[y][0]:
#								pass
#							elif z in shadow[forms[j]][0]:
#								return 0
#							elif z not in shadow[forms[j]]:
#								shadow[forms[j]].append(z)
#				for y in shadow:
#					if forms[j] in shadow[y]:
#						for z in shadow[forms[j]]:
#							if z == shadow[forms[j]][0]:
#								pass
#							elif z == forms[j]:
#								return 0
#							elif z in shadow[y][0]:
#								return 0
#							elif z not in shadow[y]:
#								shadow[y].append(z)
#New stuff ends here

				if forms[j] in subst:
					forms.append(subst[forms[j]])
					instances.append(instances[j])
				else:
					for x in shadow[forms[j]][0]:
						subst[x] = instances[j]
			del forms[j]
			del instances[j]
			continue

		for i in rang:  # Match shadowed variable 
			if instances[i] in shadow.keys():
				if type(forms[i]) is list  and\
					forms[i][0][0] in [42,43] and forms[i][1] not in givenvars:
					pass
				else:
					j = i
					break
		if j != -1: 
			if type(forms[j]) is str  and synt.symtype(forms[j]) in [10,11,14,15]:
				if forms[j] in givenvars or synt.symtype(forms[j]) in [14,15]:
					if instances[j] in subst:
						instances.append(subst[instances[j]])
						forms.append(forms[j])
					else:
						for x in shadow[instances[j]][0]:
							subst[x] = forms[j]
				else:
					if forms[j] in shadow[instances[j]]:
						return 0
					shadow[instances[j]][0].append(forms[j])
					shadow[forms[j]] = shadow[instances[j]]
					if instances[j] in subst:
						subst[forms[j]] = subst[instances[j]]			
			else:
				nb = synt.nblist(forms[j])
				r = shadow_extend(instances[j],nb)
				if r == 0:return 0
#				for x in nb:
#					if x == instances[j]:
#						return 0
#					elif pattern.bvar.match(x):
#						return 0
#					elif x not in shadow[instances[j]]:
#						shadow[instances[j]].append(x)
#
#New stuff starts here:
#
#				for y in shadow:
#					if y in nb:
#						for z in shadow[y]:
#							if z == shadow[y][0]:
#								pass
#							elif z == instances[j]:
#								return 0
#							elif z not in shadow[instances[j]]:
#								shadow[instances[j]].append(z)
#				for y in shadow:
#					if instances[j] in shadow[y]:
#						for z in shadow[instances[j]]:
#							if z == shadow[instances[j]][0]:
#								pass
#							elif z == y:
#								return 0
#							elif z not in shadow[y]:
#								shadow[y].append(z)
#New stuff ends here

				if instances[j] in subst:
					forms.append(forms[j])
					instances.append(subst[instances[j]])
				else:
					for x in shadow[instances[j]][0]:
						subst[x] = forms[j]
			del instances[j]
			del forms[j]
			continue

				
		for i in rang:  # Match unshadowed variables 
			if type(forms[i]) is str  and type(instances[i]) is str and\
			synt.symtype(forms[i])in [10,11] and synt.symtype(instances[i])in [10,11]and\
			forms[i] not in givenvars and instances[i] not in givenvars:
				j = i
				break
		if j != -1: 
			shadow[forms[j]] = [[forms[j],instances[j]]]
			shadow[instances[j]] = shadow[forms[j]]
			del forms[j]
			del instances[j]
			continue

		for i in rang: # Match Unshadowed Variable
			if type(forms[i]) is str  and synt.symtype(forms[i]) in [10,11] and\
         forms[i] not in givenvars:
				if type(instances[i]) is list  and instances[i][0][0] in [42,43] and\
				 instances[i][1] not in givenvars:
					pass
				else:
					j = i
					break
		if j != -1:
			if type(instances[j]) is str  and synt.symtype(instances[j]) in [10,11,14,15]:
				if instances[j] in givenvars or synt.symtype(instances[j]) in [14,15]:
						subst[forms[j]] = instances[j]
						shadow[forms[j]]= [[forms[j]]]
				else:
					print "THIS shouldn't happen"
			else:
				nb = synt.nblist(instances[j])
				r = shadow_extend(forms[j],nb)
				if r == 0: return 0
#				shadow[forms[j]] = [[forms[j]]] 
#				for x in nb:
#					if x == forms[j]:
#						return 0
#					elif pattern.bvar.match(x):
#						return 0
#					elif x not in shadow[forms[j]]:
#						shadow[forms[j]].append(x)
#
#New stuff starts here:
#
#				for y in shadow:
#					if y in nb:
#						for z in shadow[y]:
#							if z == shadow[y][0]:
#								pass
#							elif z == forms[j]:
#								return 0
#							elif z not in shadow[forms[j]]:
#								shadow[forms[j]].append(z)
#				for y in shadow:
#					if forms[j] in shadow[y]:
#						for z in shadow[forms[j]]:
#							if z == shadow[forms[j]][0]:
#								pass
#							elif z == y:
#								return 0
#							elif z not in shadow[y]:
#								shadow[y].append(z)
#New stuff ends here

#				for x in nb:
#					if x == forms[j]:
#						return  0
#					if pattern.bvar.match(x):  # Catch bvars
#						return 0
#					if x not in givenvars and x not in shadow[forms[j]]:
#						shadow[forms[j]].append(x)
#
#New stuff starts here:
#					for y in shadow:
#						if forms[j] in shadow[y]:
#							if x in shadow[y][0]:
#								return 0
#							elif x not in shadow[y]:
#								shadow[y].append(x)
#						elif y == x:
#							for z in shadow[y][1:]:
#								if z in shadow[forms[j]][0]:
#									return 0
#								elif z not in shadow[forms[j]]:
#									shadow[forms[j]].append(z)
#New stuff ends here
	
				subst[forms[j]] = instances[j]
			del forms[j]
			del instances[j]
			continue

		for i in rang: # Match Unshadowed Variable
			if type(instances[i]) is str  and synt.symtype(instances[i]) in [10,11] and\
         instances[i] not in givenvars:
				if type(forms[i]) is list  and forms[i][0][0] in [42,43] and\
				 forms[i][1] not in givenvars:
					pass
				else:
					j = i
					break
		if j != -1:
			if type(forms[j]) is str  and\
         synt.symtype(forms[j]) in [10,11,14,15]:
				if forms[j] in givenvars or synt.symtype(forms[j]) in [14,15]:
						subst[instances[j]] = forms[j]
						shadow[instances[j]]= [[instances[j]]]
				else:
					print "THIS shouldn't happen"
			else:
				nb = synt.nblist(forms[j])
				r = shadow_extend(instances[j],nb)
				if r == 0: return 0
#				shadow[instances[j]] = [[instances[j]]] 
#				for x in nb:
#					if x == instances[j]:
#						return 0
#					elif pattern.bvar.match(x):
#						return 0
#					elif x not in shadow[instances[j]]:
#						shadow[instances[j]].append(x)
#
#New stuff starts here:
#
#				for y in shadow:
#					if y in nb:
#						for z in shadow[y]:
#							if z == shadow[y][0]:
#								pass
#							elif z == instances[j]:
#								return 0
#							elif z not in shadow[instances[j]]:
#								shadow[instances[j]].append(z)
#				for y in shadow:
#					if instances[j] in shadow[y]:
#						for z in shadow[instances[j]]:
#							if z == shadow[instances[j]][0]:
#								pass
#							elif z in shadow[y][0]: 
#								return 0
#							elif z not in shadow[y]:
#								shadow[y].append(z)
#New stuff ends here

#				for x in nb:
#					if x == instances[j]:
#						return  0
#					if pattern.bvar.match(x):  # Catch bvars
#						return 0
#					if x not in givenvars and x not in shadow[instances[j]]:
#						shadow[instances[j]].append(x)
#
#New stuff starts here:
#					for y in shadow:
#						if instances[j] in shadow[y]:
#							if x in shadow[y][0]:
#								return 0
#							elif x not in shadow[y]:
#								shadow[y].append(x)
#						elif y == x:
#							for z in shadow[y][1:]:
#								if z in shadow[instances[j]][0]:
#									return 0
#								elif z not in shadow[instances[j]]:
#									shadow[instances[j]].append(z)
#New stuff ends here
	
				subst[instances[j]] = forms[j]
			del instances[j]
			del forms[j]
			continue

		for i in rang:  # Defined schemator under AND
			if synt.cmop(forms[i]):
				for ii in range(1,len(forms[i])): # Defined schemator
					if type(forms[i][ii])is list :
						if forms[i][ii][0][0] in [42,43]:
							if forms[i][ii][1] in subst.keys():
								jj = ii
								j = i
								break
				else:
					continue
				break
		if j != -1:
			w = subst[forms[j][jj][1]]
			x = schemsubst(w,forms[j][jj])
			if synt.cmop(x) == synt.cmop(forms[j]):
				forms[j][jj:jj+1] = x[1:]
			else:
				forms[j][jj] = x
			continue

		for i in rang:  # Defined schemator under AND
			if synt.cmop(instances[i]):
				for ii in range(1,len(instances[i])):# Defined schemator
					if type(instances[i][ii])is list :
						if instances[i][ii][0][0] in [42,43]:
							if instances[i][ii][1] in subst.keys():
								jj = ii
								j = i
								break
				else:
					continue
				break
		if j != -1:
			w = subst[instances[j][jj][1]]
			x = schemsubst(w,instances[j][jj])
			if synt.cmop(x) == synt.cmop(instances[j]): 
				instances[j][jj:jj+1] = x[1:]
			else:
				instances[j][jj] = x
			continue

		for i in rang:  # Define All Bound Schemator  
			if type(forms[i]) is list  and forms[i][0][0] in [42,43]:
				if forms[i][1] in givenvars:
					pass
#				elif not groundtermp(instances[i]):
#					pass
				else:
					d = dbvlistp(forms[i][2:])
					if d != 0:
						j = i
						break
		if j != -1:
			localbvcond = []
			for k in range(2,len(forms[j])):
 				localbvcond.append([
           addressesof(forms[j][k],instances[j],[]), k - 2 ])
# 							# Slot 0 is the tag, slot 1 the schemator.	
			conj = makeconj( localbvcond)
#			for x in synt.nblist(instances[j]):  # Catch bvars Now done in makesubst
#				if pattern.bvar.match(x):
#					if x not in forms[j]:
#						return 0
			if d == 2:
				w = makesubst(forms[j], instances[j], conj,newbvlist(len(forms[j][2:])))	
			else:
				w = makesubst(forms[j], instances[j], conj) 
			if w == 0: return 0
			subst[forms[j][1]] = w
			shadow[forms[j][1]] = makeshadow(w)
			if forms[j][1] in schematch.keys():
				for s,v in schematch[forms[j][1]]:
					x = schemsubst(w,s)
					instances.append(x)
					forms.append(v)
				del schematch[forms[j][1]]
			continue


		for i in rang:  # Define All Bound Schemator  
			if type(instances[i]) is list  and instances[i][0][0] in [42,43]:
				if instances[i][1] in givenvars:
					pass
#				elif not groundtermp(forms[i]):
#					pass
				else:
					d = dbvlistp(instances[i][2:])
					if d != 0:
						j = i
						break
		if j != -1:
			localbvcond = []
			for k in range(2,len(instances[j])):
 				localbvcond.append([addressesof(instances[j][k],forms[j],[]), k - 2 ])
# 							# Slot 0 is the tag, slot 1 the schemator.	
			conj = makeconj( localbvcond)
#			for x in synt.nblist(forms[j]):  # Catch bvars  now done in makesubst
#				if pattern.bvar.match(x):
#					if x not in instances[j]:
#						return 0
			if d == 2:
				w = makesubst(instances[j], forms[j], conj, newbvlist(len(instances[j][2:]))) 
			else:
				w = makesubst(instances[j], forms[j], conj) 
			if w == 0: return 0
			subst[instances[j][1]]= w
			shadow[instances[j][1]] = makeshadow(w)
			if instances[j][1] in schematch.keys():
				for s,v in schematch[instances[j][1]]:
					x = schemsubst(w,s)
					forms.append(x)
					instances.append(v)
				del schematch[instances[j][1]]
			continue
		
#		print "QQQQ"
		for i in rang:  # match one AND conjunct 
			if '' != synt.cmop(forms[i]) == synt.cmop(instances[i]):
				formsj = conjuncts(forms[i])
				instancesj = conjuncts(instances[i])
				wf = wildcardindices(formsj)
				wi = wildcardindices(instancesj)
				nwf = len(wf)
				nwi = len(wi)
				if nwi == nwf == 0 and conjlen(formsj) != conjlen(instancesj):
#					print "1"
					return 0	
#				print "instancesj = ", instancesj
#				matches=couldmatches(formsj,instancesj)
#				print "Matches:"
#				print "nwf = ", nwf
#				print "nwi = ", nwi
#				for m in matches:
#					print "len = ", len(m[2])
#					synt.pprint(m)
				if nwi == 0:
					m = [0,1]
					for k in range(len(formsj)):
						if k in wf:
							continue
						x = formsj[k]
						m = could_matches(x, instancesj,givenvars)
						if len(m) < 2: break
					if len(m) == 0: return 0
					if len(m) == 1: 
						savematch = ['f', x, m]
						j = i 
						break
				if nwf == 0:
					m = [0,1]
					for k in range(len(instancesj)):
						if k in wi:
							continue
						y = instancesj[k]
						m = could_matches(y, formsj,givenvars)
						if len(m) < 2: break
					if len(m) == 0: return 0
					if len(m) == 1:
						savematch = [ 'i', y, m]
						j = i
						break
							
		if j != -1:
			usedflags = usedflags|2
			match = savematch 
# 			print "Using match = ", match
# Need a second case for an AND match
			if match[0] == 'f':
				formsj.remove(match[1])
				if type(match[2][0] )is list :
					if type(match[2][0][0]) is not list:
						print "bad form =", match
						raise SystemExit
				if synt.cmop(match[2][0]):
# This case should be handled elsewhere 
					for k in range(1,len(match[2][0]),2):
						instancesj.remove(match[2][0][k])
				else:
					instancesj.remove(match[2][0])
				if not instancesj: 
					return 0
				forms.append(match[1])
				instances.append(match[2][0])
			elif match[0] == 'i':
				instancesj.remove(match[1])
				if synt.cmop(match[2][0]):
# This case should be handled elsewhere 
					for k in range(1,len(match[2][0]),2):
						formsj.remove(match[2][0][k])
				else:
					formsj.remove(match[2][0])
				if not formsj: 
					return 0
				forms.append(match[2][0])
				instances.append(match[1])
			forms[j] = newconjunction(forms[j], formsj)
			instances[j] = newconjunction(instances[j],instancesj)
			continue

#		print "RRRR"
		for i in rang:  # match one all-bound schematic AND conjunct 
			if j != -1: break
			if '' != synt.cmop(forms[i]) == synt.cmop(instances[i]):
				formsj = conjuncts(forms[i])
				instancesj = conjuncts(instances[i])
				wf = wildcardindices(formsj)
				wi = wildcardindices(instancesj)
				if len(wi) == 0:
					for x in formsj:
						if type(x) is list  and x[0][0] in [42,43]:
							if x[1] in givenvars:
								pass
							elif x[1] in schematch and dbvlistp(x[2:]) == 1:
								projections = []
								for z in x[2:]:
									if z in instancesj:
										projections.append(z)
								if projections:
									print "Projections present, code needed!"
									continue
								cmop_and = True 
								cmop_or = False
								for u,v in schematch[x[1]]:
									cmopp = (synt.cmop(v)== synt.cmop(forms[i]))
									if cmopp: arity = conjlen(odds(v))
									cmop_and = cmop_and and cmopp
									cmop_or = cmop_or or cmopp
								if cmop_or != cmop_and:
									return 0
								if cmop_or:
									matches = []
									for y in instancesj: 	
										for u,v in schematch[x[1]]:
											for k in range(1,len(v),2):
												if bvcould_match(x,y,u,v[k]) != 0:
													break
											else:
												break
										else:
											matches.append(y)
									if len(matches) < arity:
										return 0
									if len(matches) == arity:
										savematch = ['f', x, matches]
										j = i 
										break
								else:
									matches = []
									for y in instancesj: 	
										for u,v in schematch[x[1]]:
											if bvcould_match(x,y,u,v) == 0:
												break
										else:
											matches.append(y)
									if len(matches) == 0:
										return 0
									if len(matches) == 1:
										savematch = ['f', x, matches]
										j = i 
										break
				if len(wf) == 0:
					for y in formsj:
						if type(y) is list  and y[0][0] in [42,43]:
							if y[1] in givenvars:
								pass
							elif y[1] in schematch and dbvlistp(y[2:]) == 1:
								projections = []
								for z in y[2:]:
									if z in formsj:
										projections.append(z)
								if projections:
									print "Projections present, code needed!"
									continue
								cmop_and = True 
								cmop_or = False
								for u,v in schematch[y[1]]:
									cmopp = (synt.cmop(v)== synt.cmop(instances[i]))
									if cmopp: arity = conjlen(odds(v))
									cmop_and = cmop_and and cmopp
									cmop_or = cmop_or or cmopp
								if cmop_or != cmop_and:
									return 0
								if cmop_or:
									matches = []
									for x in formsj: 	
										for u,v in schematch[y[1]]:
											for k in range(1,len(v),2):
												if bvcould_match(y,x,u,v[k]) != 0:
													break
											else:
												break
										else:
											matches.append(x)
									if len(matches) < arity:
										return 0
									if len(matches) == arity:
										savematch = ['i', y, matches]
										j = i 
										break
								else:
									matches = []
									for x in formsj: 	
										for u,v in schematch[y[1]]:
											if bvcould_match(y,x,u,v) == 0:
												break
										else:
											matches.append(x)
									if len(matches) == 0:
										return 0
									if len(matches) == 1:
										savematch = ['i', y, matches]
										j = i 
										break
				
		if j != -1:
			usedflags = usedflags|64
			match = savematch 
# 			print "Using match = ", match
# 			print "Using formsj = ", formsj 
			if match[0] == 'f':
				formsj.remove(match[1])
				for z in match[2]:
					instancesj.remove(z)
				if not instancesj: 
					return 0
				forms.append(match[1])
				instances.append(newconjunction(forms[j],match[2]))
			elif match[0] == 'i':
				instancesj.remove(match[1])
				for z in match[2]:
						formsj.remove(z)
				if not formsj: 
					return 0
				forms.append(newconjunction(instances[j],match[2]))
				instances.append(match[1])
			forms[j] = newconjunction(forms[j], formsj)
			instances[j] = newconjunction(instances[j],instancesj)
			continue
							
					
#		print "SSSS"
		for i in rang:# AND equation subtracting
# if one is a subset of the other 
			if j != -1:break
			if synt.cmop(forms[i]):
				for ii in rang:
					if ii > i and synt.cmop(forms[ii]):
						if len(forms[i])>len(forms[ii])and\
             len(instances[i])>len(instances[ii]):
							longf = forms[i]
							shortf = forms[ii]
							jj = i
							longi = instances[i]
							shorti = instances[ii]
						elif len(forms[ii])>len(forms[i])and\
             len(instances[ii])>len(instances[i]):
							longf = forms[ii]
							shortf = forms[i]
							jj = ii
							longi = instances[ii]
							shorti = instances[i]
						else:
							continue
						flongs = odds(longf)
						fshorts = odds(shortf)
						for x in fshorts:
							if x in flongs:
								flongs.remove(x)
							else:
								break
						else:
							ilongs = odds(longi)
							ishorts = odds(shorti)
							for x in ishorts:
								if x in ilongs:
									ilongs.remove(x)
								else:
									break
							else:
								j = jj
								break
		if j != -1:
			usedflags = usedflags|1 # Subtracting Equations
			newform = newconjunction(longf, flongs)
			newinst = newconjunction(longi, ilongs)
			forms[j] = newform
			instances[j] = newinst
			continue	

#		print "TTTT"
		for i in rang:# Grounded Undefined Schematic Expression
			if type(forms[i])is list  and forms[i][0][0] in [42,43] and forms[i][1] not in givenvars:
				if forms[i][1] not in schematch.keys():
					for kk in  range(2,len(forms[i])):
						if not groundtermp(forms[i][kk]):
							break
					else:
						j = i
						break
		if j != -1:
			schematch[forms[j][1]] = [[forms[j],instances[j]]]
			del forms[j]
			del instances[j]
			continue

#		print "UUUU"
		for i in rang:# Grounded Undefined Schematic Expression
			if type(instances[i])is list  and instances[i][0][0] in [42,43]and instances[i][1] not in givenvars:
				if instances[i][1] not in schematch.keys():
					for kk in  range(2,len(instances[i])):
						if not groundtermp(instances[i][kk]):
							break
					else:
						j = i
						break
		if j != -1:
			schematch[instances[j][1]] = [[instances[j],forms[j]]]
			del forms[j]
			del instances[j]
			continue
		
#		print "VVVV"
		for i in rang:# Undefined Schematic Expression
			if type(forms[i])is list  and forms[i][0][0] in [42,43] and forms[i][1] not in givenvars:
#			if type(forms[i])is list  and forms[i][0][0] in [42,43]:
				j = i
				break
		if j != -1:
			usedflags = usedflags|4
			if forms[j][1] not in schematch.keys():
				schematch[forms[j][1]] = []
			if forms[j][1] not in schemcond.keys():
				schemcond[forms[j][1]] = []

      #Main Slot Filling Loop
			knownslots = []
			knownaddresses = []
			for u,v in schemcond[forms[j][1]]:
				knownslots.append(v)
				knownaddresses.extend(u)
			n_knownslots = -1
			while n_knownslots < len(knownslots): 
				n_knownslots = len(knownslots)
				
        #Find all unique bv slots:
				unique_bvcoords = []
				if groundtermp(instances[j]):
					for k in range(2,len(forms[j])):
						if k - 2 not in knownslots and type(forms[j][k]) is str  and\
                                                 pattern.bvar.match(forms[j][k]):
							for kk in range(2,len(forms[j])):
								if kk - 2 in knownslots or kk == k:
									pass
								elif addressesof(forms[j][k],forms[j][kk],[]):
									break
							else:
								unique_bvcoords.append(k)
	
				for k in unique_bvcoords:
					schemads = addressesof(forms[j][k],instances[j],[])
					okschemads = []
					for  a in schemads:
						for b in knownaddresses:
							if inline(a,b):
								if len(a)  < len(b):
									return 0
								else:
									break
						else:
							okschemads.append(a)  
					schemcond[forms[j][1]].append([okschemads, k - 2])
				# Slot 0 is the tag, slot 1 the schemator.	


				knownslots = []
				knownaddresses = []
				for u,v in schemcond[forms[j][1]]:
					knownslots.append(v)
					knownaddresses.extend(u)


      #Find a single difference slot 
				if len(knownslots) + 2 < len(forms[j]):
					for u,v in schematch[forms[j][1]]:
						ndiffs = 0
#						print "ndiffs1 = ", ndiffs
						for k in range(2,len(forms[j])):
							if k - 2 in knownslots:
								pass
							elif groundeq(u[k], forms[j][k]):
								pass
							else:
								ndiffs = ndiffs + 1
								diffspot = k
						if ndiffs == 1: 
							d = diffaddresslist(forms[j][diffspot],u[diffspot],instances[j],v,
                                         knownaddresses,[])
							if d == 0:
								if groundtermp(u[diffspot]) and \
                                         groundtermp(forms[j][diffspot]):
#									print "u[diffspot]= ",u[diffspot]
#									print "groundedvars = ", groundedvars
#									print "forms[j][diffspot] = ", forms[j][diffspot]
#									print "HHH"
									return 0
								else:
									break
							elif d[0] == [[]]:
#								print "HIJHIJ"
								break
							else:
								schemcond[forms[j][1]].append([d[0],diffspot -2])
								newmatches = d[1]
# 								print "addresses = ", d[0]
# 								print "newmatches = ", d[1]
								for uu,vv in newmatches:
									forms.append(uu)
									instances.append(vv) 
#								print 3434,d
								break


				knownslots = []
				knownaddresses = []
				for u,v in schemcond[forms[j][1]]:
					knownslots.append(v)
					knownaddresses.extend(u)
       #End of slot filling loop

			schematch[forms[j][1]].append([forms[j],instances[j]])
#			print "schematch = ", schematch

#			print "len(forms[j]) = ", len(forms[j])
#			print " n_knownslots + 2 = ", n_knownslots + 2 
#			print "knownslots = ", knownslots 
#			print "knownaddresses = ", knownaddresses
			
			if n_knownslots + 2 == len(forms[j]):
				newform = forms[j][:2] + newbvlist(len(forms[j][2:]))
				conj = makeconj(schemcond[forms[j][1]])
#				print "newform = ", newform
#				print "instances[j] = ", instances[j] 
#				print "conj = ", conj 
#           We probably need to ground instances[j]
				w = makesubst(newform,instances[j],conj)
				if w == 0:return 0
				subst[forms[j][1]] = w 
				shadow[forms[j][1]] = makeshadow(w)
				for x in synt.nblist(w[1]):
					if not pattern.bvar.match(x) and x not in shadow[forms[j][1]]:
						shadow[forms[j][1]].append(x)
			 
				for u,v in schematch[forms[j][1]]:
					forms.append(schemsubst(w,u))
					instances.append(v)
				del schemcond[forms[j][1]]
				del schematch[forms[j][1]]
			del forms[j]
			del instances[j]
			continue

#		print "WWWW"
		for i in rang:# Undefined Schematic Expression
			if type(instances[i])is list  and instances[i][0][0] in [42,43]and instances[i][1] not in givenvars:
#			if type(instances[i])is list  and instances[i][0][0] in [42,43]:
				j = i
				break
		if j != -1:
			usedflags = usedflags|4
			if instances[j][1] not in schematch.keys():
				schematch[instances[j][1]] = []
			if instances[j][1] not in schemcond.keys():
				schemcond[instances[j][1]] = []

         #Main Slot Filling Loop
			knownslots = []
			knownaddresses = []
			for u,v in schemcond[instances[j][1]]:
				knownslots.append(v)
				knownaddresses.extend(u)
			n_knownslots = -1
			while n_knownslots < len(knownslots): 
				n_knownslots = len(knownslots)
				
            #Find all unique bv slots:
				unique_bvcoords = []
				if groundtermp(forms[j]):
					for k in range(2,len(instances[j])):
						if k - 2 not in knownslots and \
                type(instances[j][k]) is str  and\
                pattern.bvar.match(instances[j][k]):
							for kk in  range(2,len(instances[j])):
								if kk - 2 in knownslots or kk == k:
									pass
								elif addressesof(instances[j][k],instances[j][kk],[]):
									break
							else:
								unique_bvcoords.append(k)
	
				for k in unique_bvcoords:
					schemads = addressesof(instances[j][k],forms[j],[])
					okschemads = []
					for  a in schemads:
						for b in knownaddresses:
							if inline(a,b):
								if len(a)  < len(b):
									return 0
								else:
									break
						else:
							okschemads.append(a)  
					schemcond[instances[j][1]].append([okschemads, k - 2])
				# Slot 0 is the tag, slot 1 the schemator.	


				knownslots = []
				knownaddresses = []
				for u,v in schemcond[instances[j][1]]:
					knownslots.append(v)
					knownaddresses.extend(u)


            #Find a single difference slot 
				if len(knownslots) + 2 < len(instances[j]):
					for u,v in schematch[instances[j][1]]:
						ndiffs = 0
#						print "ndiffs2 = ", ndiffs
						for k in range(2,len(instances[j])):
							if k - 2 in knownslots:
								pass
							elif groundeq(u[k], instances[j][k]):
								pass
							else:
								ndiffs = ndiffs + 1
								diffspot = k
						if ndiffs == 1: 
							d = diffaddresslist( instances[j][diffspot],u[diffspot],forms[j],v,
                                          knownaddresses,[])
							if d == 0:
								if groundtermp(u[diffspot]) and \
                                  groundtermp(instances[j][diffspot]):
									return 0
								else:
									break
							else:
								schemcond[instances[j][1]].append([d[0],diffspot -2])
								newmatches = d[1]
								for uu,vv in newmatches:
									forms.append(uu)
									instances.append(vv) 
								break


				knownslots = []
				knownaddresses = []
				for u,v in schemcond[instances[j][1]]:
					knownslots.append(v)
					knownaddresses.extend(u)
         #End of slot filling loop

			schematch[instances[j][1]].append([instances[j],forms[j]])

			if n_knownslots + 2 == len(instances[j]):
				newform = instances[j][:2] + newbvlist(len(instances[j][2:]))
				conj = makeconj(schemcond[instances[j][1]])
				w = makesubst(newform,forms[j],conj)
#				print "newform = ", newform
#				print "conj= ", conj
				if w == 0 : return 0
				subst[instances[j][1]] = w 
				shadow[instances[j][1]] = makeshadow(w)
				for x in synt.nblist(w[1]):
					if not pattern.bvar.match(x) and x not in shadow[instances[j][1]]:
						shadow[instances[j][1]].append(x)
			 
				for u,v in schematch[instances[j][1]]:
					instances.append(schemsubst(w,u))
					forms.append(v)
				del schemcond[instances[j][1]]
				del schematch[instances[j][1]]
			del instances[j]
			del forms[j]
			continue

#		print "XXXX"
		for i in rang: # match one AND conjunct by counting
			if '' != synt.cmop(forms[i]) == synt.cmop(instances[i]): 
				formsj = conjuncts(forms[i])
				instancesj = conjuncts(instances[i])
				wf = wildcardindices(formsj)
				wi = wildcardindices(instancesj)
				nwf = len(wf)
				nwi = len(wi)
#				print "instancesj = ", instancesj
				matches=couldmatches(formsj,instancesj)
#				print "Matches:"
#				for m in matches:
#					print "len = ", len(m[2])
#					synt.pprint(m)
#				savematch = matches[0]
				matchnum = 10000 
				if nwf == 1 and nwi == 0:
					wind = wf[0]
					wmatches = could_matches(formsj[wind],instancesj,givenvars)
#					for match in matches:
#						if match[0]=='f' and match[1] == formsj[wind]:
#							wmatches = match[2]
#							break
#					else:
#						raise "Missing wildcard"
					if type(formsj[wind]) is str :
						twcf = formsj[wind]
						nomatches = 1
						for ii in rang:
							if ii == i:
								continue
							if synt.cmop(forms[ii]) == '':
								continue
							if twcf not in forms[ii]:
								continue
							formsji = conjuncts(forms[ii])
							instancesji = conjuncts(instances[ii])
							if wildcardindices(instancesji):
								continue
							cmatches = could_matches(twcf,instancesji,givenvars)
#							matches=couldmatches(formsji,instancesji)
#							for match in matches:
#								if match[0]=='f' and match[1] == twcf:
#									cmatches = match[2]
#									break
#							else:
#								raise "Missing wildcard"
							nomatches = 0
				
							wmatches = pairoff(wmatches,cmatches)
						if nomatches:
							continue
						cf = conjlen(odds(forms[i]))
						ci = conjlen(odds(instances[i]))
						if wmatches == []:
							print "New rejection"
							return 0
						if len(wmatches) + cf < ci + 1:
							print "2138" 
							return 0
						elif len(wmatches) + cf == ci + 1:
							j = i
							newcon = newconjunction(instances[i],wmatches) 
#							match[2] = [newcon]
							savematch = ['f', twcf, [newcon]] 
							break

					else: 
						twcf = formsj[wind][1]
#						print "twcf = ", twcf
						nomatches = 1
						for ii in rang:
							if ii == i:
								continue
							if not synt.cmop(forms[ii]):
								continue
							for xii in forms[ii]:
								if type(xii) is list  and xii[0] in [42,43] and xii[1] == twcf:
									xiij = xii
									break
							else:
								continue
							formsji = conjuncts(forms[ii])
							instancesji = conjuncts(instances[ii])
							if wildcardindices(instancesji):
								continue 
							matches=couldmatches(formsji,instancesji)
							for match in matches:
								if match[0] == 'f' and match[1] == xiij:
									cmatches = match[2]
									break
							else:
								raise "Programming error"
							rvar = revarmatches([xiij,cmatches],formsj[wind])
							if not rvar:
								continue
							nomatches = 0
							wmatches = pairoff(wmatches,rvar)
						if nomatches:
							continue
						cf = conjlen(odds(forms[i]))
						ci = conjlen(odds(instances[i]))
						if len(wmatches) + cf < ci + 1:
							print "2173"
							return 0
						elif len(wmatches) + cf == ci + 1:
							j = i
#							print "cf =", cf
#							print "ci =", ci
							newcon = newconjunction(instances[i],poff) 
							match[2] = [newcon]
							savematch = match 
#							print "savematch = "
#							synt.pprint(savematch)
							break

				elif nwi == 1 and nwf == 0:
					wind = wi[0]
					for match in matches:
						if match[0] == 'i' and match[1] == instancesj[wind]:
							wmatches =match[2]
							break
					else:
						raise "Missing wildcard"
					if type(instancesj[wind]) is str :
						twci = instancesj[wind]
						nomatches = 1
						for ii in rang:
							if ii == i:
								continue
							if synt.cmop(instances[ii]) == '':
								continue
							formsji = conjuncts(forms[ii])
							instancesji = conjuncts(instances[ii])
							if wildcardindices(formsji):
								continue
							for match in matches:
								if match[0] == 'i' and match[1] == twci:
									cmatches = match[2]
									break
							else:
								raise "Missing wildcard"
							nomatches = 0
							wmatches = pairoff(wmatches,cmatches)
						if nomatches:
							continue
						cf = conjlen(odds(forms[i]))
						ci = conjlen(odds(instances[i]))

						if len(wmatches) + ci < cf + 1:
							return 0
						elif len(wmatches) + ci == cf + 1:
							j = i
							newcon = newconjunction(forms[i],wmatches)
							match[2] = [newcon]
							savematch = match
							break
					else:
						twci = instancesj[wind][1]
						nomatches = 1
						for ii in rang:
							if ii == i:
								continue
							if not synt.cmop(instances[ii]):
								continue
						for xii in instances[ii]:
							if type(xii)is list  and xii[0] in [42,43] and xii[1] == twci:
								xiij = xii
								break
						else:
							continue
						formsji = conjuncts(forms[ii])
						instancesji = conjuncts(instances[ii])
						if wildcardindices(formsji):
							continue
						matches = couldmatches(instancesji,formsji)
						for match in matches:
							if match[0] == 'i' and match[1] == xiij:
								cmatches = match[2]
								break
						else:
							raise "Programming error"
						rvar = revarmatches([xiij,cmatches],instancej[wind])
						if not rvar:
							continue
						nomatches = 0
						wmatches = pairoff(wmatches,rvar)
					if nomatches:
						continue
					cf = conjlen(odds(forms[i]))
					ci = conjlen(odds(instances[i]))
					if len(wmatches) + ci < cf + 1:
						return 0
					elif len(wmatches) + ci == cf + 1:
						j = i
						newcon = newconjunction(forms[i], wmatches)
						match[2] = [newcon]
						savematch = match
						break

		if j != -1:
			usedflags = usedflags|8
			match = savematch 
# Need a second case for an AND match
			if match[0] == 'f':
				formsj.remove(match[1])
				if type(match[2][0] )is list :
					if type(match[2][0][0]) is not list:
						print "bad form =", match
						raise "parse error"
				if synt.cmop(match[2][0]):
					for k in range(1,len(match[2][0]),2):
						instancesj.remove(match[2][0][k])
				else:
					instancesj.remove(match[2][0])
				if not instancesj: return 0
				forms.append(match[1])
				instances.append(match[2][0])
			elif match[0] == 'i':
				instancesj.remove(match[1])
				if synt.cmop(match[2][0]):
					for k in range(1,len(match[2][0]),2):
						formsj.remove(match[2][0][k])
				else:
					formsj.remove(match[2][0])
				if not formsj: return 0
				forms.append(match[2][0])
				instances.append(match[1])
			forms[j] = newconjunction(forms[j], formsj)
			instances[j] = newconjunction(instances[j],instancesj)
			continue

#		print "YYYY"
		newmatch = []
		for p in []: 
#		for p in schematch: # Look for fixable variables in a schemator under an AND
			newmatch = []
			andmatch = -1
			for u,v in schematch[p]:
				foundcmop = synt.cmop(v)
				if foundcmop:
					if andmatch == -1:
						andmatch = 1
					elif andmatch == 0:
						andmatch = 2
				else:
					if andmatch == -1:
						andmatch = 0
					elif andmatch == 1:
						andmatch = 2
			if andmatch == 2: break
				
			# Find schemator under an AND
			# See if any possible matches are forced
			# See of any of these can be produce a difference of one only slot
			# See if these provide a variable match from diffaddresslist
			if andmatch == 0:
				for i in rang:
					if '' != synt.cmop(forms[i]) == synt.cmop(instances[i]):
						m = len(forms[i])
						n = len(instances[i])
						for ii in range(1,m,2):
							if type(forms[i][ii]) is list  and forms[i][ii][0][0] in[42,43] and\
	                              forms[i][ii][1] == p: 
								for jj in range(1,n,2):
									matchlist = could_matches(instances[i][jj],odds(forms[i]),givenvars)
									if len(matchlist) > 1: continue
									elif len(matchlist)==0: return 0
									elif matchlist[0] != forms[i][ii] : continue
									mustmatch = matchlist[0]
									print "mustmatch =  ", mustmatch 
									for u,v in schematch[p]: # Look for unsubsted variable
										compkey = comparison_key(u,forms[i][ii])
										if compkey == 0:
											continue
										if len(compkey[0]) == 0: # Try to remove a conjunct
											continue
										else: # if n_slot_diffs == 1: 
											slot_num = compkey[0][0]
											knownaddresses = []
											for k in compkey[1]:
												knownaddresses.extend(
                                         addressesof(schemexp1[k],instances[i][jj]))
											print "forms[i][ii][slot_num] =",forms[i][ii][slot_num] 
											print "u[slot_num] = ", u[slot_num]
											print "instances[i][jj] = ", instances[i][jj]
											print "v = ", v
											print "knownaddresses = ", knownaddresses 
											d = diffaddresslist(forms[i][ii][slot_num],u[slot_num],
                                                  instances[i][jj],v,knownaddresses,[])
											print "d = ", d
											if d == 0 : return 0
											# Look for unsubsted (or unshadowed ?) variable
											for uu,vv in d[1]: 
												if type(uu) is str and\
													synt.symtype(uu) in [10,11] and \
                                       uu not in givenvars and uu not in subst.keys():
													newmatch = [uu,vv]
													break
												if type(vv) is str and\
													synt.symtype(vv) in [10,11] and \
                                       vv not in givenvars and vv not in subst.keys():
													newmatch = [uu,vv]
													break
										if newmatch: break
									if newmatch: break
								if newmatch: break
						if newmatch: break
			elif andmatch == 1:
#				print "ABCABC"
#				raise "Got here"
				for i in rang:
					if '' != synt.cmop(forms[i]) == synt.cmop(instances[i]):
						m = len(forms[i])
						n = len(instances[i])
						for ii in range(1,m,2):
							if type(forms[i][ii]) is list  and forms[i][ii][0][0] in[42,43] and\
	                              forms[i][ii][1] == p: 
								for jj in range(1,n,2):
									matchlist = could_matches(instances[i][jj],odds(forms[i]),givenvars)
									if len(matchlist) > 1: continue
									elif len(matchlist)==0: return 0
									elif matchlist[0] != forms[i][ii] : continue
									mustmatch = matchlist[0]
									for u,v in schematch[p]: # Look for unsubsted variable
#										print "u = ", u
#										print "v = ", v
										compkey = comparison_key(u,forms[i][ii])
										if compkey == 0:
											continue
										if len(compkey[0]) == 0: # Try to remove a conjunct
											continue
										else: #  n_slot_diffs == 1:
											slot_num = compkey[0][0]
#											print "slot_num = ", slot_num
											knownaddresses = []
											for k in compkey[1]:
												knownaddresses.extend(
                                         addressesof(schemexp1[k],instances[i][jj]))
											diffaddlist = []
											for w in range(1,len(v),2):
#												print "forms[i][ii][slot_num] =",forms[i][ii][slot_num] 
#												print "u[slot_num] = ", u[slot_num]
#												print "instances[i][jj] = ", instances[i][jj]
#												print "v[w] = ", v[w]
#												print "knownaddresses = ", knownaddresses 
												d = onediffaddresslist(
                                                  instances[i][jj],v[w],knownaddresses,[])
#												print "d = " , d
												if d[0] == [] or d[0] == [[]]:
													continue
												# Look for unsubsted (or unshadowed ?) variable
												uu = forms[i][ii][slot_num] 
												vv = u[slot_num]
												if type(uu) is str  and \
                                       synt.symtype(uu) in [10,11] and \
       	                              uu not in givenvars and uu not in subst.keys():
													#print "d = ", d
													newmatch = [uu, d[1][0]] 
													break
												if type(vv) is str  and \
                                       synt.symtype(vv) in [10,11] and \
       	                              vv not in givenvars and vv not in subst.keys():
													newmatch =  [d[1][1], vv] 
													break
										if newmatch: break
									if newmatch: break
								if newmatch: break
						if newmatch: break
								
		if newmatch:
#			raise "It is used"
			forms.append(newmatch[0])
			instances.append(newmatch[1])
			continue

#		print "ZZZZ"
		for i in rang:  # commutative AND matching 
			if '' != synt.cmop(forms[i]) == synt.cmop(instances[i]):
				formsj = conjuncts(forms[i])
				instancesj = conjuncts(instances[i])
				wf = wildcardindices(formsj)
				wi = wildcardindices(instancesj)
				nwf =  len(wf)
				nwi =  len(wi)
#				print "i = ", i
# 				print "nwf = ", nwf
# 				print "nwi = ", nwi
				if nwi + nwf < 2:
					nwfj = nwf
					nwij = nwi
					j = i 
				if nwi + nwf == 0:
					break
		if j != -1:
			print "Guessing now"
			usedflags = usedflags | 128 # Guessing now
			andop = forms[j][2]
			substdomain = subst.keys() 
#			print "formsj =", formsj
#			print "instancesj = ", instancesj
#			print "wf = ",wf
#			print "wi = ",wi
					
			if nwfj == 1 :
				if len(instances[j]) < len(forms[j]) :
#					print 555, "no"
					return 0

				newinstances = []
				wildcard = formsj[wf[0]]
				del formsj[wf[0]]
				for y in formsj:
					for x in instancesj:
						if couldmatch(y,x):
							newinstances.append(x)
							instancesj.remove(x)
							break
					else:
# 						print 55, instancesj,y
						return 0
#				print "wildcard = ", wildcard
				if instancesj == []:
					print "wildcard jilted"
					return 0
				forms.extend(formsj)
				instances.extend(newinstances)
				forms.append(wildcard)
				if len(instancesj) > 1:
					newandform = [forms[j][0]]
					for x in instancesj:
						newandform.append(x)
						newandform.append(andop)
					newandform.pop()
					instances.append(newandform)
				else:
#					synt.pprint(instances)
#					synt.pprint(instancesj)
					instances.append(instancesj[0])
				del forms[j]
				del instances[j]
				continue
			elif nwij == 1 :
				if  len(instances[j]) > len(forms[j]) :
#					print 66, "what??"
					return 0
				wildcard = instancesj[wi[0]] 
				del instancesj[wi[0]]
				newforms = []
				for y in instancesj:
					for x in formsj:
						if couldmatch(y, x):
							newforms.append(x)
							formsj.remove(x)
							break
					else:
#							print 56, formsj, instancesj[0]
						return 0
				if formsj == []:
					print "wildcard jilted"
					return 0
				forms.extend(newforms)
				instances.extend(instancesj)
				instances.append(wildcard)
				if len(formsj) > 1: 
					newandform = [instances[j][0]]
					for x in formsj:
						newandform.append(x)
						newandform.append(andop)
					newandform.pop()
					forms.append(newandform)
				else:
					forms.append(formsj[0])
				if len(forms) != len(instances):
					print len(forms)
					print len(instances)
				del forms[j]
				del instances[j]
				continue
			else:
				if len(formsj) != len(instancesj):
# 					print "1111"
#					print nwfj
#					print nwij
					return 0	
				matches = []
				for x in formsj:
					xmatch = [] 
					for y in instancesj:
#						print "trying couldmatch"
#						print "x = ", x
#						print "y = ", y
#						print "givenvars = ", givenvars
#						print "subst = ", subst
						if couldmatch(x,y):
							xmatch.append(y)
					matches.append(['f',x,xmatch])
					if len(xmatch) == 0:
#						print "x = ", x
#						print "instancesj = ", instancesj
#						print "2222"
						return 0
				for y in instancesj:
					ymatch = []
					for x in formsj:
						if couldmatch(x,y):
							ymatch.append(x)
					matches.append(['i',y,ymatch])
					if len(ymatch)== 0:
						print "3333"
						return 0
 
				formsjp = []
				instancesjp = []
				while instancesj:
					nextmatch = matches[0]
					matchnum = len(nextmatch[2])
					for match in matches:
						if len(match[2]) <  matchnum:
							nextmatch = match
							matchnum = len(nextmatch[2])
					if matchnum == 0:
						print "4444"
						return 0
					matches.remove(nextmatch)
					if nextmatch[0] == 'f':
						for matchp in matches:
							if matchp[0] == 'f' and  nextmatch[2][0] in matchp[2]:
								matchp[2].remove(nextmatch[2][0])
						for matchp in matches:
							if matchp[0] == 'i' and matchp[1] == nextmatch[2][0]:
								break
						matches.remove(matchp)
						for matchp in matches:
							if matchp[0] == 'i' and matchp[1] == nextmatch[2][0]:
								matchp[2].remove(nextmatch[1])
						formsj.remove(nextmatch[1])
						instancesj.remove(nextmatch[2][0])
						formsjp.append(nextmatch[1])
						instancesjp.append(nextmatch[2][0])
					else:#if nextmatch[0] == 'i':
						for matchp in matches:
							if matchp[0] == 'i' and nextmatch[2][0] in matchp[2]:
								matchp[2].remove(nextmatch[2][0])
						for matchp in matches:
							if matchp[0] == 'f' and matchp[1] == nextmatch[2][0]:
								break
						matches.remove(matchp)
						for matchp in matches:
							if matchp[0] == 'f' and matchp[1] == nextmatch[2][0]:
								matchp[2].remove(nextmatch[1])
						instancesj.remove(nextmatch[1])
						instancesjp.append(nextmatch[1])
						formsj.remove(nextmatch[2][0])
						formsjp.append(nextmatch[2][0])
				del instances[j]
				del forms[j]
				forms.extend(formsjp)
				instances.extend(instancesjp)
				continue

#		if forms == []:
#			for x in schematch.keys():
#				print "schematch =",x, schematch[x]

#		print "Match exhausted"
		return 0
# Could check for consistency of subst here
# Will not do this unless errors appear
	return [usedflags, subst]

def conjlen(formlist):
	count = 0
	for f in formlist:
		if type(f) is list  and f[0][0] in [42,43]\
         and f[1] in schematch.keys()and synt.cmop(schematch[f[1]][0][1]):
			count = count + len(schematch[f[1]][0][1])/2
		elif f in subst.keys() and synt.cmop(subst[f]):
			count = count + len(subst[f])/2
		else:
			count = count +1
	return count

def dbvlistp(arglist):
	if type(arglist)is not list:
		raise "List expected"
	for x in arglist:
		if type(x) is not str :
			break
			return 0
		if not pattern.bvar.match(x):
			return 0
		if arglist.count(x) > 1:
			return 0
	else:
		return 1
	n = len(arglist)
	for k in range(n):
		x = synt.nblist(arglist[k])
		if x == []:
			return 0
		for y in x:
			if not pattern.bvar.match(y):
				return 0
		for kk in range(n):
			if k == kk:
				pass
			elif addressesof(arglist[k],arglist[kk]) != []:
				return 0
	return 2  

def could_matches(form, formlist, givars,modpair=[]):
	matches = []
	xmatch = []
#		firstpair = schematch[form[1]][0] and u,v = firstpair
#    v = schematch[form[1]][0][1] 
	if type(form) is list  and form[0][0] in [42,43] and\
      form[1] in schematch.keys() and synt.cmop(schematch[form[1]][0][1]):
		firstpair = schematch[form[1]][0] 
		u,v = firstpair
		modpair = [form[2:],u[2:]]
		prexmatch = []
		for k in range(1,len(v),2):
			submatches = []
			for kk in range(len(formlist)):
				if couldmatch(form,formlist[kk],k,modpair):
					submatches.append(kk)	
			prexmatch.append([k,form,submatches])
#		print "prexmatch = "
#		synt.pprint(prexmatch)
		b = buildandmatches(formlist,prexmatch,v)
#		print "buildandmatches = ",b
		xmatch.extend(b)
	else:
		for y in formlist:
			if couldmatch(form,y,[],modpair):
				xmatch.append(y)
			elif type(y) is list  and y[0][0] in [42,43] and\
      y[1] in schematch.keys() and synt.cmop(schematch[y[1]][0][1]):
				for kk in range(1,len(schematch[y[1]][0][1]),2):
					if couldmatch(form,schematch[y[1]][0][1][kk],[],modpair):
						xmatch.append(0)					
						xmatch.append(0)					
	if 0 not in xmatch:
#		print "xmatch = ", xmatch
		matches.append(['f', form, xmatch])
	return xmatch

def bvcould_match(x,y,u,v):
	return couldmatch(y,v,keyvars = x[2:],keyvalues=u[2:])

def couldmatches(formsj, instancesj, modpair = [],keyvars=[],keyvalues=[]):
	matches = []
	for x in formsj:
		xmatch = []
#			firstpair = schematch[x[1]][0] and u,v = firstpair
#     v = schematch[x[1]][0][1] 
		if type(x) is list  and x[0][0] in [42,43] and\
       x[1] in schematch.keys() and synt.cmop(schematch[x[1]][0][1]):
			firstpair = schematch[x[1]][0] 
			u,v = firstpair
			modpair = [x[2:],u[2:]]
			prexmatch = []
			for k in range(1,len(v),2):
				submatches = []
#				raise "Count this A"
				for kk in range(len(instancesj)):
					if couldmatch(x,instancesj[kk],k,modpair,keyvars,keyvalues):
						submatches.append(kk)	
				prexmatch.append([k,x,submatches])
#			print "prexmatch = "
#			synt.pprint(prexmatch)
			b = buildandmatches(instancesj,prexmatch,v)
#			print "buildandmatches = ",b
			xmatch.extend(b)
		else:
			for y in instancesj:
				if couldmatch(x,y,[],modpair,keyvars,keyvalues):
					xmatch.append(y)
				elif type(y) is list  and y[0][0] in [42,43] and\
       y[1] in schematch.keys() and synt.cmop(schematch[y[1]][0][1]):
#					raise "Count this B"
					for kk in range(1,len(schematch[y[1]][0][1]),2):
						if couldmatch(x,schematch[y[1]][0][1][kk],[],modpair,keyvars,keyvalues):
							xmatch.append(0)					
		if 0 not in xmatch:
#			print "xmatch = ", xmatch
			matches.append(['f', x, xmatch])
	for y in instancesj:
		ymatch = []
#			firstpair = schematch[x[1]][0] and u,v = firstpair
#     v = schematch[x[1]][0][1] 
		if type(y) is list  and y[0][0] in [42,43] and\
       y[1] in schematch.keys() and synt.cmop(schematch[y[1]][0][1]):
			firstpair = schematch[y[1]][0] 
			u,v = firstpair
			preymatch = []
			for k in range(1,len(v),2):
				submatches = []
#				raise "Count this C"
				for kk in range(len(formsj)):
					if couldmatch(formsj[kk],y,k,modpair,keyvars,keyvalues):
						submatches.append(kk)	
				preymatch.append([k,x,submatches])
#			print "preymatch = "
#			synt.pprint(preymatch)
			b = buildandmatches(formsj,preymatch,v)
#			print "buildandmatches = ",b
			ymatch.extend(b)
		else:
			for x in formsj:
#				print "x = ",x
#				print "y = ",y
				if couldmatch(x,y,[],modpair,keyvars,keyvalues):
					ymatch.append(x)
				elif type(x) is list  and x[0][0] in [42,43] and\
       x[1] in schematch.keys() and synt.cmop(schematch[x[1]][0][1]):
#					raise "Count this D"
					for kk in range(1,len(schematch[x[1]][0][1]),2):
#						print "kk = ", kk
#						print "schematch[x[1]][0][1][kk] = ", schematch[x[1]][0][1][kk]
						if couldmatch(schematch[x[1]][0][1][kk],y,[],modpair,keyvars,keyvalues):
							ymatch.append(0)					
		if 0 not in ymatch:
#			print "ymatch = ", ymatch
			matches.append(['i',y,ymatch])
	return matches

def couldmatch(form1,form2,sfm1=[],modpair=[],keyvars=[],keyvalues=[]):
#	print "entering couldmatch with:"
#	print "modpair =", modpair 

#	print "form1 =", form1
#	print "form2 =", form2
	if form1 in keyvars:
		form1 = keyvalues[keyvars.index(form1)]
	if form1 == form2:
		return 1
	if form1 in subst.keys():
		form1 = subst[form1]
	if form2 in subst.keys():
		form2 = subst[form2]
	if form1 == form2:
		return 1
	if type(form1) is list  and form1[0][0] in [42,43]:
		if form1[1] in givenvars:
			pass
		elif form1[1] in subst.keys():
			w = subst[form1[1]]
			form1 = schemsubst(w,form1)
		elif form1[1] in schematch.keys():
			if dbvlistp(form1[2:]) == 1:
				localbvcond = []
				for k in range(2,len(form1)):
 					localbvcond.append([addressesof(form1[k],form2,[]), k - 2 ])
# 					# Slot 0 is the tag, slot 1 the schemator.	
				conj = makeconj(localbvcond)
				w = makesubst(form1, form2, conj) 
				if w == 0: return 0

				chkform = [[100,1]]
				chkinst = [[100,1]]
					
				for x,y in schematch[form1[1]]:
					if sfm1:
						chkform.append(schemsubst(w,x))
						chkinst.append(y[sfm1])
					else:
						chkform.append(schemsubst(w,x))
						chkinst.append(y)
#				print "form1[1] =",form1[1]
#				print "chkform ="
#				synt.pprint(chkform)
#				print "modpair = " , modpair
#				print "chkinst ="
#				synt.pprint(chkinst)
				return couldmatch(chkform, chkinst,[],modpair,keyvars,keyvalues)
			else:
				return 1
		else:
			return 1
	if type(form2) is list  and form2[0][0] in [42,43]:
		if form2[1] in givenvars:
			pass
		elif form2[1] in subst.keys():
			w = subst[form2[1]]
			form2 = schemsubst(w, form2)

		elif form2[1] in schematch.keys():
			allbound = 1
			for arg in form2[2:]:
				if type(arg) is str  \
          and pattern.bvar.match(arg):
					pass
				else:
					allbound = 0
			if allbound:

				localbvcond = []
				for k in range(2,len(form2)):
 					localbvcond.append([
            addressesof(form2[k],form1,[]), k - 2 ])
# 					# Slot 0 is the tag, slot 1 the schemator.	
				conj = makeconj( localbvcond)
				w = makesubst(form2, form1, conj) 
				if w == 0: return 0

				chkform = [[100,1]]
				chkinst = [[100,2]]
				for x,y in schematch[form2[1]]:
					chkform.append(schemsubst(w,x))
					chkinst.append(y)
				return couldmatch(chkform, chkinst,[],modpair,keyvars,keyvalues)
			else:
				return 1
		else:
			return 1
	if form1 == form2:
		return 1
	if form1 in givenvars and form2 in givenvars:
		return 0 
	if type(form1) is str :
		if form1 in givenvars or synt.symtype(form1) not in [10,11]: 
			if form2 in givenvars:
				return 0
			if type(form2) is list :
				return 0
			if synt.symtype(form2) not in [10,11]:
				return 0
	if type(form2) is str :
		if form2 in givenvars or synt.symtype(form2)not in [10,11]:
			if form1 in givenvars:
				return 0
			if type(form1) is list :
				return 0
			if synt.symtype(form1) not in [10,11]:
				return 0
	if type(form1) is list  or type(form2) is list : 
		if type(form1) is str :
			if synt.symtype(form1) not in [10,11]:
					return 0
			if form1 in givenvars:
					return 0
		elif type(form2) is str :
			if synt.symtype(form2) not in [10,11]:
					return 0
			if form2 in givenvars:
					return 0
		else:
			if form1[0] != form2[0]:
				return 0
			if synt.cmop(form1):
				forms1 = conjuncts(form1)
				forms2 = conjuncts(form2)
				wi1 = wildcardindices(forms1)
				wi2 = wildcardindices(forms2)
				nw1 = len(wi1)
				nw2 = len(wi2)
				if nw1 == nw2 == 0 and conjlen(forms1) != conjlen(forms2):
					return 0
				matches = couldmatches(forms1,forms2,modpair,keyvars,keyvalues)
				savematch = matches[0]
				matchnum = 10000 
				if nw1 == nw2 == 0:
					for match in matches:
						if len(match[2]) < matchnum: 
							savematch = match
							matchnum = len(match[2])
				elif nw2 == 0:
					for match in matches:
						if match[0] == 'f' and len(match[2]) < matchnum:
							savematch = match
							matchnum = len(match[2])
				elif nw1 == 0:
					for match in matches:
						if match[0] == 'i' and len(match[2]) < matchnum:
							savematch = match
							matchnum = len(match[2])
				if matchnum == 0:
					return 0
				return 1
#
			if len(form1) != len(form2):
				return 0
			fbvlist = synt.indvlist(form1)
			ibvlist = synt.indvlist(form2)
			if len(fbvlist) != len(ibvlist):
				return 0
			nlist = newbvlist(len(fbvlist))
			form1 = synt.indvsubst(nlist, fbvlist, form1)
			form2 = synt.indvsubst(nlist, ibvlist,form2)
			for i in range(1,len(form1)):
				if couldmatch(form1[i],form2[i],[],modpair,keyvars,keyvalues) == 0:
#					print "form1[",i,"] = ", form1[i]
#					print "form2[",i,"] = ", form2[i]
#					print 6464646
					return 0
	elif synt.symtype(form1) not in [10,11] and synt.symtype(form2) not in [10,11]:
			return 0
	elif synt.symtype(form1) in [10,11] and pattern.bvar.match(form1) and\
not(modpair and form1 in modpair[0]): 
		return 0 
	elif synt.symtype(form1) in [10,11] and  nbbvarlist(form2,modpair):
		return 0 
	elif synt.symtype(form2) in [10,11] and pattern.bvar.match(form2) and\
not(modpair and form2 in modpair[0]): 
		return 0 
	elif synt.symtype(form2) in [10,11] and  nbbvarlist(form1,modpair):
		return 0 
	return 1

def buildandmatches(instancesj,pmatch,andform):
	return map(lambda chlist :buildandmatch(instancesj,chlist,andform),indexchoices(pmatch))
		
def indexchoices(pmatch):
	if pmatch == []:return [[]]
	headmatch = pmatch[0]
	tailmatches = indexchoices(pmatch[1:])
	retlist = []
	for j in headmatch[2]:
		for t in tailmatches:
			for u in t:
				if u[1] == j:
					break
			else:
				retlist.append(t + [[headmatch[0],j]])
	return retlist	

def buildandmatch(instancesj,choicelist,andform):
	retmatch = [andform[0],instancesj[choicelist[0][1]]]
	for c,d in choicelist[1:]:
		retmatch.append(andform[2])
		retmatch.append(instancesj[d])
#	print "single and match"
#	synt.pprint(retmatch)
	return retmatch

def conjuncts(andform):
	andop = andform[2]
	substdomain = subst.keys()
	forms = []
	for i in range(1,len(andform),2): 
		if andform[i] in substdomain:
			formsi = subst[andform[i]]
			if type(formsi) is list  and \
	 			len(formsi[0]) > 2 and formsi[0][2] == -1 and \
				andop == formsi[2]:
				for ii in range(1, len(formsi), 2):
					forms.append(formsi[ii])
			else:
				forms.append(formsi)
		else:
			forms.append(andform[i])
	return forms

def newconjunction(oldform, newconjuncts):
	if len(newconjuncts) == 1:
		return newconjuncts[0]
#	print "oldform = ", oldform
#	print "newconjuncts= ", 
	newform = [oldform[0],newconjuncts[0]]
	for i in range(1,len(newconjuncts)):
		newform.append(oldform[2])
		newform.append(newconjuncts[i])
	return newform

def addressesof(var, exp,address = []):
	if type(var) is str :
		if var == exp:
			return [address]
		if type(exp) is str :
			return []
		retlist = []
		for i in range(1, len(exp)):
			retlist = retlist + addressesof(var,exp[i],address+[i])
		return retlist
	elif couldmatch(var, exp) != 0:
		return [address]
	elif type(exp) is str :
		return []
	retlist = []
	for i in range(1, len(exp)):
		retlist = retlist + addressesof(var,exp[i],address+[i])
	return retlist
	
def makesubst(schemform, instance, condition,bvlist = []):
#	print "condition = ",condition
	if bvlist == []:
		bvlist = schemform[2:]
	sbval = subval(instance,condition,bvlist)
	nb = synt.nblist(sbval,bvlist)
	r = shadow_extend(schemform[1], nb)
	if r == 0 :return 0
# 	shadow[schemform[1]] = [[schemform[1]]]
	for x in synt.nblist(sbval,bvlist):
#		print "x3 = ", x
#		print "schemform = ", schemform
		if pattern.bvar.match(x):
			return 0
#		if x == schemform[1]:
#				return 0
#
#New stuff starts here:
#		for y in shadow:
#			if schemform[1] in shadow[y]:
#				if x in shadow[y][0]:
#					return 0
#				elif x not in shadow[y]:
#					shadow[y].append(x)
#			elif y == x:
#				for z in shadow[y][1:]:
#					if z in shadow[schemform[1]][0]:
#						return 0
#					elif z not in shadow[schemform[1]]:
#						shadow[schemform[1]].append(z)
#New stuff ends here

	retschem = schemform[:2] + bvlist
	return [retschem, sbval]


def makeshadow(w):
	retlist = []
	nbl = synt.nblist(w[1])
	for x in nbl:
		if x not in retlist and x not in w[0][2:]:
			retlist.append(x)
	return [[w[0][1]]] + retlist

def newbvlist(n):
	global bvarnum
	r = []	
	for x in range(n):
		bvarnum = bvarnum + 1
		r.append('z_{' + ("%d" % bvarnum) + '}')
	return r
	
def subval(exp, choiceconj, bvlist):
	if choiceconj == []:
		return exp
	for x,j in choiceconj:
		if x == []:
			return bvlist[j]
	if type(exp) is str :
		print "exp = ", exp
		print "choiceconj = ", choiceconj
		print "bvlist = ", bvlist
		raise "exp is not a list" 
	retlist = [exp[0]]
	for i in range(1, len(exp)):
		for x,j in choiceconj:
			if x == [i]:
				retlist.append(bvlist[j])
				break
		else:
			y = []
			for z,k in choiceconj:
				if z[0] == i:
					y.append([z[1:],k])	
			retlist.append(subval(exp[i],y,bvlist))
	return retlist
		
def schemsubst(sub, exp):
# Adopt form for sub [schemform , tform]
# Assume that any bound variables in schemform have
# been refreshed.  Bad Assumption!!  Do the work here.
	schemform = sub[0]
	tform = sub[1]
	nflist = synt.nfvlist(tform)
	nblist = synt.nblist(exp)
	for x in nblist:
		if x in nflist:
			tform = synt.bvarreplace(tform, newbvlist(len(nflist)))
			break
	if type(exp) is str :
		return exp
	if exp[1] == schemform[1]: 
		return schemsubstaux(schemform[2:],exp[2:],tform)
	retlist = [exp[0]]
	for x in exp[1:]:
		retlist.append(schemsubst([schemform, tform],x))
	return retlist

def schemsubstaux(outvars,inlist,exp):
	if exp in outvars: 
		v = outvars.index(exp)
		return inlist[v]
	if type(exp) is str :
		return exp
	retlist = [exp[0]]
	for x in exp[1:]:
		retlist.append(schemsubstaux(outvars,inlist,x))
	return retlist

def makeconj(slicelist):
	choiceconj = []
	for x,i in slicelist:
		for y in x:
			choiceconj.append([y,i])
	return choiceconj

def inline(treeadda, treeaddb):
	if len(treeadda) <= len(treeaddb):
		return treeaddb[:len(treeadda)] == treeadda
	else:
		return treeadda[:len(treeaddb)] == treeaddb


def subst(inlist,outlist,pexp): 
	""" Indiscriminate string substitution """
#	print "subst pexp = ", pexp
	if type(pexp) is list :
		r = []
		for t in pexp:
			r.append(subst(inlist,outlist,t))
		return r
	elif type(pexp) is str :
		if pexp in outlist:
			return inlist[outlist.index(pexp)]
		else:
			return pexp
	else:  #Numbers don't get trashed
		return pexp

def nbbvarlist(form,mp):
	if mp :
		exceptions = mp[0]
	else:
		exceptions = []
	nb = synt.nblist(form)
	retlist = []
	for x in nb:
		if pattern.bvar.match(x)and x not in exceptions:
			retlist.append(x)
	return retlist

def wildcardindices(formlist):
	retlist = []
	for k in range(len(formlist)):
		if wildcardp(formlist[k]):
			retlist.append(k)
	return retlist 

def wildcardp(x):
	if type(x) is str :
		if x in subst.keys(): 
			print "x = ", x
			print "subst[x] = ", subst[x]
			return wildcardp(subst[x])
		elif x in givenvars:
			return 0
		elif synt.symtype(x) in [10,11]:
			return 1
		else:
			return 0
	elif type(x) is list :
		if synt.cmop(x):
			for k in range(1,len(x),2):
				if wildcardp(x[k] ):
					return 1
			return 0
		elif x[0][0] in [42,43]:
			if x[1] in givenvars:
				return 0
#			elif x[1] in schematch.keys():
#				return 1
#				return wildcardp(schematch[x[1]][0][1]) 
			else:
				return 1
		else:
			return 0
	else:
		raise "Error in the parser"
	
def odds(list):
	retlist = []
	for k in range(1,len(list),2):
		retlist.append(list[k])
	return retlist

def comparison_key(schemexp1, schemexp2):
	boundslots = []
	compslots = []
	for k in range(2,len(schemexp1)):
		if pattern.bvar.match(schemexp1[k]):
			boundslots.append(k)
		elif nbbvarlist(schemexp1[k],[]):
			return 0
		if schemexp1[k] != schemexp2[k]:
			if k not in boundslots:
				compslots.append(k)
	if len(compslots) < 2:
		return [compslots, boundslots]
	else:
		return 0

def pairoff(conja, conjb):
	formsj = conja[:]
	instancesj = conjb[:]
	matches = []
	for x in formsj:
		xmatch = [] 
		for y in instancesj:
			if couldmatch(x,y):
				xmatch.append(y)
		matches.append(['f',x,xmatch])
	for y in instancesj:
		ymatch = []
		for x in formsj:
			if couldmatch(x,y):
				ymatch.append(x)
		matches.append(['i',y,ymatch])

	formsjp = []
	instancesjp = []
	while formsj:
		nextmatch = matches[0]
		matchnum = 1000 
		for match in matches:
			if 0 < len(match[2]) <  matchnum:
				nextmatch = match
				matchnum = len(nextmatch[2])
		if matchnum == 1000: break
		matches.remove(nextmatch)
		if nextmatch[0] == 'f':
			for matchp in matches:
				if matchp[0] == 'f' and nextmatch[2][0] in matchp[2]:
					matchp[2].remove(nextmatch[2][0])
			for matchp in matches:
				if matchp[0] == 'i' and matchp[1] == nextmatch[2][0]:
					break
			matches.remove(matchp)
			for matchp in matches:
				if matchp[0] == 'i' and matchp[1] == nextmatch[2][0]:
					matchp[2].remove(nextmatch[1])
			formsj.remove(nextmatch[1])
			instancesj.remove(nextmatch[2][0])
			formsjp.append(nextmatch[1])
			instancesjp.append(nextmatch[2][0])
		else:#if nextmatch[0] == 'i':
			for matchp in matches:
				if matchp[0] == 'i' and nextmatch[2][0] in matchp[2]:
					matchp[2].remove(nextmatch[2][0])
			for matchp in matches:
				if matchp[0] == 'f' and matchp[1] == nextmatch[2][0]:
					break
			matches.remove(matchp)
			for matchp in matches:
				if matchp[0] == 'f' and matchp[1] == nextmatch[2][0]:
					matchp[2].remove(nextmatch[1])
			instancesj.remove(nextmatch[1])
			instancesjp.append(nextmatch[1])
			formsj.remove(nextmatch[2][0])
			formsjp.append(nextmatch[2][0])
	return formsjp

def newgroundlist():
#	retlist = groundedvars[:]
	retlist = givenvars[:]
	done = False 
	while not done:
		done = True 
		for v in shadow:
			if v in retlist:
				continue
			if len(shadow[v]) > 1:
				for x in shadow[v][1:]:
					if x not in retlist:
						break
				else:
					done = False
					for y in shadow[v][0]:
						if y not in retlist:
							retlist.append(y)
					continue
			for w in shadow[v][0]:
				if w in retlist:
					for z in shadow[v][0]:
						if z not in retlist:
							retlist.append(z)
					done = False 
	return retlist
					
	

def groundtermp(term):
	for x in synt.nblist(term):
		if pattern.bvar.match(x):
			pass
		elif x not in groundedvars:
			return False
	return True

def stepreduce(x):
	if x in subst.keys():
		return subst[x]
	if type(x) is list  and x[0][0] in [42,43] and x[1] in subst.keys():
		return schemsubst(subst[x[1]], x)
	if x in shadow.keys():
		return shadow[x][0][0]
	return x

def groundeddiffaddresslist(expa,expb,skipaddresses,address=[]):
#	print "expa = ", expa
#	print "expb = ", expb
#	print "address = ", address
# Return a list of addresses of irreconcileable locations. 
	if expa == expb:
		return []
#	if couldmatch(terma, expa) and couldmatch(termb,expb):
#		return [address]
#	print "YYY"
	expa = stepreduce(expa)
	expb = stepreduce(expb)
	if expa == expb:
		return []
#	if couldmatch(terma, expa) and couldmatch(termb,expb):
#		return [address]
#	if groundtermp(expa) and groundtermp(expb):
#		return [address]
	if type(expa) is str and type(expb) is str:
		if groundtermp(expa) and groundtermp(expb):
			return [address]
		else:
			return 0
	if type(expa) is str  or type(expb) is str :
		return []
#		if type(expa) is str  and\
#           synt.symtype(expa) in [10,11] and expa not in givenvars: 
#			return [[],[[expa,expb]]]
#		elif type(expb) is str  and\
#           synt.symtype(expb) in [10,11] and expb not in givenvars: 
#			return [[],[[expa,expb]]]
#		else:
#			return 0
	if len(expa) != len(expb) or expa[0] != expb[0]:
		return [address]
	if '' != synt.cmop(expa) == synt.cmop(expb):
		return []
	fbvlist = synt.indvlist(expa)
	ibvlist = synt.indvlist(expb)
	if len(fbvlist) != len(ibvlist):
		return [address]
	n = len(expa)
	retadlist = []
	nlist = newbvlist(len(fbvlist))
	expa = synt.indvsubst(nlist, fbvlist, expa)
	expb = synt.indvsubst(nlist, ibvlist, expb)
	for k in range(1,n):
		nextad = address + [k]
		if nextad in skipaddresses:
			continue
		r = groundeddiffaddresslist(expa[k],expb[k],skipaddresses,nextad)
		retadlist.extend(r)
	return retadlist

def diffaddresslist(terma,termb,expa,expb,skipaddresses,address=[]):
#	print "terma = ", terma
#	print "termb = ", termb
#	print "expa = ", expa
#	print "expb = ", expb
#	print "address = ", address
# Return a list of addresses and a list of matches. [addresslist, matchlist]
	if expa == expb:
		return [[],[]]
	if couldmatch(terma, expa) and couldmatch(termb,expb):
		return [[address],[ [terma, expa], [termb, expb] ]]
	terma = stepreduce(terma)
	termb = stepreduce(termb)
	expa = stepreduce(expa)
	expb = stepreduce(expb)
	if expa == expb:
		return [[],[]]
	if couldmatch(terma, expa) and couldmatch(termb,expb):
		return [[address],[]]
	if type(expa) is str  or type(expb) is str :
		if type(expa) is str  and\
           synt.symtype(expa) in [10,11] and expa not in givenvars: 
			return [[],[[expa,expb]]]
		elif type(expb) is str  and\
           synt.symtype(expb) in [10,11] and expb not in givenvars: 
			return [[],[[expa,expb]]]
		else:
			return 0
	if len(expa) != len(expb) or expa[0] != expb[0]:
		return 0
	n = len(expa)
	retadlist = []
	retmatchlist = []
	if '' != synt.cmop(expa) == synt.cmop(expb):
		reorder_expb = []
		for k in range(1,n,2):
			nextad = address + [k]
			if nextad in skipaddresses:
				continue
			for kk in range(1,n,2):
				if kk in reorder_expb:
					continue
				elif expa[k] == expb[kk]:			
					reorder_expb.append(kk)
					break
				r = diffaddresslist(terma,termb,expa[k],expb[kk],skipaddresses,nextad)
				if r != 0:
					reorder_expb.append(kk)
					retadlist.extend(r[0])
					retmatchlist.extend(r[1])
					break
			else:
				return 0
#		print "retadlist = ", retadlist
#		print "retmatchlist = ", retmatchlist
		return [retadlist, retmatchlist] 
	fbvlist = synt.indvlist(expa)
	ibvlist = synt.indvlist(expb)
	if len(fbvlist) != len(ibvlist):
		return 0
	nlist = newbvlist(len(fbvlist))
	expa = synt.indvsubst(nlist, fbvlist, expa)
	expb = synt.indvsubst(nlist, ibvlist, expb)
	for k in range(1,n):
		nextad = address + [k]
		if nextad in skipaddresses:
			continue
		r = diffaddresslist(terma,termb,expa[k],expb[k],skipaddresses,nextad)
		if r == 0:
			return 0
		retadlist.extend(r[0])
		retmatchlist.extend(r[1])
	return [retadlist, retmatchlist] 
	
def onediffaddresslist(expa,expb,skipaddresses=[],address=[]):
# Return a list of addresses and a required match. [addresslist, match]
	if expa == expb:
		return [[],[]]
	if type(expa) is str  or type(expb) is str :
		return [[address],[expa,expb]]
	if len(expa) != len(expb) or expa[0] != expb[0]:
		return [[address],[expa,expb]]
	n = len(expa)
	retadlist = []
	retmatch = []
# Might need to replace index variables here.
	for k in range(1,n):
		nextad = address + [k]
		if nextad in skipaddresses:
			continue
		d = onediffaddresslist(expa[k],expb[k],skipaddresses,nextad)
		if retmatch == []:
			retadlist = d[0]
			retmatch = d[1]
		elif d[0] == []:
			pass
		elif d[1] == retmatch:
			retadlist.extend(d[0])
		else: 
			return [[address],[expa,expb]]
	return [retadlist, retmatch]
						
def groundeq(a,b):
	if a == b : return 1
	if a in subst.keys():
		a = subst[a]
	if b in subst.keys():
		b = subst[b]
	if a in shadow.keys() and b in shadow.keys():
		return shadow[a] is shadow[b]
	if a == b: return 1
	if type(a) is str :
		return 0
	if type(b) is str :
		return 0
	if a[0][0] in [42,43] and a[1] in subst.keys():
		a = schemsubst(subst[a[1]],a)
	if b[0][0] in [42,43] and b[1] in subst.keys():
		b = schemsubst(subst[b[1]],b)
	if a == b: return 1
	if type(a) is str :
		return 0
	if type(b) is str :
		return 0
	if len(a) != len(b):
		return 0
	for k in range(1,len(a)):
		if not groundeq(a[k],b[k]):
			return 0
	return 1

def makebvmap(oldschemform, newschemform,retmap):
	""" retmap is a dictionary modified so as to return
	the bvmap.  If this is impossible makebvmap returns 1 """
	if type(oldschemform) is str :
		if pattern.bvar.match(oldschemform):
			if oldschemform in retmap.keys():
				if newschemform != retmap[oldschemform]:
					return 1
			elif pattern.bvar.match(newschemform):
				if newschemform in retmap.values():
					return 1
				else:
					retmap[oldschemform] = newschemform
			else:
				return 1 
		elif oldschemform != newschemform:
			return 1
	elif type(newschemform) is str :
			return 1
	elif len(oldschemform) != len(newschemform):
		return 1
	elif oldschemform[0] != newschemform[0]:
		return 1
	else:
		for k in range(1,len(oldschemform)):
			r = makebvmap(oldschemform[k],newschemform[k],retmap) 
			if r: return r 

				
def revarmatches(oldmatch, newschemform):
	bvmap = {}
	if makebvmap(oldmatch[0], newschemform,bvmap):
		return 0
	return synt.subst(bvmap.values(),bvmap.keys(),oldmatch[1])

