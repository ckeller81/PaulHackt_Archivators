import time

import numpy as np

import torch.utils.data
import torch.backends.cudnn as cudnn

from torch.autograd import Variable
from image_similarity.utils import KleeImageNetLoader

from image_similarity.triplet_net import *


def calculate_accuracy(trainloader, testloader, is_gpu):
    net = TripletNet(resnet18(model_urls))

    # For training on GPU, we need to transfer net and data onto the GPU
    # http://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html#training-on-gpu
    if is_gpu:
        net = torch.nn.DataParallel(net).cuda()
        cudnn.benchmark = True

    print('==> Retrieve model parameters ...')
    checkpoint = torch.load("checkpoint/checkpointcheckpoint.pth.tar")
    net.load_state_dict(checkpoint['state_dict'])

    net.eval()

    t1 = time.time()
    t2 = time.time()
    print("Get all test image classes, Done ... | Time elapsed {}s".format(t2 - t1))

    # list of traning images names, e.g., "../tiny-imagenet-200/train/n01629819/images/n01629819_238.JPEG"
    training_images = []
    for line in open("triplets.txt"):
        line_array = line.split(",")
        training_images.append(line_array[0])
    t3 = time.time()
    print("Get all training images, Done ... | Time elapsed {}s".format(t3 - t2))

    # get embedded features of training
    embedded_features = []
    with torch.no_grad():
        for batch_idx, (data1, data2, data3) in enumerate(trainloader):

            if is_gpu:
                data1, data2, data3 = data1.cuda(), data2.cuda(), data3.cuda()

            # wrap in torch.autograd.Variable
            data1, data2, data3 = Variable(
                data1), Variable(data2), Variable(data3)

            # compute output
            embedded_a, _, _ = net(data1, data2, data3)
            embedded_a_numpy = embedded_a.data.cpu().numpy()

            embedded_features.append(embedded_a_numpy)

    t4 = time.time()
    print("Get embedded_features, Done ... | Time elapsed {}s".format(t4 - t3))

    # TODO: 1. Form 2d array: Number of training images * size of embedding
    embedded_features_train = np.concatenate(embedded_features, axis=0)

    embedded_features_train.astype('float32').tofile("embedded_features_train.txt")

    # embedded_features_train = np.fromfile("../embedded_features_train.txt", dtype=np.float32)


if __name__ == '__main__':
    # load triplet dataset
    trainloader, testloader = KleeImageNetLoader(".", 5, 5)

    # calculate test accuracy
    calculate_accuracy(trainloader, testloader, False)