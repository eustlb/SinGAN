import torch
import random
from math import floor
from torchvision import transforms
from PIL import Image

class Dataset(torch.utils.data.dataset.Dataset):
    def __init__(self, root='', batch_size=1, crop_size=0, custom=0):
        self.root = root
        self.batch_size = batch_size
        self.crop_size = crop_size
        self.custom = custom
        self._init()

    def _init(self):
        # to tensor
        self.to_tensor = transforms.ToTensor()

        # open image
        image = Image.open(self.root).convert('RGB')
        self.image = self.to_tensor(image).unsqueeze(dim=0)
        self.image = (self.image - 0.5) * 2

        # set from outside
        self.reals = None
        self.noises = None
        self.amps = None

    def _get_augment_params(self, size):
        random.seed(random.randint(0, 12345))

        # position
        w_size, h_size = size

        #if random.randint(0,3) >0 : 
        x = random.randint(0, max(0, w_size - self.crop_size))
        y = random.randint(0, max(0, h_size - self.crop_size))

        flip = random.random() > 0.5

        return {'pos': (x, y), 'flip': flip}

    def _augment(self, image, aug_params, scale=1):
        x, y = aug_params['pos']
        
        image = image[:, round(x * scale):(round(x * scale) + round(self.crop_size * scale)), round(y * scale):(round(y * scale) + round(self.crop_size * scale))]
        #print("shape : [{}:{}, {}:{}] ,  x,y : [{},{}]  , scale : {}  , crop : {}".format(round(x * scale), (round(x * scale) + round(self.crop_size * scale)), round(y * scale), 
        #(round(y * scale) + round(self.crop_size * scale)), x, y, scale, self.crop_size))
        if aug_params['flip']:
            image = image.flip(-1)
        return image
    
    def _cust_augment(self, image, aug_params, scale=1):
        if random.randint(0,3) >2 : 
          #print("--0--")
          x, y = aug_params['pos']
        else : 
          x, y = (0, 0)

        #print("shape : [{}:{}, {}:{}] ,  x,y : [{},{}]  , scale : {}  , crop : {}".format(round(x * scale), (round(x * scale) + round(self.crop_size * scale)), round(y * scale), 
        #(round(y * scale) + round(self.crop_size * scale)), x, y, scale, self.crop_size))
        image = image[:, round(x * scale):(round(x * scale) + round(self.crop_size * scale)), round(y * scale):(round(y * scale) + round(self.crop_size * scale))]

        if aug_params['flip']:
            image = image.flip(-1)

        return image

    def __getitem__(self, index):
        amps = self.amps

        #print("self.image.size()[-2:] : ", self.image.size()[-2:])

        # cropping
        if self.crop_size:
            reals, noises = {}, {}
            aug_params = self._get_augment_params(self.image.size()[-2:])
            #print("image size : ", self.image.size()[-2:])

            for key in self.reals.keys():
              scale = self.reals[key].size(-1) / float(self.image.size(-1))
              #print("scaled image : ", self.reals[key].size(-1))
              
              if self.custom: 
                reals.update({key: self._cust_augment(self.reals[key].clone(), aug_params, scale)})
                noises.update({key: self._cust_augment(self.noises[key].clone(), aug_params, scale)})
              
              else : 
                #print("Size : ", self.reals[key].size())
                reals.update({key: self._augment(self.reals[key].clone(), aug_params, scale)})
                noises.update({key: self._augment(self.noises[key].clone(), aug_params, scale)})

        # full size
        else: 
            reals = self.reals #TODO: clone when crop
            noises = self.noises #TODO: clone when crop

        return {'reals': reals, 'noises': noises, 'amps': amps}
       
    def __len__(self):
        return self.batch_size
