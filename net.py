import numpy as np

class Net:
    def __init__(self):
        self.weights1 = np.random.uniform(low=-1.0, high=1.0, size=(2,8))
        self.weights2 = np.random.uniform(low=-1.0, high=1.0, size=(8,1))

    # evaluate net given 2 inputs
    def eval(self, width, height):
        input = np.array([width, height])
        layer1 = relu(np.dot(input, self.weights1))
        output = relu(np.dot(layer1, self.weights2))
        return output[0]

    # reset weights of net
    def reset(self):
        self.weights1 = np.random.uniform(low=-1.0, high=1.0, size=(2,8))
        self.weights2 = np.random.uniform(low=-1.0, high=1.0, size=(8,1))

    # print weights of net
    def display(self):
        print(self.weights1)
        print(self.weights2)

# relu activation on matrice
def relu(x):
    np.maximum(x, 0, x)
    return x
