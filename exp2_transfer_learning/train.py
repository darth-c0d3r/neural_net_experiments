import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as F
import torch.optim as optim
import torchvision # for data
from model import SimpleConvNet
import numpy as np
import PIL
from database_util import *

# hyper-parameters
batch_size = 100
epochs = 100
report_every = 50
conv = [3,16,32,64]
fc = [256]
n_classes = 5
dropout_rate = 0.5
size = 32 # update

# GPU related info
cuda = 1
device = torch.device("cuda" if torch.cuda.is_available() and cuda == 1 else "cpu") # default gpu
print("Device:", device)

model = SimpleConvNet(size, conv, fc, n_classes, dropout_rate).to(device)
model.my_init(0.0, 0.01)
criterion = nn.CrossEntropyLoss().to(device)
optimizer = optim.Adagrad(model.parameters(), lr=0.005)

def train(model, optim, db):

	for epoch in range(1, epochs+1):

		train_loader = torch.utils.data.DataLoader(db['train'],batch_size=batch_size, shuffle=True)

		# Update (Train)
		model.train()
		for batch_idx, (data, target) in enumerate(train_loader):

			data, target = Variable(data.to(device)), Variable((target.float()).to(device))
			optimizer.zero_grad()
			output = model(data)
			loss = criterion(output,target.long())
			# print(output.size())
			pred = output.data.max(1, keepdim=True)[1] # get the index of the max log-probability
			correct = pred.eq(target.data.view_as(pred).long()).cpu().sum()
			loss.backward()
			optimizer.step()

			if batch_idx % report_every == 0:
				print('Train Epoch: {} [{}/{} ({:.0f}%)]  Loss: {:.6f}, Accuracy: {}/{} ({:.6f})'.format(
					epoch, batch_idx * len(data), len(train_loader.dataset),
					100.0 * batch_idx / len(train_loader), loss.item(), correct, len(data), float(correct)/float(len(data))))


		# Evaluate
		model.eval()
		eval_loss = float(0)
		correct = 0
		batch_count = 0
		eval_loader = torch.utils.data.DataLoader(db['eval'], batch_size=batch_size, shuffle=True)
		with torch.no_grad():
			for data, target in eval_loader:

				data, target = Variable(data.to(device)), Variable((target.float()).to(device))
				output = model(data)
				eval_loss += criterion(output, target.long()).item() # sum up batch loss
				pred = output.data.max(1, keepdim=True)[1] # get the index of the max log-probability
				correct += pred.eq(target.data.view_as(pred).long()).cpu().sum()
				batch_count += 1

		eval_loss /= batch_count
		accuracy = float(correct) / len(eval_loader.dataset)

		with open('results/base_model_dataright.dat', 'a+') as file:
			file.write(str(accuracy)+"\n")
		print('Eval set: Average loss: {:.4f}, Accuracy: {}/{} ({:.6f})\n'.format(
			eval_loss, correct, len(eval_loader.dataset),
			accuracy))					
	torch.save(model, 'convnet_right.pt')

def main():

	db = prepare_db()
	db_l, db_r = split_database(db)
	print("Database split done!")
	train(model, optimizer, db_r)


if __name__ == '__main__':
	main()