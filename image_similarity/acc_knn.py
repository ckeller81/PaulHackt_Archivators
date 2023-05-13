import time
import os
import argparse

import numpy as np

import torch.utils.data
import torch.backends.cudnn as cudnn
import matplotlib.pyplot as plt

from PIL import Image
from joblib import dump, load
from torch.autograd import Variable
from image_similarity.utils import tranform_test_img

from image_similarity.triplet_net import *

from sklearn.neighbors import NearestNeighbors


def load_train_embedding():
    embedding_space = np.fromfile("embedded_features_train.txt", dtype=np.float32)
    embedding_space = embedding_space.reshape(-1, 4096)
    return embedding_space


def load_train_images():
    # list of traning images names, e.g., "../tiny-imagenet-200/train/n01629819/images/n01629819_238.JPEG"
    # update to get class names
    t2 = time.time()

    training_images = []
    for line in open("triplets.txt"):
        line_array = line.split(",")
        if line_array[0] not in training_images:
            training_images.append(line_array[0])
    t3 = time.time()
    print("Get all training images, Done ... | Time elapsed {}s".format(t3 - t2))
    return training_images


def gen_embedding(net, data, is_gpu):
    if is_gpu:
        data = data.cuda()
    data = Variable(data)

    embedded, _, _ = net(data, data, data)
    embedded_numpy = embedded.data.cpu().numpy()
    return embedded_numpy


def load_net(is_gpu):
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
    return net


def plot_results(query, top_N, results, images):
    fig = plt.figure()
    ax = fig.add_subplot(1, top_N + 1, 1)
    imgplot = plt.imshow(np.asarray(Image.open(query)))
    ax.set_title("Query")

    for indx, val in enumerate(results[1][0]):
        if indx == top_N:
            break
        else:
            ax = fig.add_subplot(1, top_N + 1, indx + 2)
            a = np.asarray(Image.open(images[val]))
            plt.axis('off')
            imgplot = plt.imshow(a)

    fig.savefig("Image_Search_Results.jpg", bbox_inches='tight')


def train_neighbor_model(embedding_data):
    # n_neighbors is 500 because there are 200 classes and 100,000 images in training space
    neighbor_model = NearestNeighbors(n_neighbors=6, algorithm='kd_tree', n_jobs=-1)
    neighbor_model.fit(embedding_data)
    dump(neighbor_model, 'checkpoint/neighbor_model.joblib')
    return neighbor_model


def predict_unseen(test_query, top_N, training_images, embedding_space, is_gpu):
    if os.path.isfile('checkpoint/neighbor_model.joblib'):
        neighbor_model = load('checkpoint/neighbor_model.joblib')
    else:
        neighbor_model = train_neighbor_model(embedding_space)

    query_img = tranform_test_img(Image.open(test_query).convert('RGB')).reshape(1, 3, 224, 224)

    net = load_net(is_gpu)

    query_embed = gen_embedding(net, query_img, is_gpu)

    predictions = neighbor_model.kneighbors(query_embed, return_distance=True)

    plot_results(test_query, top_N, predictions, training_images)


if __name__ == '__main__':
    image = "./data/val/57789.jpg"

    training_images = load_train_images()
    embedding_space = load_train_embedding()

    predict_unseen(image, 5, training_images, embedding_space, False)