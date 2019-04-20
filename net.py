import numpy as np
#from utils import sigmoid

class Net:
    def __init__(self):
        self.weights1 = np.random.uniform(low=-1.0, high=1.0, size=(2,8))
        self.weights2 = np.random.uniform(low=-1.0, high=1.0, size=(8,1))

    def eval(self, width, height):
        input = np.array([width, height])
        layer1 = relu(np.dot(input, self.weights1))
        output = relu(np.dot(layer1, self.weights2))
        return output[0]

    def reset(self):
        self.weights1 = np.random.uniform(low=-1.0, high=1.0, size=(2,8))
        self.weights2 = np.random.uniform(low=-1.0, high=1.0, size=(8,1))

    def display(self):
        print(self.weights1)
        print(self.weights2)

def relu(x):
    np.maximum(x, 0, x)
    return x
