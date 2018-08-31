import numpy as np
import copy
from mygrid.grid import Section,TransformerModel, Auto_TransformerModel
import pandas as pd
"""
This scripts allows the user to calculate the unbalanced short-circuits on radial distribution
systems modeled on mygrid.

"""


def biphasic(distgrid, node_name, fs='Higher',Df=False, zc=0+0j):
	"""
	Calculates the two-phase short circuit

	Parameters
	----------
	distgrid: mygrid.grid.DistGrid

	node_name: str
		The name of node fault
	fs: str
		Designates which phases participate in the short circuit
		Options: 'Iab', 'Iac', 'Ibc' and 'Higher'.
	Df: bool
		Indicates whether the function returns a dataframe or a dictionary.
		If true the function returns a DataFrame.
	zc: complex
		Contact Impedance
	Returns:
	Dict or a DataFrame
	"""
	zz=dict()
	zus,zpus=upstream_area(distgrid, node_name)
	zds,zpds=downstream_area(distgrid, node_name)
	Xab=np.zeros((3,1), dtype=complex)
	Xac=np.zeros((3,1), dtype=complex)
	Xbc=np.zeros((3,1), dtype=complex)
	voltage_source=voltage(distgrid,node_name)
	zz.update(zpus)
	zz.update(zpds)
	l=0+0j
	for i in [zds, zus]:
		if type(i) != type(None):
			l += np.linalg.inv(i)
	l=np.linalg.inv(l)+zc
	C=calc_c(l)
	Cab=copy.copy(C)
	Cac=copy.copy(C)
	Cbc=copy.copy(C)

	Cab[3,3]=Cab[4,4]=1
	Cab[6,0]=Cab[6,1]=Cab[5,2]=1

	Cac[3,3]=Cac[5,5]=1
	Cac[6,0]=Cac[6,2]=Cac[4,1]=1

	Cbc[4,4]=Cbc[5,5]=1
	Cbc[6,1]=Cbc[6,2]=Cbc[3,0]=1

	IPS=np.zeros((7,1),dtype=complex)
	IPS[0:3,0:1]=np.linalg.inv(l).dot(voltage_source)
	Xab +=np.linalg.inv(Cab).dot(IPS)[0:3]
	Xac +=np.linalg.inv(Cac).dot(IPS)[0:3]
	Xbc +=np.linalg.inv(Cbc).dot(IPS)[0:3]

	If={'Fab': {'Ifa':Xab[0,0],'Ifb':Xab[1,0],'Ifc':Xab[2,0]},
		'Fac': {'Ifa':Xac[0,0],'Ifb':Xac[1,0],'Ifc':Xac[2,0]},
		'Fbc': {'Ifa':Xbc[0,0],'Ifb':Xbc[1,0],'Ifc':Xbc[2,0]}}

	If=pd.DataFrame(If)
	erase=None
	if fs =='Higher':
		fs=If.abs().max().idxmax()

	if fs=='Fac':
		Iz=If['Fac']
		erase=[1]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid,ep=erase)
	elif fs=='Fab':
		Iz=If['Fab']
		erase=[2]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid,ep=erase)
	elif fs == 'Fbc':
		Iz=If['Fbc']
		erase=[0]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid,ep=erase)


	if Df:
		ict=dict_to_DataFrame(ict)

	return ict

def biphasic_to_ground(distgrid,node_name, fs='Higher',Df=False, zc=0+0j):
	"""
	Calculates the two-phase-grounded short circuit

	Parameters
	----------
	distgrid: mygrid.grid.DistGrid

	node_name: str
		The name of node fault
	fs: str
		Designates which phases participate in the short circuit
		Options: 'Iab', 'Iac', 'Ibc' and 'Higher'.
	Df: bool
		Indicates whether the function returns a dataframe or a dictionary.
		If true the function returns a DataFrame.
	zc: complex
		Contact Impedance
	Returns:
	Dict or a DataFrame
	"""
	zz=dict()
	zus,zpus=upstream_area(distgrid, node_name)
	zds,zpds=downstream_area(distgrid, node_name)
	zz.update(zpus)
	zz.update(zpds)

	Xab=np.zeros((3,1), dtype=complex)
	Xac=np.zeros((3,1), dtype=complex)
	Xbc=np.zeros((3,1), dtype=complex)
	voltage_source=voltage(distgrid,node_name)

	l=0+0j
	for i in [zds, zus]:
		if type(i) != type(None):
			l += np.linalg.inv(i)
	l=np.linalg.inv(l)+zc

	C=calc_c(l)
	Cab=copy.copy(C)
	Cac=copy.copy(C)
	Cbc=copy.copy(C)

	Cab[3,3]=Cab[4,4]=Cab[6,6]=1
	Cab[5,2]=1

	Cac[3,3]=Cac[5,5]=Cac[6,6]=1
	Cac[4,1]=1

	Cbc[4,4]=Cbc[5,5]=Cbc[6,6]=1
	Cbc[3,0]=1

	IPS=np.zeros((7,1),dtype=complex)
	IPS[0:3,0:1]=np.linalg.inv(l).dot(voltage_source)

	Xab +=np.linalg.inv(Cab).dot(IPS)[0:3]
	Xac +=np.linalg.inv(Cac).dot(IPS)[0:3]
	Xbc +=np.linalg.inv(Cbc).dot(IPS)[0:3]

	If={'Fabg': {'Ifa':Xab[0,0],'Ifb':Xab[1,0],'Ifc':Xab[2,0]},
		'Facg': {'Ifa':Xac[0,0],'Ifb':Xac[1,0],'Ifc':Xac[2,0]},
		'Fbcg': {'Ifa':Xbc[0,0],'Ifb':Xbc[1,0],'Ifc':Xbc[2,0]}}
	If=pd.DataFrame(If)

	if fs =='Higher':
		fs=If.abs().max().idxmax()

	if fs=='Facg':
		Iz=If['Facg']
		erase=[1]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid,ep=erase)
	elif fs=='Fabg':
		Iz=If['Fabg']
		erase=[2]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid,ep=erase)
	elif fs == 'Fbcg':
		Iz=If['Fbcg']
		erase=[0]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid,ep=erase)

	if Df:
		ict=dict_to_DataFrame(ict)

	return ict
def three_phase_to_ground(distgrid,node_name,Df=False, zc=0+0j):
	"""
	Calculates the three-phase-grounded short circuit

	Parameters
	----------
	distgrid: mygrid.grid.DistGrid

	node_name: str
		The name of node fault
	fs: str
		Designates which phases participate in the short circuit
		Options: 'Iab', 'Iac', 'Ibc' and 'Higher'.
	Df: bool
		Indicates whether the function returns a dataframe or a dictionary.
		If true the function returns a DataFrame.
	zc: complex
		Contact Impedance
	Returns:
	Dict or a DataFrame
	"""
	zz=dict()
	zus,zpus=upstream_area(distgrid, node_name)
	zds, zpds=downstream_area(distgrid, node_name)
	zz.update(zpus)
	zz.update(zpds)
	X=np.zeros((3,1), dtype=complex)
	voltage_source=voltage(distgrid,node_name)

	l=0+0j
	for i in [zds, zus]:
		if type(i) != type(None):
			l += np.linalg.inv(i)
	l=np.linalg.inv(l)+zc

	C=calc_c(l)
	C[3,3]=C[4,4]=C[5,5]=C[6,6]=1
	IPS=np.zeros((7,1),dtype=complex)
	IPS[0:3,0:1]=np.linalg.inv(l).dot(voltage_source)

	X +=np.linalg.inv(C).dot(IPS)[0:3]
	If={'Fabcg': {'Ifa':X[0,0],'Ifb':X[1,0],'Ifc':X[2,0]}}
	If=pd.DataFrame(If)
	ict=calc_contributions(zz,np.array(If).reshape(3,1),node_name,distgrid, ep=[])
	if Df:
		ict=dict_to_DataFrame(ict)
	return ict

def three_phase(distgrid,node_name,Df=False,  zc=0+0j):
	"""
	Calculates the three-phase short circuit

	Parameters
	----------
	distgrid: mygrid.grid.DistGrid

	node_name: str
		The name of node fault
	Df: bool
		Indicates whether the function returns a dataframe or a dictionary.
		If true the function returns a DataFrame.
	zc: complex
		Contact Impedance
	Returns:
	Dict or a DataFrame
	"""
	zz=dict()
	zus,zpus=upstream_area(distgrid, node_name)
	zds,zpds=downstream_area(distgrid, node_name)
	zz.update(zpus)
	zz.update(zpds)

	X=np.zeros((3,1), dtype=complex)
	voltage_source=voltage(distgrid,node_name)

	l=0+0j
	for i in [zds, zus]:
		if type(i) != type(None):
			l += np.linalg.inv(i)
	l=np.linalg.inv(l)+zc
	C=calc_c(l)
	C[3,3]=C[4,4]=C[5,5]=1
	C[6,0]=C[6,1]=C[6,2]=1

	IPS=np.zeros((7,1),dtype=complex)
	IPS[0:3,0:1]=np.linalg.inv(l).dot(voltage_source)

	X +=np.linalg.inv(C).dot(IPS)[0:3]

	If={'Fabc': {'Ifa':X[0,0],'Ifb':X[1,0],'Ifc':X[2,0]}}

	If=pd.DataFrame(If)

	ict=calc_contributions(zz,np.array(If).reshape(3,1),node_name,distgrid,ep=[])

	if Df:
		ict=dict_to_DataFrame(ict)

	return ict

def mono_phase(distgrid,node_name,zf=0, fs='Higher',Df=False,  zc=0+0j):
	"""
	Calculates the mono-phase short circuit

	Parameters
	----------
	distgrid: mygrid.grid.DistGrid

	node_name: str
		The name of node fault
	fs: str
		Designates which phases participate in the short circuit
		Options: 'Ia', 'Ia', 'Ib' and 'Higher'.
	Df: bool
		Indicates whether the function returns a dataframe or a dictionary.
		If true the function returns a DataFrame.
	zc: complex
		Contact Impedance
	Returns:
	Dict or a DataFrame
	"""
	zz=dict()
	zus,zpus=upstream_area(distgrid, node_name)
	zds,zpds=downstream_area(distgrid, node_name)
	zz.update(zpus)
	zz.update(zpds)

	Xa=np.zeros((3,1), dtype=complex)
	Xb=np.zeros((3,1), dtype=complex)
	Xc=np.zeros((3,1), dtype=complex)
	voltage_source=voltage(distgrid,node_name)

	l=0+0j
	for i in [zds, zus]:
		if type(i) != type(None):
			l += np.linalg.inv(i)
	l=np.linalg.inv(l)+zc

	C=calc_c(l)
	Ca=copy.copy(C)
	Cb=copy.copy(C)
	Cc=copy.copy(C)

	Ca[3,3]=Ca[6,6]=1
	Ca[4,1]=Ca[5,2]=1

	Cb[4,4]=Cb[6,6]=1
	Cb[3,0]=Cb[5,2]=1

	Cc[5,5]=Cc[6,6]=1
	Cc[3,0]=Cc[4,1]=1

	IPS=np.zeros((7,1),dtype=complex)
	IPS[0:3,0:1]=np.linalg.inv(l).dot(voltage_source)

	Xa+=np.linalg.inv(Ca).dot(IPS)[0:3]
	Xb+=np.linalg.inv(Cb).dot(IPS)[0:3]
	Xc+=np.linalg.inv(Cc).dot(IPS)[0:3]

	If={'Fag': {'Ifa':Xa[0,0],'Ifb':Xa[1,0],'Ifc':Xa[2,0]},
		'Fbg': {'Ifa':Xb[0,0],'Ifb':Xb[1,0],'Ifc':Xb[2,0]},
		'Fcg': {'Ifa':Xc[0,0],'Ifb':Xc[1,0],'Ifc':Xc[2,0]}}

	If=pd.DataFrame(If)
	if fs =='Higher':
		fs=If.abs().max().idxmax()

	if fs=='Fag':
		Iz=If['Fag']
		erase=[1,2]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid,ep=erase)
	elif fs=='Fbg':
		Iz=If['Fbg']
		erase=[0,2]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid,ep=erase)
	elif fs == 'Fcg':
		Iz=If['Fcg']
		erase=[0,1]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid,ep=erase)

	if Df:
		ict=dict_to_DataFrame(ict)

	return ict

def min_mono_phase(distgrid,node_name,zf=0, zt=40, fs='Higher',Df=False,  zc=0+0j):
	"""
	Calculates the min-mono-phase short circuit

	Parameters
	----------
	distgrid: mygrid.grid.DistGrid

	node_name: str
		The name of node fault
	fs: str
		Designates which phases participate in the short circuit
		Options: 'Ia', 'Ia', 'Ib' and 'Higher'.
	Df: bool
		Indicates whether the function returns a dataframe or a dictionary.
		If true the function returns a DataFrame.
	zc: complex
		Contact Impedance
	Returns:
	Dict or a DataFrame
	"""
	zz=dict()
	zus,zpus=upstream_area(distgrid, node_name)
	zds,zpds=downstream_area(distgrid, node_name)
	zz.update(zpus)
	zz.update(zpds)

	Xa=np.zeros((3,1), dtype=complex)
	Xb=np.zeros((3,1), dtype=complex)
	Xc=np.zeros((3,1), dtype=complex)
	voltage_source=voltage(distgrid,node_name)

	l=0+0j
	for i in [zds, zus]:
		if type(i) != type(None):
			l += np.linalg.inv(i)
	l=np.linalg.inv(l+zc)
	C=calc_c(l+zt)
	Ca=copy.copy(C)
	Cb=copy.copy(C)
	Cc=copy.copy(C)

	Ca[3,3]=Ca[6,6]=1
	Ca[4,1]=Ca[5,2]=1

	Cb[4,4]=Cb[6,6]=1
	Cb[3,0]=Cb[5,2]=1

	Cc[5,5]=Cc[6,6]=1
	Cc[3,0]=Cc[4,1]=1

	IPS=np.zeros((7,1),dtype=complex)
	IPS[0:3,0:1]=np.linalg.inv(l).dot(voltage_source)

	Xa+=np.linalg.inv(Ca).dot(IPS)[0:3]
	Xb+=np.linalg.inv(Cb).dot(IPS)[0:3]
	Xc+=np.linalg.inv(Cc).dot(IPS)[0:3]

	If={'Fag_min': {'Ifa':Xa[0,0],'Ifb':Xa[1,0],'Ifc':Xa[2,0]},
		'Fbg_min': {'Ifa':Xb[0,0],'Ifb':Xb[1,0],'Ifc':Xb[2,0]},
		'Fcg_min': {'Ifa':Xc[0,0],'Ifb':Xc[1,0],'Ifc':Xc[2,0]}}

	If=pd.DataFrame(If)
	if fs =='Higher':
		fs=If.abs().max().idxmax()

	elif fs=='Fag_min':
		Iz=If['Fag_min']
		erase=[1,2]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid ,ep=erase)
	elif fs=='Fbg_min':
		Iz=If['Fbg_min']
		erase=[0,2]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid ,ep=erase)
	elif fs == 'Fcg_min':
		Iz=If['Fcg_min']
		erase=[1,0]

		ict=calc_contributions(zz,np.array(Iz).reshape(3,1),node_name,distgrid ,ep=erase)

	if Df:
		ict=dict_to_DataFrame(ict)

	return ict
def calc_c(l):

	C=np.zeros((7,7),dtype=complex)
	C[0,0]=C[1,1]=C[2,2]=1
	l=np.linalg.inv(l)
	C[0:3,3:6]=l
	C[0,6]=np.sum(l[0,0:3])
	C[1,6]=np.sum(l[1,0:3])
	C[2,6]=np.sum(l[2,0:3])

	return C



def voltage(distgrid,node_name):
	loads=distgrid.load_nodes
	loads_path=distgrid.load_nodes_tree.node_to_root_path(node_name)
	voltage_source=loads[distgrid.load_nodes_tree.root].vp


	i=len(loads_path[0,0:])-1
	while i >=1 :

		n1=loads[loads_path[1,i]]
		n2=loads[loads_path[1,i-1]]

		section=distgrid.sections_by_nodes[(n1,n2)]

		if isinstance(section.transformer, TransformerModel):

			voltage_source=section.A.dot(voltage_source)


		i-=1


	return voltage_source

def downstream_area(distgrid, node_name):
	tree=distgrid.load_nodes_tree.tree
	rnp=distgrid.load_nodes_tree.rnp.tolist()

	z, pp=resolve_downstream_area(distgrid, node_name, tree, rnp)

	return z,pp

def upstream_area(distgrid, node_name):
	tree=distgrid.load_nodes_tree.tree
	rnp=distgrid.load_nodes_tree.rnp.tolist()
	z, pp=resolve_upstream_area(distgrid, node_name, tree, rnp)
	return z,pp

def resolve_upstream_area(distgrid, n1, tree, rnp, nf=False):

	zpll=list()
	zp=dict()
	ds_neighbors=list()
	load_nodes=distgrid.load_nodes
	n1_depth=int(rnp[:][0][rnp[:][1].index(n1)])
	n1=load_nodes[n1]


	for i in distgrid.load_nodes_tree.tree[n1.name]:
		if int(rnp[:][0][rnp[:][1].index(i)]) > n1_depth:
			ds_neighbors.append(load_nodes[i])

	if len(ds_neighbors)!=0:
		if n1.generation != None:
			if type(n1.generation) == type(list()):
				for i in n1.generation:
					zpll.append(n1.generation.Z)
				zpll=inv_Z(zpll)
				zp[n1]=zpll

			else:
				zpll.append(n1.generation.Z)
				zp[n1]=n1.generation.Z

		for i in ds_neighbors:

			a, pp=resolve_upstream_area(distgrid, i.name, tree, rnp, nf=True)
			zp.update(pp)
			if type(a) == type(None):
				continue

			else:
				zeq=0
				if (n1, i) in distgrid.sections_by_nodes.keys():
					zeq = distgrid.sections_by_nodes[(n1, i)]

					if isinstance(zeq.transformer, TransformerModel):
						a= zeq.a.dot(a+zeq.transformer.z).dot(zeq.d)
						zpll.append(a)

					elif isinstance(zeq.transformer, Auto_TransformerModel):
						a= zeq.a.dot(a).dot(zeq.d)
						zpll.append(a)
					else:
						a=zeq.Z + a
						zpll.append(a)

				zp[n1,i] = a

		if len(zpll) == 0:
			return None, zp
		elif len(zpll) == 1 and n1.generation != None:
			zp[n1]=inv_Z(zpll)
			return zp[n1], zp
		else:
			return inv_Z(zpll), zp

	else:

		if n1.generation !=None:
			if type(n1.generation) == type(list()):
				for i in n1.generation:
					zpll.append(i.Z)

				zpll=inv_Z(zpll)
				zp[n1]=zpll

				return zpll, zp

			else:
				zp[n1]=n1.generation.Z

				return n1.generation.Z, zp


		else:
			return None, zp

def inv_Z(zpll):
		zeq=0
		if len(zpll) !=1:
			for i in zpll:
				if np.all(i==0):
					zeq=0
					break
				else:
					zeq +=np.linalg.inv(i)

			if np.all(zeq == 0):
				return zeq

			else:
				zeq = np.linalg.inv(zeq)
				return zeq
		else:
			return zpll[0]

def resolve_downstream_area(distgrid, n1, tree, rnp, n2=None, nf=False):

	zpll=list()
	zp=dict()
	up_neighbor=None
	ds_neighbors=list()
	load_nodes=distgrid.load_nodes
	n1_depth=int(rnp[:][0][rnp[:][1].index(n1)])
	n1=load_nodes[n1]


	if n1_depth !=0:
		for i in distgrid.load_nodes_tree.tree[n1.name]:
			if int(rnp[:][0][rnp[:][1].index(i)]) < n1_depth:
				up_neighbor=load_nodes[i]
				break

		a, pp=resolve_downstream_area(distgrid, up_neighbor.name, tree, rnp, n2=n1.name, nf=True)
		zp.update(pp)

		if type(a) != type(None):
			zeq=0

			if (up_neighbor, n1) in distgrid.sections_by_nodes.keys():
				zeq = distgrid.sections_by_nodes[(up_neighbor, n1)]

				if isinstance(zeq.transformer, TransformerModel):
					a = zeq.A.dot(a).dot(zeq.d) + zeq.transformer.z
					zpll.append(a)

				elif isinstance(zeq.transformer, Auto_TransformerModel):
					a = zeq.A.dot(a).dot(zeq.d) + zeq.transformer.zz
					zpll.append(a)

				else:
					a=zeq.Z + a
					zpll.append(a)
				zp[up_neighbor, n1] = a


	if n1.generation != None and nf:
		if type(n1.generation) == type(list()):
			for i in n1.generation:
				zpll.append(i.Z)
				zp[n1]=zpll

		else:
			zpll.append(n1.generation.Z)
			zp[n1]=zpll

	if n1.external_grid != None:
		zpll.append(n1.external_grid.Z)
		zp[n1]=zpll

	if nf:
		for i in distgrid.load_nodes_tree.tree[n1.name]:
			if int(rnp[:][0][rnp[:][1].index(i)]) > n1_depth  and (i != n2):
				ds_neighbors.append(load_nodes[i])


	if len(ds_neighbors) !=0:

		for i in ds_neighbors:
			a,pp=resolve_upstream_area(distgrid, i.name, tree, rnp)
			zp.update(pp)

			if type(a) == type(None):
				continue

			else:

				zeq=0

				if (n1, i) in distgrid.sections_by_nodes.keys():
					zeq = distgrid.sections_by_nodes[(n1, i)]

					if isinstance(zeq.transformer, TransformerModel):
						a= zeq.a.dot(a+zeq.transformer.z).dot(zeq.d)
						zpll.append(a)

					elif isinstance(zeq.transformer, Auto_TransformerModel):
						a= zeq.a.dot(a + zeq.transformer.zz).dot(zeq.d)
						zpll.append(a)

					else:
						a=zeq.Z + a
						zpll.append(a)

				zp[n1,i] = a

	if len(zpll) == 0:
		return None, zp
	if len(zpll) == 1:
		return zpll[0], zp
	else:

		zeq=0
		for i in zpll:

			if i.any()==0:
				zeq=i
				return zeq, zp

			zeq +=np.linalg.inv(i)

		zeq = np.linalg.inv(zeq)
		return zeq, zp

def calc_contributions(zz,Iz,nodes,distgrid,ep):
	tree=distgrid.load_nodes_tree.tree
	ln=distgrid.load_nodes
	nodes=[ln[nodes]]
	ict=dict()

	visit_nodes=list()
	iz_nodes=dict()
	iz_nodes[nodes[0].name]=[Iz,ep]
	ict[nodes[0].name]=Iz
	root_name=distgrid.load_nodes_tree.root

	while len(nodes) !=0:

		next_nodes=list()
		for i in nodes:
			stop=False
			adjacent_nodes=[ln[x] for x in tree[i.name] if ln[x] not in visit_nodes]

			isl=dict()
			inv=np.zeros((3,3), dtype=complex)
			p=0

			if i.generation !=None:
				if type(i.generation)==type(list()):
					ep_n=iz_nodes[i.name][1]
					for j in i. generation:
						p=np.linalg.inv(vectorize_zz(j.Z,iz_nodes[i.name][1]))
						isl[j.name]=[p,None]
						inv +=p
				else:
					ep_n=iz_nodes[i.name][1]
					p=np.linalg.inv(i.generation.Z)
					isl[i.generation.name]=[p,None]
					inv +=p

			if i.name==root_name:
				if i.external_grid.Z.all()==0:
					stop=True
				else:
					ep_n=iz_nodes[i.name][1]
					p=np.linalg.inv(i.external_grid.Z)
					isl[i.external_grid.name]=[p,None]
					inv +=p

			if not(stop):
				for j in adjacent_nodes:
					p=0
					if (i, j) in zz.keys():

						section=distgrid.sections_by_nodes[(i,j)]
						next_nodes.append(j)
						p=np.linalg.inv(vectorize_zz(zz[(i,j)].round(6), iz_nodes[i.name][1]))
						if isinstance(section.transformer,TransformerModel):
							ep_n = new_phase_erase(section.transformer.connection,iz_nodes[i.name][1])

							isl[j.name] = [p, section.a]

						elif isinstance(section.transformer, Auto_TransformerModel):
							ep_n = new_phase_erase(section.transformer.connection,iz_nodes[i.name][1])
							isl[j.name] = [p, section.a]
						else:
							ep_n=iz_nodes[i.name][1]
							isl[j.name] = [p, None]
						inv += p

					elif (j, i) in zz.keys():
						section=distgrid.sections_by_nodes[(j,i)]
						next_nodes.append(j)
						p=np.linalg.inv(vectorize_zz(zz[(j,i)].round(6), ep))
						if isinstance(section.transformer,TransformerModel):
							ep_n = new_phase_erase(section.transformer.connection,iz_nodes[i.name][1])

							isl[j.name] = [p, section.d]

						elif isinstance(section.transformer, Auto_TransformerModel):
							ep_n = new_phase_erase(section.transformer.connection,iz_nodes[i.name][1])
							isl[j.name] = [p, section.d]
						else:
							ep_n=iz_nodes[i.name][1]
							isl[j.name] = [p, None]

						inv += p


			if len(isl) !=0:


				z=np.linalg.inv(inv)
				for y in isl.keys():
					izz=isl[y][0].dot(z).dot(iz_nodes[i.name][0])
					if type(isl[y][1]) != type(None):
						izz=isl[y][1].dot(izz)
					if y[0]=="GD":

						iz_nodes[y] =  [izz,ep_n]
						ict[y] =  izz

					else:

						iz_nodes[y] =  [izz, ep_n]
						ict[y] =  izz



		visit_nodes.extend(nodes)

		nodes=next_nodes


	return ict


def vectorize_zz(value,phase_erase=None):
	for i in phase_erase:
		value[:,i]=0
		value[i,:]=0
		value[i,i]=10e9
	return value

def dict_to_DataFrame(ict):
	for i in ict.keys():
		ict[i]=ict[i].reshape(1,3,).tolist()[0]
	ict=pd.DataFrame(ict)

	return ict

def new_phase_erase(tf_type,old_phase_erase):

	pr=[0,1,2]
	if tf_type == "Dyn":
		if len(old_phase_erase)==2:
			pr.remove(old_phase_erase[0])
			pr.remove(old_phase_erase[1])

			return pr
		elif len(old_phase_erase)==1:

			return []
		else:

			return []
