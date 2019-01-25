#!/usr/bin/env python
#!-*-coding:utf-8 -*-
"""

@version: python3.7
@author: ‘v-enshi‘
@license: Apache Licence
@contact: 123@qq.com
@site:
@software: PyCharm
@file: hw1.py
@time: 2019/1/23 19:24
"""


import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time

start = time.perf_counter()
#####################################
# 1. data loading
train = []
test = []
for i in range(18):
    train.append([])


with open('train.csv','r',encoding='big5') as trainFile:
    trainData = csv.reader(trainFile)
    count = 0
    for row in trainData:
        if count == 0:

            count += 1
            continue
        for i in range(3,27):

            if row[i] == "NR":
                train[(count-1)%18].append(float(0))
            else:
                train[(count - 1) % 18].append(float(row[i]))
        count += 1


with open('test.csv','r',encoding='big5') as testFile:
    testData = csv.reader(testFile)

    count = 0
    for row in testData:
        if count % 18 == 0:
            test.append([])
            for i in range(2,11):
                test[(count) // 18].append(float(row[i]))
        else:
            for i in range(2, 11):
                if row[i] == "NR":
                    test[(count)//18].append(float(0))
                else:
                    test[(count ) // 18].append(float(row[i]))
        count += 1
xTest = np.array(test)


#####################################
#3.归一化normalize
train = np.array(train)
def MaxMinNormalization(x,Max,Min):
    x = (x - Min) / (Max - Min)
    return x
Max = []
Min = []
for i in range(len(train)):
    Max.append(train[i,:].max())
    Min.append(train[i,:].min())
    train[i, :] = MaxMinNormalization(train[i,:],Max[i],Min[i])

for i in range(xTest.shape[1]):
    xTest[:, i] = MaxMinNormalization(xTest[:, i], Max[i//9], Min[i//9])


#####################################
# 2.pre-processing


xTrain = []
yTrain = []

lenOfMonth = int(len(train[0]) / 12)  #5760/12 =480 = 20*24
lenOfMonthX = lenOfMonth - 9
#per month
# i-> month; j ->hours in a month; k-> feature; t -> 9 hours
for i in range(12):
    for j in range(lenOfMonthX):
        xTrain.append([])
        for k in range(18):
            for t in range(9):
                xTrain[lenOfMonthX * i +j].append(train[k][lenOfMonth * i +j + t])
                # x是把9个小时的指标按照[九个小时的指标1，九个小时的指标2，]组成了一个vetors

        yTrain.append(train[9][lenOfMonth*i+j+9])


x = np.array(xTrain)
y = np.array(yTrain)


#####################################
#4.training

w = np.zeros(len(x[0])) #162*1
one = np.ones(len(x))
b = 1
lr = 0.0001 #learning rate
iteration = int(1e6)

x_t = x.transpose()  #x: 5652*162  ; x_t:162*5652
loss_history = []


for i in range(iteration):

    error = (y - b*one- np.dot(x ,w))
    loss = np.sum(error**2)/len(x)
    loss_history.append(loss)
    w_grad = -np.dot(x_t,error)/len(x)
    b_grad = -error.sum()/len(x)
    w = w - lr* w_grad
    b = b - lr*b_grad

print("loss history is",loss_history)
np.save('model_norm_Grad_w.npy',w)
np.save('model_norm_Grad_b.npy',b)


############################################
#5 testing

predict = np.dot(xTest,w) + b*np.ones(len(xTest))
predict = predict * (Max[9] - Min[9]) + Min[9]


##########################
#6 evaluate
ans = pd.read_csv("ans.csv")             #读取csv文件
true = list(ans["value"])

true_count = 0
for i in range(len(true)):
    if abs(predict[i] - true[i])< 6:
        true_count += 1
accuracy = true_count / len(true)
print("accuracy is :{:.2%}".format(accuracy))

filename = "predict_norm_grad.csv"
text = open(filename,"w+")
s = csv.writer(text,delimiter=',',lineterminator='\n')
s.writerow(["id", "value"])
for i in range(len(ans)):
    s.writerow(["id_"+str(i), str(predict[i])])
text.close()

predictError = np.sum(abs(predict - true))/(len(predict))
print("predict error is :",predictError )
end = time.perf_counter()
print ('time cost is ',end-start)


plt.plot(range(iteration),loss_history,'o-',ms =3,lw=1.5,color = 'black')
#plt.xlim(-200,-100)
plt.ylim(0,0.5)
plt.xlabel(r'$iter$',fontsize =16)
plt.ylabel(r'$loss$',fontsize =16)
plt.show()





