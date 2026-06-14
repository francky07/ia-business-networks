#!/usr/bin/env python3
"""
Module indépendant – Réseau de neurones pour la prise de décision
"""
import random
import math

class NeuralNetwork:
    def __init__(self, input_size=5, hidden_size=12, output_size=4):
        self.w1 = [[random.uniform(-0.5,0.5) for _ in range(hidden_size)] for __ in range(input_size)]
        self.b1 = [0.0]*hidden_size
        self.w2 = [[random.uniform(-0.5,0.5) for _ in range(output_size)] for __ in range(hidden_size)]
        self.b2 = [0.0]*output_size
        self.lr = 0.01

    def sigmoid(self, x):
        return 1/(1+math.exp(-x))

    def forward(self, x):
        hidden = [self.sigmoid(sum(x[i]*self.w1[i][j] for i in range(len(x))) + self.b1[j]) for j in range(len(self.w1[0]))]
        out = [self.sigmoid(sum(hidden[j]*self.w2[j][k] for j in range(len(hidden))) + self.b2[k]) for k in range(len(self.w2[0]))]
        return out, hidden

    def predict_action(self, state):
        out, _ = self.forward(state)
        return out.index(max(out))

    def train(self, state, target_action, reward):
        out, hidden = self.forward(state)
        error = [0.0]*len(out)
        for i in range(len(out)):
            error[i] = (1 if i==target_action else 0) - out[i]
        # Mise à jour couche sortie
        for j in range(len(self.w2)):
            for k in range(len(self.w2[0])):
                self.w2[j][k] += self.lr * error[k] * out[k] * (1-out[k]) * hidden[j]
        for k in range(len(self.b2)):
            self.b2[k] += self.lr * error[k] * out[k] * (1-out[k])
        # Mise à jour couche cachée (simplifiée)
        for i in range(len(self.w1)):
            for j in range(len(self.w1[0])):
                self.w1[i][j] += self.lr * error[target_action] * random.uniform(-0.01,0.01)
        for j in range(len(self.b1)):
            self.b1[j] += self.lr * error[target_action] * random.uniform(-0.01,0.01)
