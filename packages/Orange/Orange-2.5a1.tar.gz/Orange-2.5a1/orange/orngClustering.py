from Orange.clustering.kmeans import * 
# from Orange.cluster.hierarchical import * 

from Orange.distance.instances import \
     AlignmentList, \
     DistanceMap, \
     DistanceMapConstructor, \
     ExampleDistConstructor, \
     ExampleDistBySorting, \
     ExampleDistVector, \
     ExamplesDistance, \
     ExamplesDistance_Normalized, \
     ExamplesDistanceConstructor

from Orange.distance.instances import Hamming as ExamplesDistance_Hamming
from Orange.distance.instances import DTW as ExamplesDistance_DTW
from Orange.distance.instances import Euclidean as ExamplesDistance_Euclidean
from Orange.distance.instances import Manhattan as ExamplesDistance_Manhattan
from Orange.distance.instances import Maximal as ExamplesDistance_Maximal
from Orange.distance.instances import Relief as ExamplesDistance_Relief

from Orange.distance.instances import DTWConstructor as ExamplesDistanceConstructor_DTW
from Orange.distance.instances import EuclideanConstructor as ExamplesDistanceConstructor_Euclidean
from Orange.distance.instances import HammingConstructor as ExamplesDistanceConstructor_Hamming
from Orange.distance.instances import ManhattanConstructor as ExamplesDistanceConstructor_Manhattan
from Orange.distance.instances import MaximalConstructor as ExamplesDistanceConstructor_Maximal 
from Orange.distance.instances import ReliefConstructor as ExamplesDistanceConstructor_Relief

from Orange.distance.instances import PearsonRConstructor as ExamplesDistanceConstructor_PearsonR
from Orange.distance.instances import PearsonR as ExamplesDistance_PearsonR
from Orange.distance.instances import SpearmanRConstructor as ExamplesDistanceConstructor_SpearmanR
from Orange.distance.instances import SpearmanR as ExamplesDistance_SpearmanR


from Orange.clustering.kmeans import Clustering as KMeans
from Orange.clustering.kmeans import init_random as kmeans_init_random
from Orange.clustering.kmeans import init_diversity as kmeans_init_diversity
from Orange.clustering.kmeans import init_hclustering as KMeans_init_hierarchicalClustering
from Orange.clustering.kmeans import data_center as data_center
from Orange.clustering.kmeans import plot_silhouette as plot_silhouette
from Orange.clustering.kmeans import score_distance_to_centroids as score_distance_to_centroids
from Orange.clustering.kmeans import score_silhouette as score_silhouette
from Orange.clustering.kmeans import score_fast_silhouette as score_fastsilhouette

from Orange.clustering.hierarchical import clustering as hierarchicalClustering
from Orange.clustering.hierarchical import clustering_features as hierarchicalClustering_attributes
from Orange.clustering.hierarchical import cluster_to_list as hierarchicalClustering_clusterList
from Orange.clustering.hierarchical import top_clusters as hierarchicalClustering_topClusters
from Orange.clustering.hierarchical import top_cluster_membership as hierarhicalClustering_topClustersMembership
from Orange.clustering.hierarchical import order_leaves as orderLeaves

from Orange.clustering.hierarchical import dendrogram_draw, DendrogramPlotPylab, DendrogramPlot
#left for backward compatibility
hierarchicalClustering_attributes
