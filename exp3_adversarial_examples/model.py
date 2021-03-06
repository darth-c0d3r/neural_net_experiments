import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.nn.parameter import Parameter
from collections import OrderedDict
import numpy as np

class classifier(nn.Module):

	def __init__(self, size, conv, fc, n_classes):
		super(classifier, self).__init__()
		self.dropout_rate = 0.5

		# convolutional layers
		self.c_kernel_size = 3
		self.c_padding = 1
		self.p_kernel_size = 2
		self.conv_layers = nn.ModuleList()
		self.dropout_layers = nn.ModuleList()

		for i in range(len(conv)-1):
			self.conv_layers.append(nn.Conv2d(conv[i], conv[i+1], kernel_size=self.c_kernel_size, padding=self.c_padding))
			size = size + 2*self.c_padding - self.c_kernel_size + 1
			size = int(size/self.p_kernel_size)

		self.pool = nn.MaxPool2d(kernel_size=self.p_kernel_size)

		self.size = size*size*conv[-1]

		# fully connected layers
		fc = [self.size] + fc
		self.fc_layers = nn.ModuleList()
		for i in range(len(fc)-1):
			self.fc_layers.append(nn.Linear(fc[i], fc[i+1]))
			self.dropout_layers.append(nn.Dropout(self.dropout_rate))

		# output layer
		self.output_layer = nn.Linear(fc[-1], n_classes)

	def forward(self, x):
		index=0

		# convolutional layers
		for conv_layer in self.conv_layers:
			x = self.pool(torch.relu(conv_layer(x)))

		# fully connected layers
		x = x.view(-1, self.size)
		for fc_layer in self.fc_layers:
			x = torch.relu(fc_layer(x))
			x = self.dropout_layers[index](x)
			index += 1

		# output layer
		x = self.output_layer(x)

		return x