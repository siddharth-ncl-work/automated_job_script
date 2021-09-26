parent_mol_dir='../parent'
mol_dir='.'

import numpy as np
import pandas as pd
import os
import subprocess
from subprocess import Popen,PIPE


def getParentData():
	global data_dict
	output=subprocess.run(['grep','Thermal correction to Gibbs Free Energy','neutral/.log'],stdout=PIPE)	
	output=subprocess.run(['grep','Thermal correction to Gibbs Free Energy','anion/.log'],stdout=PIPE)
	
def getGtherm_neutral(mol_list):
	Gtherm_list=[]
    for mol in mol_list:
		os.path.isfile(f'{mol}.log'):
			output=subprocess.run(['grep','Thermal correction to Gibbs Free Energy',f'{mol}.log'],stdout=PIPE)
		else:
			Gtherm_list.append(np.nan)

def getGtherm_anion():
	pass

def getEsol_neutral():
	Esol_list=[]
	for mol in mol_list:
        os.path.isfile(f'{mol}.log'):
			output=subprocess.run(['grep','SCF Done',file],stdout=PIPE)
        else:
            Gtherm_list.append(np.nan)

def getEsol_anion():
	pass

def getMolList():
	mol_set=set()
	for file in os.listdir('{mol_dir}/neutral/')+os.listdir('{mol_dir}/anion'):
		if file.endswith('.log'):
			mol_set.add(file.strip().split('.')[0])
	return list(list(mol_set))
		
mol_list=getMolList()
print(mol_list)
data_dict={'molecule':[],'G_therm_neutral':[],'G_therm_anion':[],'E_sol_neutral':[],'E_sol_anion':[]}

