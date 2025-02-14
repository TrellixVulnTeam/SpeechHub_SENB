### authors: Wim Boes & Robbe Van Rompaey
### date: 12-10-2016

import os
import sys
import itertools

# parameters

params = {	'init_scale'	: [0.05],
		'learning_rate'	: [1],
		'max_grad_norm'	: [1,5,10],
		'num_layers'	: [2],
		'num_steps'	: [35],
		'hidden_size'	: [512],
		'max_epoch'	: [6],
		'max_max_epoch'	: [39],
		'keep_prob'	: [0.5],
		'lr_decay'	: [0.8],
		'batch_size'	: [20],
		'vocab_size'	: [10000],
		'embedded_size'	: [256],
                'optimizer'     : ['GradDesc'],
                'loss_function' : ['sequence_loss_by_example']          }


job_name = 'grad_norm.job'
dag_name = 'grad_norm.dag'
test_name = 'max_grad_norm'
python_file_name = 'ptboriginal'
python_file_path = python_file_name + '.py'

# script jobfile		

jobfile = open(job_name,'w')

jobfile.write('Universe         = vanilla \n')
jobfile.write('RequestCpus	= 1 \n')
jobfile.write('RequestMemory    = 2G \n')
jobfile.write('+RequestWalltime = 36000 \n')
jobfile.write('\n')
jobfile.write('request_GPUs = 1 \n')
jobfile.write('requirements =  (CUDAGlobalMemoryMb >= 1024) && (CUDACapability >= 3.5) && (machineowner == "PSI/Spraak") \n')
jobfile.write('\n')
jobfile.write('NiceUser = true \n')
jobfile.write('Notification = Error \n')
jobfile.write('initialdir = . \n')
jobfile.write('\n')
jobfile.write('executable = /users/start2014/r0385169/bin/python \n')
jobfile.write('arguments = ' + '"' + python_file_path +' --init_scale=$(init_scale) --learning_rate=$(learning_rate) --max_grad_norm=$(max_grad_norm) --num_layers=$(num_layers) --num_steps=$(num_steps) --hidden_size=$(hidden_size) --max_epoch=$(max_epoch) --max_max_epoch=$(max_max_epoch) --keep_prob=$(keep_prob) --lr_decay=$(lr_decay) --batch_size=$(batch_size) --vocab_size=$(vocab_size) --embedded_size=$(embedded_size) --num_run=$(num_run) --test_name=$(test_name) --optimizer=$(optimizer) --loss_function=$(loss_function)' + '"' + '\n')
jobfile.write('\n')
jobfile.write('Log          = ' + python_file_name + '_$(test_name)_$(num_run).log \n')
jobfile.write('Output       = ' + python_file_name + '_$(test_name)_$(num_run).out \n')
jobfile.write('Error        = ' + python_file_name + '_$(test_name)_$(num_run).err \n')
jobfile.write('\n')
jobfile.write('Queue')

jobfile.close()

# script dagfile

dagfile = open(dag_name,'w')

params_keys = params.keys()

num_runs = 1
for key in params_keys:
	num_runs = num_runs * len(params[key])

for num_run in xrange(num_runs):
	dagfile.write('JOB ' + test_name + str(num_run) + ' ' + job_name + ' DIR . \n')

perm_opts_list = []
for key in params_keys:
	perm_opts_list.append(params[key])
perm_list = list(itertools.product(*perm_opts_list))

dagfile.write('\n')

num_run = 0
for perm in perm_list:
	dagfile.write('VARS ' + test_name + str(num_run) + ' ')
	for index,key in enumerate(params_keys):
		dagfile.write(key + '=' + '"' + str(perm[index]) + '" ')
	dagfile.write('num_run=' + '"' + str(num_run) + '" ')
	num_run = num_run + 1
	dagfile.write('test_name=' + '"' + test_name + '" \n')

dagfile.close()
