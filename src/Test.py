import torch
import numpy as np
from scipy.misc import imread
from PIL import Image
import torchvision.transforms as transforms
from torch.autograd import Variable

from Utils import load_model_from_file


def test(transform, model_path='../checkpoints/190508_0909_001.pth', img_path='../test.jpg', gpu=None):
    net = load_model_from_file(model_path, True)
    net.eval()
    img = imread(img_path, mode='RGB')
    img = Image.fromarray(img)
    img = transform(img)
    img = img.view((-1, 3, 224, 224))
    with torch.no_grad():
        img = Variable(img)
    if gpu is not None:
        img = img.cuda()

    outputs = net(img)
    outputs = outputs.cpu().data
    outputs = outputs.view((-1, 20))
    print(outputs)


if __name__ == '__main__':
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
    val_transform = transforms.Compose([
            #transforms.Scale(256),
            #transforms.CenterCrop(227),
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            normalize,
        ])
    test(val_transform)
