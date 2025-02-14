##### imports

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import sys

from gensim import corpora, models
import numpy as np
import fnmatch

##### functions
        
class ds_data(object):
    def __init__(self, batch_size, data_path, name):
        self.batch_size = batch_size
        
        #reading data
        path = os.path.join(data_path, name)
        self.directory = os.path.join(data_path, name + '_batch_files')
        info_file = os.path.join(self.directory, 'info.txt')
        if not (os.path.exists(info_file)):
            print("Creating directory %s" % self.directory)
            if not (os.path.exists(self.directory)): 
                os.mkdir(self.directory)
            amount_sentences = sum(1 for line in open(path))
            self._epoch_size = amount_sentences//batch_size
            self.batch_size = batch_size
            with open(info_file, 'w') as i_f:
                i_f.write('batch_size: ' + str(batch_size) + '\n')
                i_f.write('amount_sentences: ' + str(amount_sentences) + '\n')
            create_new_batch_files = True
        else:
            with open(info_file,"r") as i_f:
                batch_size_previous = int(i_f.readline().split()[1])
                amount_sentences = int(i_f.readline().split()[1])
            if batch_size_previous != batch_size:
                os.remove(info_file)
                create_new_batch_files = True
            else:
                create_new_batch_files = False                     
        self._epoch_size = amount_sentences//batch_size
        
        #creating batch_files that will later be read
        if create_new_batch_files:
            filelist = [ f for f in os.listdir(self.directory)]
            for f in filelist:
                os.remove(os.path.join(self.directory,f))
            with open(path, "r") as f:
                sentences = [lines.decode('utf-8') for lines in f]
            for i in xrange(self._epoch_size):
                batch_file = os.path.join(self.directory, 'batch' + str(i) + '.txt')
                with open(batch_file, 'w') as bf:
                    for j in xrange(batch_size):
                        new_sentence = sentences[i + j*self._epoch_size]
                        bf.write(new_sentence.encode('utf-8'))
            with open(info_file, 'w') as i_f:
                i_f.write('batch_size: ' + str(batch_size) + '\n')
                i_f.write('amount_sentences: ' + str(amount_sentences) + '\n')   
            print('creating batch_files done')
            
        #reading word_to_id
        dict_path = os.path.join(data_path, "dictionary.ds.dict")
        dictionary = corpora.Dictionary.load(dict_path)
        self._word_to_id = dict()
        for (wordid,word) in dictionary.iteritems():
            self._word_to_id[word] = wordid
        self._unk_id = self._word_to_id['<unk>']
        self._bos_id = self._word_to_id['<bos>']
        self._eos_id = self._word_to_id['<eos>']
        self._pad_id = len(self._word_to_id)
        
        self.batch_id = 0
        

    def next_batch(self, max_seq_len):
        if self.batch_id == self.epoch_size:
            self.batch_id = 0
        batch_data = self.pad_id*np.ones((self.batch_size,max_seq_len))
        batch_labels = self.pad_id*np.ones((self.batch_size,max_seq_len))
        seq_len = np.zeros(self.batch_size)
        
        with open(os.path.join(self.directory, 'batch' + str(self.batch_id) + '.txt'), 'r') as f:
            sentences = [lines.decode('utf-8') for lines in f]
        for i in xrange(self.batch_size):
            new_sentence = sentences[i].split()
            new_sentence = [self._word_to_id[word] for word in new_sentence]
            seqlen = len(new_sentence)
            seq_len[i] = min(seqlen, max_seq_len)
            
            batch_data[i,0:min(seqlen, max_seq_len)] = new_sentence[0:min(seqlen, max_seq_len)]
            new_sentence.append(self.bos_id)
            batch_labels[i,0:min(seqlen, max_seq_len)] = new_sentence[1:min(seqlen, max_seq_len)+1]
        self.batch_id += 1 
        return batch_data, batch_labels, seq_len
        
    def print_next_batch(self, max_seq_len):
        batch_data, batch_labels, seq_len = self.next_batch(max_seq_len)
        reverse = {v: k for k, v in self._word_to_id.iteritems()}
        reverse[self.pad_id] = 'PAD'
        batch_lst = [reverse[int(word_id)] for sentence in batch_data for word_id in sentence]
        targets_lst = [reverse[int(word_id)] for sentence in batch_labels for word_id in sentence]
        for i in xrange(self.batch_size):
            print('batch ' + str(i))
            print(batch_lst[max_seq_len*i:max_seq_len*(i+1)])
            print(targets_lst[max_seq_len*i:max_seq_len*(i+1)])
            print(seq_len[i])
        
    @property
    def unk_id(self):
        return self._unk_id
        
    @property
    def bos_id(self):
        return self._bos_id
        
    @property
    def eos_id(self):
        return self._eos_id
        
    @property
    def pad_id(self):
        return self._pad_id

    @property
    def word_to_id(self):
        return self._word_to_id
        
    @property
    def epoch_size(self):
        return self._epoch_size

class ds_data_with_history(object):
    def __init__(self, batch_size, history_size, data_path, name):
        self.batch_size = batch_size
	self.history_size = history_size        

        #reading data
        path = os.path.join(data_path, name)
        self.directory = os.path.join(data_path, name + '_batch_files')
        info_file = os.path.join(self.directory, 'info.txt')
        if not (os.path.exists(info_file)):
            print("Creating directory %s" % self.directory)
            if not (os.path.exists(self.directory)): 
                os.mkdir(self.directory)
            amount_sentences = sum(1 for line in open(path))
            self._epoch_size = amount_sentences//batch_size
            self.batch_size = batch_size
            with open(info_file, 'w') as i_f:
                i_f.write('batch_size: ' + str(batch_size) + '\n')
                i_f.write('amount_sentences: ' + str(amount_sentences) + '\n')
            create_new_batch_files = True
        else:
            with open(info_file,"r") as i_f:
                batch_size_previous = int(i_f.readline().split()[1])
                amount_sentences = int(i_f.readline().split()[1])
            if batch_size_previous != batch_size:
                os.remove(info_file)
                create_new_batch_files = True
            else:
                create_new_batch_files = False                     
        self._epoch_size = amount_sentences//batch_size
        
        #creating batch_files that will later be read
        if create_new_batch_files:
            filelist = [ f for f in os.listdir(self.directory)]
            print(filelist)
            for f in filelist:
                os.remove(os.path.join(self.directory,f))
            with open(path, "r") as f:
                sentences = [lines.decode('utf-8') for lines in f]
            for i in xrange(self._epoch_size):
                batch_file = os.path.join(self.directory, 'batch' + str(i) + '.txt')
                with open(batch_file, 'w') as bf:
                    for j in xrange(batch_size):
                        new_sentence = sentences[i + j*self._epoch_size]
                        bf.write(new_sentence.encode('utf-8'))
            with open(info_file, 'w') as i_f:
                i_f.write('batch_size: ' + str(batch_size) + '\n')
                i_f.write('amount_sentences: ' + str(amount_sentences) + '\n')   
            print('creating batch_files done')
            
        #reading word_to_id
        dict_path = os.path.join(data_path, "dictionary.ds.dict")
        dictionary = corpora.Dictionary.load(dict_path)
        self._word_to_id = dict()
        for (wordid,word) in dictionary.iteritems():
            self._word_to_id[word] = wordid
        self._unk_id = self._word_to_id['<unk>']
        self._bos_id = self._word_to_id['<bos>']
        self._eos_id = self._word_to_id['<eos>']
        self._pad_id = len(self._word_to_id)
        
        self.batch_id = 0
        self.history = self.pad_id*np.ones((batch_size,history_size))
        

    def next_batch(self, max_seq_len):
        if self.batch_id == self.epoch_size:
            self.batch_id = 0
        batch_data = self.pad_id*np.ones((self.batch_size,max_seq_len))
        history_data = np.concatenate((self.history,self.pad_id*np.ones((self.batch_size,max_seq_len-1))), axis=1)
        batch_labels = self.pad_id*np.ones((self.batch_size,max_seq_len))
        seq_len = np.zeros(self.batch_size)
        
        with open(os.path.join(self.directory, 'batch' + str(self.batch_id) + '.txt'), 'r') as f:
            sentences = [lines.decode('utf-8') for lines in f]
        for i in xrange(self.batch_size):
            new_sentence = sentences[i].split()
            new_sentence = [self._word_to_id[word] for word in new_sentence]
            seqlen = len(new_sentence)
            seq_len[i] = min(seqlen, max_seq_len)

            batch_data[i,0:min(seqlen, max_seq_len)] = new_sentence[0:min(seqlen, max_seq_len)]
            history_data[i,-max_seq_len+1:] = batch_data[i,0:-1]
            if seqlen >= self.history_size:
                self.history[i] = np.array(new_sentence[-self.history_size:])
            else:
                self.history[i] = np.concatenate((self.history[i,seqlen:],np.array(new_sentence)))
            new_sentence.append(self.bos_id)
            batch_labels[i,0:min(seqlen, max_seq_len)] = new_sentence[1:min(seqlen, max_seq_len)+1]
        self.batch_id += 1 
        return batch_data, history_data, batch_labels, seq_len
        
    def print_next_batch(self, max_seq_len):
        batch_data, history_data, batch_labels, seq_len = self.next_batch(max_seq_len)
        reverse = {v: k for k, v in self._word_to_id.iteritems()}
        reverse[self.pad_id] = 'PAD'
        batch_lst = [reverse[int(word_id)] for sentence in batch_data for word_id in sentence]
        targets_lst = [reverse[int(word_id)] for sentence in batch_labels for word_id in sentence]
        history_lst = [reverse[int(word_id)] for sentence in history_data for word_id in sentence]
        for i in xrange(self.batch_size):
            print('batch ' + str(i))
            print(batch_lst[max_seq_len*i:max_seq_len*(i+1)])
            print(targets_lst[max_seq_len*i:max_seq_len*(i+1)])
            print(history_lst[(self.history_size+max_seq_len-1)*i:(self.history_size+max_seq_len-1)*(i+1)])
            print(seq_len[i])
        
    @property
    def unk_id(self):
        return self._unk_id
        
    @property
    def bos_id(self):
        return self._bos_id
        
    @property
    def eos_id(self):
        return self._eos_id
        
    @property
    def pad_id(self):
        return self._pad_id

    @property
    def word_to_id(self):
        return self._word_to_id
        
    @property
    def epoch_size(self):
        return self._epoch_size
