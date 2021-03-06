import numpy as np
import matplotlib.pyplot as plt
#plt.style.use('ggplot')

from sklearn.cluster import KMeans

#x = [1, 5, 1.5, 8, 1, 9]
#y = [2, 8, 1.8, 8, 0.6, 11]
#plt.scatter(x,y)
#plt.show()

X = np.array([[1, 2],
			   [5, 8],
			   [1.5, 1.8],
			   [1, 0.6],
			   [9, 11]])

#print X
#X = np.append(X, [[3,4]], axis=0)
#print X

kmeans = KMeans(n_clusters=2)
kmeans.fit(X)

centroids = kmeans.cluster_centers_
labels = kmeans.labels_

print "Centroides:"
print(centroids)
print "Tamanyo de los clusters:"
print np.bincount(labels)
print ("-------------")
'''
#grafico para cluster = 2
print(labels)

colors = ["g.", "r."]

for i in range(len(X)):
	print("coordinate",X[i], "label:", labels[i])
	plt.plot(X[i][0], X[i][1], colors[labels[i]], markersize = 10)

plt.scatter(centroids[:, 0],centroids[:, 1], marker = "x", s=150, linewidths = 5, zorder = 10)

plt.show()
'''