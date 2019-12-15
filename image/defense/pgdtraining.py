from DeepRobust.image.defense.config import config, args

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
import torch.nn.functional as F

import numpy as np
from PIL import Image
from DeepRobust.image.attack.pgd import PGD
from DeepRobust.image.netmodels.CNN import Net
from DeepRobust.image.defense.base_defense import BaseDefense

class PGDtraining(BaseDefense):
    def __init__(self, model, device):
        self.model = model
        self.device = device

    def generate(self, **kwargs):
        """
        Pgd attacking process:
        """
        assert parse_params(**kwargs) 

        torch.manual_seed(100)
        device = torch.device(self.device)

        model = model.to(self.device)
        optimizer = optim.SGD(model.parameters(), lr, momentum=0.1)
    
        save_model = True
        for epoch in range(1, 100 + 1):     ## 5 batches
            print(epoch, flush = True)  ## han
            train(self.model, self.device, self.train_loader, self.optimizer, epoch)
            test(model, device, test_loader)

            if (save_model):
                if os.path.isdir('./' + self.save_dir):
                    torch.save(model.state_dict(), './' + self.save_dir +"/mnist_pgdtraining.pt")  ## han
                    print("model saved in " + './' + save_dir)
                else:
                    print("make new directory and save model in " + './' + self.save_dir)
                    os.mkdir('./' + self.save_dir)
                    torch.save(model.state_dict(), './' + self.save_dir +"/mnist_pgdtraining.pt")  ## han

        return self.model    
    
    def parse_params(self, 
                    train_loader,
                    test_loader,
                    save_dir,
                    lr = 0.0005,
                    momentum = 0.1):
        # """
        # Set parameters for pgd training.
        # """
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.save_dir = save_dir
        self.lr = lr
        self.momentum = momentum

    def train(self, device, train_loader, optimizer, epoch):
        """
        Training process.
        """
        self.model.train()
        correct = 0
        bs = train_loader.batch_size

        for batch_idx, (data, target) in enumerate(train_loader):

            optimizer.zero_grad()
            data, target = data.to(device), target.to(device)
            adversary = PGD(model)
            AdvExArray = adversary.generate(data, target, epsilon = 0.3, num_steps = 40)

            output = model(AdvExArray)
            loss = loss()
            loss.backward()

            optimizer.step()

            pred = output.argmax(dim = 1, keepdim = True)
            correct += pred.eq(target.view_as(pred)).sum().item()

            #print every 10
            if batch_idx % 10 == 0:
                print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\tAccuracy:{:.2f}%'.format(
                    epoch, batch_idx * len(data), len(train_loader.dataset),
                       100. * batch_idx / len(train_loader), loss.item(), 100 * correct/(10*bs)))
            correct = 0
        

    def test(self, model, device, test_loader):
        """
        Testing process.
    
        """
        model.eval()

        test_loss = 0
        correct = 0
        test_loss2 = 0
        correct2 = 0
        with torch.no_grad():
             for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                
                # print clean accuracy
                output = model(data)
                test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
                pred = output.argmax(dim = 1, keepdim = True)  # get the index of the max log-probability
                correct += pred.eq(target.view_as(pred)).sum().item()
                
                # print adversarial accuracy
                advdata = adv_data()

                output_adv = model(advdata)
                test_loss2 += F.nll_loss(output_adv, target, reduction='sum').item()  # sum up batch loss
                pred2 = output_adv.argmax(dim = 1, keepdim = True)  # get the index of the max log-probability
                correct2 += pred2.eq(target.view_as(pred2)).sum().item()
            
        test_loss /= len(test_loader.dataset)
        test_loss2 /= len(test_loader.dataset)

        print('\nTest set: Clean loss: {:.3f}, Clean Accuracy: {}/{} ({:.0f}%)\n'.format(
            test_loss, correct, len(test_loader.dataset),
            100. * correct / len(test_loader.dataset)))
        
        print('\nTest set: Adv loss: {:.3f}, Adv Accuracy: {}/{} ({:.0f}%)\n'.format(
            test_loss2, correct2, len(test_loader.dataset),
            100. * correct2 / len(test_loader.dataset)))
            
    def adv_data(self, epsilon, num_steps):
        # """
        # Generate input(adversarial) data for training.
        
        # """
        adversary = PGD(model)
        data_adv = adversary.generate(data, pred.flatten(), epsilon = 0.3, num_steps = 40)
        return data_adv

    def calculate_loss(self, output, target):
        """
        Calculate loss for training.
        """
        
        loss = F.nll_loss(output, target)
        return loss
    
