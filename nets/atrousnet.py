# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Contains a variant of the CIFAR-10 model definition."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

slim = tf.contrib.slim

trunc_normal = lambda stddev: tf.truncated_normal_initializer(stddev=stddev)


def atrousnet(images, num_classes=43, is_training=False,
              dropout_keep_prob=0.5,
              prediction_fn=slim.softmax,
              scope='CifarNet'):
    """Creates a model using Dilated-Atrous convolutions.

    Args:
        images: A batch of `Tensors` of size [batch_size, height, width, channels].
        num_classes: the number of classes in the dataset.
        is_training: specifies whether or not we're currently training the model.
            This variable will determine the behaviour of the dropout layer.
        dropout_keep_prob: the percentage of activation values that are retained.
        prediction_fn: a function to get predictions out of logits.
        scope: Optional variable_scope.

    Returns:
        logits: the pre-softmax activations, a tensor of size
            [batch_size, `num_classes`]
        end_points: a dictionary from components of the network to the corresponding
            activation.
        """
    end_points = {}

    with tf.variable_scope(scope, 'AtrousNet', [images, num_classes]):

        net = slim.conv2d(images, 64, [3, 3], scope='conv1',
                          padding='VALID', weights_regularizer=None)
        end_points['conv1'] = net
        # net = slim.max_pool2d(net, [3, 3], 1, scope='pool1', padding='SAME')

        net = slim.conv2d(net, 128, [3, 3], rate=2, scope='conv2',
                          padding='VALID', weights_regularizer=None)
        end_points['conv2'] = net
        # net = slim.max_pool2d(net, [3, 3], 1, scope='pool2', padding='SAME')

        net = slim.conv2d(net, 192, [3, 3], rate=4, scope='conv3',
                          padding='VALID', weights_regularizer=None)
        end_points['conv3'] = net
        # net = slim.max_pool2d(net, [3, 3], 1, scope='pool3', padding='SAME')

        net = slim.conv2d(net, 256, [1, 1], scope='conv4')
        end_points['conv4'] = net
        net = slim.dropout(net, dropout_keep_prob, is_training=is_training,
                           scope='dropout1')
        net = slim.conv2d(net, num_classes, [1, 1],
                          biases_initializer=tf.zeros_initializer,
                          weights_initializer=trunc_normal(1/256.0),
                          weights_regularizer=None,
                          activation_fn=None,
                          scope='conv5')

        net = slim.avg_pool2d(net, [18, 18], scope='avg_pool', padding='VALID')
        logits = tf.squeeze(net)

        end_points['Logits'] = logits
        end_points['Predictions'] = prediction_fn(logits, scope='Predictions')

    return logits, end_points
atrousnet.default_image_size = 32


def atrousnet_arg_scope(weight_decay=0.004):
    """Defines the default cifarnet argument scope.

    Args:
        weight_decay: The weight decay to use for regularizing the model.

    Returns:
        An `arg_scope` to use for the inception v3 model.
    """
    with slim.arg_scope(
            [slim.conv2d],
            weights_initializer=tf.truncated_normal_initializer(stddev=5e-2),
            # weights_regularizer=slim.l2_regularizer(weight_decay),
            weights_regularizer=None,
            activation_fn=tf.nn.relu):
        with slim.arg_scope(
                [slim.fully_connected],
                biases_initializer=tf.constant_initializer(0.1),
                weights_initializer=trunc_normal(0.04),
                weights_regularizer=slim.l2_regularizer(weight_decay),
                activation_fn=tf.nn.relu) as sc:
            return sc