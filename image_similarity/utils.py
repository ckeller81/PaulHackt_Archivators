import os
import shutil
import numpy as np
from tqdm import tqdm

import torch
import torch.utils.data
import torchvision.transforms as transforms

from torch.autograd import Variable

from image_similarity.imageloader import TripletImageLoader


def KleeImageNetLoader(root, batch_size_train, batch_size_test):
    # Normalize training set together with augmentation
    transform_train = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[
            0.229, 0.224, 0.225])
    ])

    # Normalize test set same as training set without augmentation
    transform_test = transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[
            0.229, 0.224, 0.225])
    ])

    print("==> Preparing Klee ImageNet dataset ...")

    trainset = TripletImageLoader(base_path=root, triplets_filename="triplets.txt", transform=transform_train)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size_train, num_workers=1)

    testset = TripletImageLoader(base_path=root, triplets_filename="", transform=transform_test, train=False)
    testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size_test, num_workers=1)

    return trainloader, testloader


def train(net, criterion, optimizer, scheduler, trainloader, testloader, start_epoch, epochs, is_gpu):
    print("==> Start training ...")

    net.train()
    for epoch in range(start_epoch, epochs + start_epoch):
        print(f"Start with epoch {epoch}")

        loop = tqdm(trainloader)
        running_loss = 0.0

        for batch_idx, (data1, data2, data3) in enumerate(loop):

            if is_gpu:
                data1, data2, data3 = data1.cuda(), data2.cuda(), data3.cuda()

            # wrap in torch.autograd.Variable
            data1, data2, data3 = Variable(
                data1), Variable(data2), Variable(data3)

            # compute output and loss
            embedded_a, embedded_p, embedded_n = net(data1, data2, data3)
            loss = criterion(embedded_a, embedded_p, embedded_n)

            # compute gradient and do optimizer step
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # print statistics
            loss_data = loss.data
            running_loss += loss_data

            loop.set_description(f"Epoch [{epoch}/{epoch}]")
            # if batch_idx % 30 == 0:
            # print("mini Batch Loss: {}".format(loss_data))

        # Normalizing the loss by the total number of train batches
        running_loss /= len(trainloader)

        print("Training Epoch: {0} | Loss: {1}".format(epoch + 1, running_loss))

        # remember best acc and save checkpoint
        save_checkpoint({
            'epoch': epoch + 1,
            'state_dict': net.state_dict(),
        }, False)

    print('==> Finished Training ...')


def calculate_distance(i1, i2):
    return np.sum((i1 - i2) ** 2)


def tranform_test_img(img):
    transform_test = transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[
            0.229, 0.224, 0.225])
    ])
    return transform_test(img)


def save_checkpoint(state, is_best, filename='checkpoint.pth.tar'):
    """Save checkpoint."""
    directory = "checkpoint"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = directory + filename
    torch.save(state, filename)
    if is_best:
        shutil.copyfile(filename, directory + 'model_best.pth.tar')