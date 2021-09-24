job_list=[
'CF3_R2_neutral',
'CF3_R1_neutral'
]

import numpy as np
import pandas as pd
import subprocess
from subprocess import Popen,PIPE
import os
import time

def isRunning(job):
	flag=False
	p1=Popen(['qstat','-f'],stdout=PIPE)
	p2=Popen(['grep','Job_Name'],stdin=p1.stdout,stdout=PIPE,stderr=PIPE,encoding='utf-8') 
	p1.stdout.close()
	output,error=p2.communicate()
	if job in output.strip():
		flag=True
	return flag

def dirFinishedFlag(job):
	if os.path.isfile(f'{job}.log')	:
		with open(f'{job}.log') as file:
			if 'Normal termination'.lower() in file.readlines()[-1].lower():
				return 'Normal Termination'
			else:
				return 'Gaussian Error'
	else:
		return 'Log file not found '

def prepareJob(job):
	output=subprocess.run(['obabel','-i','mol',f'{job}.mol','-o','xyz'],stdout=PIPE,encoding='utf-8')
	num_atoms=int(output.stdout.strip().split('\n')[0])
	coords='\n'.join(output.stdout.strip().split('\n')[2:])
	assert num_atoms==len(coords.split('\n')),'obabel error'
	input_file_content='%Mem=4800MB\n'\
					   '%nprocshared=12\n'\
                      f'%chk={job}.chk\n'\
                       '# opt freq b3lyp/6-31+g(d,p) scf=xqc\n'\
                       '\n'\
					   'mydftmodel_sets\n'\
                       '\n'\
                       '0 1\n'\
                      +f'{coords}'\
                       '\n\n'
	with open(f'{job}.com','w') as file:
		file.write(input_file_content)
	job_script_content='#! /bin/bash\n'\
					   '#PBS -l nodes=compute-0-0:ppn=16\n'\
					   f'#PBS -N opt_{job}\n'\
					   '#PBS -j oe\n'\
					   'cd $PBS_O_WORKDIR\n'\
					   '\n'\
					   f'job={job}\n'\
					   '\n'\
					   'cat $PBS_NODEFILE > pbsnodes\n'\
					   'mkdir /tmp/$job\n'\
					   'cp $job.*  /tmp/$job/\n'\
					   'cd /tmp/$job\n'\
					   'g09 $job.com\n'\
					   'cp -r * $PBS_O_WORKDIR\n'\
					   'cd ..\n'\
					   'rm -rf /tmp/$job/\n'
	with open(f'gauss_compute_script','w') as file:
		file.write(job_script_content)

def submitJob(job):
	return subprocess.run(['qsub','gauss_compute_script'])

def waitAndCheckJob(job):
	global progress_df
	interval=0.3
	time.sleep(1)
	while isRunning(job):
		print('\tRUNNING |',end='\r')
		time.sleep(interval)
		print('\tRUNNING /',end='\r')
		time.sleep(interval)
		print('\tRUNNING -',end='\r')
		time.sleep(interval)
		print('\tRUNNING \\',end='\r')
		progress_df.loc[progress_df['JOB']==job,'STATUS']='RUNNING'
		progress_df.to_csv('PROGRESS',sep='\t',index=False)
		time.sleep(interval)
	dir_finished_flag=dirFinishedFlag(job)
	progress_df.loc[progress_df['JOB']==job,'STATUS']=f'FINISHED: {dir_finished_flag}'
	progress_df.to_csv('PROGRESS',sep='\t',index=False)
	return dir_finished_flag


# MAIN
detect_files=True
if detect_files:
	job_list=[]
	for file in os.listdir('.'):
		if file.endswith('.mol'):
			job_list.append(file.strip().split('.')[0])
print(f'JOBS:\n{list(enumerate(job_list,1))}')
progress_df=pd.DataFrame.from_dict({'Sr.No.':np.arange(1,len(job_list)+1),\
						  			'JOB':job_list,\
						  			'STATUS':['--']*len(job_list)\
						 		   })
progress_df.to_csv('PROGRESS',sep='\t',index=False)
for idx,job in enumerate(job_list):
	print(f'\n{idx+1}.{job}:')
	if isRunning(job):
		print('\tJob is already running')
		dir_finished_flag=waitAndCheckJob(job)
		print(f'\tFINISHED: {dir_finished_flag}')
	else:
		dir_finished_flag=dirFinishedFlag(job)
		if dir_finished_flag.lower()=='Normal Termination'.lower():
			progress_df.loc[progress_df['JOB']==job,'STATUS']=f'FINISHED: {dir_finished_flag}'
			progress_df.to_csv('PROGRESS',sep='\t',index=False)
			print(f'\tFINISHED: {dir_finished_flag}')
		else:
			print('\tPreparing job files')
			prepareJob(job)
			print('\tSubmitting job')
			output=submitJob(job)
			if output.returncode==0:
				print('\tJob submitted successfully')
				dir_finished_flag=waitAndCheckJob(job)
				print(f'\tFINISHED: {dir_finished_flag}')
			else:
				print('\tEncountered an error during job submission')
				progress_df.loc[progress_df['JOB']==job,'STATUS']='Job Could not be submitted'
				progress_df.to_csv('PROGRESS',sep='\t',index=False)
