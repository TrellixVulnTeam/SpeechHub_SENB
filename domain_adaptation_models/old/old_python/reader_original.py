from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import os

import tensorflow as tf


def _read_words(filename):
	with tf.gfile.GFile(filename, "r") as f:
		return f.read().decode("ascii", 'ignore').replace("\n", " ").split()


def _build_vocab(filename):
	data = _read_words(filename)

	counter = collections.Counter(data)
	count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))

	words, _ = list(zip(*count_pairs))
	word_to_id = dict(zip(words, range(len(words))))

	return word_to_id


def _file_to_word_ids(filename, word_to_id):
	data = _read_words(filename)
	return [word_to_id[word] for word in data if word in word_to_id]


def ds_raw_data(data_path=None):
	train_path = os.path.join(data_path, "train.txt")
	valid_path = os.path.join(data_path, "valid.txt")
	test_path = os.path.join(data_path, "test.txt")

	word_to_id = _build_vocab(train_path)
	train_data = _file_to_word_ids(train_path, word_to_id)
	valid_data = _file_to_word_ids(valid_path, word_to_id)
	test_data = _file_to_word_ids(test_path, word_to_id)
	vocabulary = len(word_to_id)
	unk_id = word_to_id['<unk>']
	return train_data, valid_data, test_data, vocabulary, unk_id


def ds_producer(raw_data, batch_size, num_steps, name=None):
	with tf.name_scope(name):
		raw_data = tf.convert_to_tensor(raw_data, name="raw_data", dtype=tf.int32)

		data_len = tf.size(raw_data)
		batch_len = data_len // batch_size
		data = tf.reshape(raw_data[0 : batch_size * batch_len],
											[batch_size, batch_len])

		epoch_size = (batch_len - 1) // num_steps
		assertion = tf.assert_positive(
				epoch_size,
				message="epoch_size == 0, decrease batch_size or num_steps")
		with tf.control_dependencies([assertion]):
			epoch_size = tf.identity(epoch_size, name="epoch_size")

		i = tf.train.range_input_producer(epoch_size, shuffle=False).dequeue()
		x = tf.slice(data, [0, i * num_steps], [batch_size, num_steps])
		y = tf.slice(data, [0, i * num_steps + 1], [batch_size, num_steps])
		return x, y
