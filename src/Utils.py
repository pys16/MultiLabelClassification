import os
import numpy as np
import torch
import torch.utils.data as data
from scipy.misc import imread
from PIL import Image


def adjust_learning_rate(optimizer, epoch, init_lr, step=80, decay=0.1):
    """
    This function adjust the learning rate automatically during training.
    https://www.pytorchtutorial.com/pytorch-learning-rate-decay/
    :param optimizer: the optimizer
    :param epoch: current epoch
    :param init_lr: initial learning rate
    :param step: literally
    :param decay: literally
    :return: Nothing
    """
    lr = init_lr*(decay**(epoch//step))
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr


class Logger:
    def __init__(self, path):
        self.path = path

    def scalar_summary(self, name, value, steps):
        self.__dict__[name] = (steps, value)


class MyDataLoader(data.Dataset):
    def __init__(self, transform, trainval='train', data_path='../dataset', random_crops=0):
        """
        Initialize the dataset. Inherited from torch.data.Dataset, __len__ and __getitem__ need to be implemented.
        VOC(Labels only) tree:
        --dataset root
         |--train
         | |--JPEGImages(dir)
         | |--annotations.txt
         |
         |--test
           |--JPEGImages(dir)
           |--annotations.txt
        :param transform: the transformation
        :param data_path: the root of the datapath
        :param random_crops:
        """
        self.data_path = data_path
        self.transform = transform
        self.random_crops = random_crops
        self.train_or_test = trainval

        self.__init_classes()
        self.names, self.labels = self.__dataset_info()

    def __getitem__(self, index):
        """
        This is the getitem func which enables enumerator. Implemented.
        :param index: the index of the picture
        :return: tuple (picture, its label(s))
        """
        x = imread(os.path.join(self.data_path, self.train_or_test, 'JPEGImages', self.names[index]+'.jpg'),
                   mode='RGB')
        x = Image.fromarray(x)

        # Resize directly instead of the strange operations done below...
        x = x.resize((224, 224), Image.BILINEAR)

        # scale = np.random.rand() * 2 + 0.25
        # w = int(x.size[0] * scale)
        # h = int(x.size[1] * scale)
        # if min(w, h) < 227:
        #     scale = 227 / min(w, h)
        #     w = int(x.size[0] * scale)
        #     h = int(x.size[1] * scale)

        # x = x.resize((w,h), Image.BILINEAR) # Random scale

        if self.random_crops == 0:
            x = self.transform(x)
        else:
            crops = []
            for i in range(self.random_crops):
                crops.append(self.transform(x))
            x = torch.stack(crops)

        y = self.labels[index]
        return x, y

    def __len__(self):
        """
        How many images are there. Implemented.
        :return: length
        """
        return len(self.names)

    def __dataset_info(self):
        """
        Generate names(np.array, with string elements) and labels(np.array, with array(number) elements).
        The labels appears like this: [0 0 0 0 0 1 0 0 0 0 0 0 1 0 0 1 0 0 0 0]
        Those with value 1 means the object exists in this image
        :return: names labels
        """
        annotation_file = os.path.join(self.data_path, self.train_or_test, 'annotations.txt')
        with open(annotation_file, 'r') as fp:
            lines = fp.readlines()

        names = []
        labels = []
        for line in lines:
            # Name
            names.append(line.strip('\n').split(' ')[0])

            # Label
            str_label = line.strip('\n').split(' ')[1:]
            num_label = [int(x) for x in str_label]
            flag_label = np.zeros(self.num_classes)
            flag_label[num_label] = 1

            labels.append(np.array(flag_label))

        return np.array(names), np.array(labels).astype(np.float32)

    def __init_classes(self):
        self.classes = ('person', 'bird', 'cat', 'cow',
                        'dog', 'horse', 'sheep', 'aeroplane', 'bicycle',
                        'boat', 'bus', 'car', 'motorbike',
                        'train', 'bottle', 'chair',
                        'diningtable', 'pottedplant', 'sofa', 'tvmonitor')
        self.num_classes = len(self.classes)
        self.class_to_ind = dict(zip(self.classes, range(self.num_classes)))