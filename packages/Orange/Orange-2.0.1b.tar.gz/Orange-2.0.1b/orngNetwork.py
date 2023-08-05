import math
import numpy
import os.path
import orange
import orangeom
import orngMDS
import random
import numpy
import itertools

class MdsTypeClass():
    def __init__(self):
        self.componentMDS = 0
        self.exactSimulation = 1
        self.MDS = 2

MdsType = MdsTypeClass()

class Network(orangeom.Network):
    """Orange data structure for representing directed and undirected networks with various types of weighted connections and other data."""
    
    def __init__(self, *args):
        #print "orngNetwork.Network"
        self.optimization = NetworkOptimization(self)
        self.clustering = NetworkClustering(self)
        
    def getDistanceMatrixThreshold(self, matrix, ratio):
        """Return lower and upper distance threshold values for given ratio of edges"""
        values = []
        for i in range(matrix.dim):
            for j in range(i):
                values.append((matrix[i,j], i, j))
                
        values.sort()
        return values[0][0], values[int(ratio*len(values))][0]
        
    def save(self, fileName):
        """Saves network to Pajek (.net) file."""
        self.saveNetwork(fileName)
        
    def saveNetwork(self, fileName):
        """Save network to file."""
        
        try:
            root, ext = os.path.splitext(fileName)
            if ext == '':
                fileName = root + '.net'
            graphFile = open(fileName, 'w+')
        except IOError:
            return 1
            
        root, ext = os.path.splitext(fileName)
        if ext.lower() == ".gml":
            self.saveGML(graphFile)
        else:
            self.savePajek(graphFile)

    def saveGML(self, fp):
        """Save network to GML (.gml) file format."""
        
        fp.write("graph\n[\n")
        tabs = "\t"
        fp.write("%slabel\t\"%s\"\n" % (tabs, self.name))
        
        for v in range(self.nVertices):
            try:
                label = self.items[v]['label']
            except:
                label = ""
            
            fp.write("\tnode\n\t[\n\t\tid\t%d\n\t\tlabel\t\"%s\"\n\t]\n" % (v, label))
        
        for u,v in self.getEdges():
            fp.write("\tedge\n\t[\n\t\tsource\t%d\n\t\ttarget\t%d\n\t\tlabel\t\"%s\"\n\t]\n" % (u, v, ""))
        
        fp.write("]\n")
        
        if self.items != None and len(self.items) > 0:
            (name, ext) = os.path.splitext(fp.name)
            self.items.save(name + "_items.tab")
            
        if hasattr(self, 'links') and self.links != None and len(self.links) > 0:
            (name, ext) = os.path.splitext(fp.name)
            self.links.save(name + "_links.tab")
        
    def savePajek(self, fp):
        """Save network to Pajek (.net) file format."""
        name = ''
        fp.write('### This file was generated with Orange Network Visualizer ### \n\n\n')
        if name == '':
            fp.write('*Network ' + '"no name" \n\n')
        else:
            fp.write('*Network ' + str(name) + ' \n\n')

        # print node descriptions
        fp.write('*Vertices %8d %8d\n' % (self.nVertices, self.nEdgeTypes))
        for v in range(self.nVertices):
            fp.write('% 8d ' % (v + 1))
            try:
                label = self.items[v]['label']
                fp.write(str('"' + str(label) + '"') + ' \t')
            except:
                fp.write(str('"' + str(v) + '"') + ' \t')
            
            if hasattr(self, 'coors'):
                x = self.coors[0][v]
                y = self.coors[1][v]
                z = 0.5000
                fp.write('%.4f    %.4f    %.4f\t' % (x, y, z))
            fp.write('\n')

        # print edge descriptions
        # not directed edges
        if self.directed:
            fp.write('*Arcs \n')
            for (i, j) in self.getEdges():
                if len(self[i, j]) > 0:
                    if self.nEdgeTypes > 1:
                        edge_str = str(self[i, j])
                    else:
                        edge_str = "%f" % float(str(self[i, j]))
                    fp.write('%8d %8d %s' % (i + 1, j + 1, edge_str))                    
                    fp.write('\n')
        # directed edges
        else:
            fp.write('*Edges \n')
            writtenEdges = {}
            for (i, j) in self.getEdges():
                if len(self[i, j]) > 0:
                    if i > j: i,j = j,i
                    
                    if not (i,j) in writtenEdges:
                        writtenEdges[(i,j)] = 1
                    else:
                        continue

                    if self.nEdgeTypes > 1:
                        edge_str = str(self[i, j])
                    else:
                        edge_str = "%f" % float(str(self[i, j]))
                    fp.write('%8d %8d %s' % (i + 1, j + 1, edge_str))                    
                    fp.write('\n')

        fp.write('\n')
        
        if self.items != None and len(self.items) > 0:
            (name, ext) = os.path.splitext(fp.name)
            self.items.save(name + "_items.tab")
            
        if hasattr(self, 'links') and self.links != None and len(self.links) > 0:
            (name, ext) = os.path.splitext(fp.name)
            self.links.save(name + "_links.tab")

        return 0
        
    @staticmethod
    def read(fileName, directed=0):
        """Read network. Supported network formats: from Pajek (.net) file, GML."""
        if type(fileName) == file:
            root, ext = os.path.splitext(fileName.name)
            if ext.lower() == ".net":
                net = Network(2,0).parseNetwork(fileName.read(), directed)
                net.optimization = NetworkOptimization(net)
                return net
            else:
                print "invalid network type", fileName.name
                return None
        else:
            root, ext = os.path.splitext(fileName)
            net = None
            if ext.lower() == ".net":
                net = Network(2,0).readPajek(fileName, directed)
            elif ext.lower() == ".gml":
                net = Network(2,0).readGML(fileName)
            else:
                print "Invalid file type %s" % fileName
                
            if net is not None:
                net.optimization = NetworkOptimization(net)
            return net 

class NetworkOptimization(orangeom.NetworkOptimization):
    """main class for performing network layout optimization. Network structure is defined in orangeom.Network class."""
    
    def __init__(self, network=None, name="None"):
        if network is None:
            network = orangeom.Network(2, 0)
            
        self.setGraph(network)
        self.graph = network
        
        self.maxWidth = 1000
        self.maxHeight = 1000
        
        self.attributeList = {}
        self.attributeValues = {}
        self.vertexDistance = None
        self.mds = None
        
    def computeForces(self):
        n = self.graph.nVertices
        vertices = set(range(n))
        e_avg = 0
        edges = self.graph.getEdges()
        for u,v in edges:
            u_ = numpy.array([self.graph.coors[0][u], self.graph.coors[1][u]])
            v_ = numpy.array([self.graph.coors[0][v], self.graph.coors[1][v]])
            e_avg += numpy.linalg.norm(u_ - v_)
        e_avg /= len(edges)
        
        forces = []
        maxforce = []
        components = self.graph.getConnectedComponents()
        for component in components:
            outer_vertices = vertices - set(component)
            
            for u in component:
                u_ = numpy.array([self.graph.coors[0][u], self.graph.coors[1][u]])
                force = numpy.array([0.0, 0.0])                
                for v in outer_vertices:
                    v_ = numpy.array([self.graph.coors[0][v], self.graph.coors[1][v]])
                    d = self.vertexDistance[u, v]
                    norm = numpy.linalg.norm(v_ - u_)
                    force += (d - norm) * (v_ - u_) / norm 
            
                forces.append(force)
                maxforce.append(numpy.linalg.norm(force))
            
        maxforce = max(maxforce)
        rv = []
        for v in range(n):
            force = forces[v]
            v_ = numpy.array([self.graph.coors[0][v], self.graph.coors[1][v]])
            f = force * e_avg / maxforce
            rv.append(([v_[0], v_[0] + f[0]],[v_[1], v_[1] + f[1]]))

        return rv
    
    def collapse(self):
        if len(self.graph.getNodes(1)) > 0:
            nodes = list(set(range(self.graph.nVertices)) - set(self.graph.getNodes(1)))
                
            if len(nodes) > 0:
                subgraph = orangeom.Network(self.graph.getSubGraph(nodes))
                oldcoors = self.coors
                self.setGraph(subgraph)
                self.graph = subgraph
                    
                for i in range(len(nodes)):
                    self.coors[0][i] = oldcoors[0][nodes[i]]
                    self.coors[1][i] = oldcoors[1][nodes[i]]

        else:
            fullgraphs = self.graph.getLargestFullGraphs()
            subgraph = self.graph
            
            if len(fullgraphs) > 0:
                used = set()
                graphstomerge = list()
                #print fullgraphs
                for fullgraph in fullgraphs:
                    #print fullgraph
                    fullgraph_set = set(fullgraph)
                    if len(used & fullgraph_set) == 0:
                        graphstomerge.append(fullgraph)
                        used |= fullgraph_set
                        
                #print graphstomerge
                #print used
                subgraph = orangeom.Network(subgraph.getSubGraphMergeClusters(graphstomerge))
                                   
                nodescomp = list(set(range(self.graph.nVertices)) - used)
                
                #subgraph.setattr("items", self.graph.items.getitems(nodescomp))
                #subgraph.items.append(self.graph.items[0])
                oldcoors = self.coors
                self.setGraph(subgraph)
                self.graph = subgraph
                for i in range(len(nodescomp)):
                    self.coors[0][i] = oldcoors[0][nodescomp[i]]
                    self.coors[1][i] = oldcoors[1][nodescomp[i]]
                    
                # place meta vertex in center of cluster    
                x, y = 0, 0
                for node in used:
                    x += oldcoors[0][node]
                    y += oldcoors[1][node]
                    
                x = x / len(used)
                y = y / len(used)
                
                self.coors[0][len(nodescomp)] = x
                self.coors[1][len(nodescomp)] = y
            
    def getVars(self):
        vars = []
        if (self.graph != None):
            if hasattr(self.graph, "items"):
                if isinstance(self.graph.items, orange.ExampleTable):
                    vars[:0] = self.graph.items.domain.variables
                
                    metas = self.graph.items.domain.getmetas(0)
                    for i, var in metas.iteritems():
                        vars.append(var)
        return vars
    
    def getEdgeVars(self):
        vars = []
        if (self.graph != None):
            if hasattr(self.graph, "links"):
                if isinstance(self.graph.links, orange.ExampleTable):
                    vars[:0] = self.graph.links.domain.variables
                
                    metas = self.graph.links.domain.getmetas(0)
                    for i, var in metas.iteritems():
                        vars.append(var)
                        
        return [x for x in vars if str(x.name) != 'u' and str(x.name) != 'v']
    
    def getData(self, i, j):
        if self.graph.items is orange.ExampleTable:
            return self.data[i][j]
        elif self.graph.data is type([]):
            return self.data[i][j]
        
    def nVertices(self):
        if self.graph:
            return self.graph.nVertices
        
    def rotateVertices(self, components, phi):   
        #print phi 
        for i in range(len(components)):
            if phi[i] == 0:
                continue
            
            component = components[i]
            
            x = self.graph.coors[0][component]
            y = self.graph.coors[1][component]
            
            x_center = x.mean()
            y_center = y.mean()
            
            x = x - x_center
            y = y - y_center
            
            r = numpy.sqrt(x ** 2 + y ** 2)
            fi = numpy.arctan2(y, x)
            
            fi += phi[i]
            #fi += factor * M[i] * numpy.pi / 180
                
            x = r * numpy.cos(fi)
            y = r * numpy.sin(fi)
            
            self.graph.coors[0][component] = x + x_center
            self.graph.coors[1][component] = y + y_center 
            
    def rotateComponents(self, maxSteps=100, minMoment=0.000000001, callbackProgress=None, callbackUpdateCanvas=None):
        """Rotate the network components using a spring model."""
        if self.vertexDistance == None:
            return 1
        
        if self.graph == None:
            return 1
        
        if self.vertexDistance.dim != self.graph.nVertices:
            return 1
        
        self.stopRotate = 0
        
        # rotate only components with more than one vertex
        components = [component for component in self.graph.getConnectedComponents() if len(component) > 1]
        vertices = set(range(self.graph.nVertices))
        step = 0
        M = [1]
        temperature = [[30.0, 1] for i in range(len(components))]
        dirChange = [0] * len(components)
        while step < maxSteps and (max(M) > minMoment or min(M) < -minMoment) and not self.stopRotate:
            M = [0] * len(components) 
            
            for i in range(len(components)):
                component = components[i]
                
                outer_vertices = vertices - set(component)
                
                x = self.graph.coors[0][component]
                y = self.graph.coors[1][component]
                
                x_center = x.mean()
                y_center = y.mean()
                
                for j in range(len(component)):
                    u = component[j]

                    for v in outer_vertices:
                        d = self.vertexDistance[u, v]
                        u_x = self.graph.coors[0][u]
                        u_y = self.graph.coors[1][u]
                        v_x = self.graph.coors[0][v]
                        v_y = self.graph.coors[1][v]
                        L = [(u_x - v_x), (u_y - v_y)]
                        R = [(u_x - x_center), (u_y - y_center)]
                        e = math.sqrt((v_x - x_center) ** 2 + (v_y - y_center) ** 2)
                        
                        M[i] += (1 - d) / (e ** 2) * numpy.cross(R, L)
            
            tmpM = numpy.array(M)
            #print numpy.min(tmpM), numpy.max(tmpM),numpy.average(tmpM),numpy.min(numpy.abs(tmpM))
            
            phi = [0] * len(components)
            #print "rotating", temperature, M
            for i in range(len(M)):
                if M[i] > 0:
                    if temperature[i][1] < 0:
                        temperature[i][0] = temperature[i][0] * 5 / 10
                        temperature[i][1] = 1
                        dirChange[i] += 1
                        
                    phi[i] = temperature[i][0] * numpy.pi / 180
                elif M[i] < 0:  
                    if temperature[i][1] > 0:
                        temperature[i][0] = temperature[i][0] * 5 / 10
                        temperature[i][1] = -1
                        dirChange[i] += 1
                    
                    phi[i] = -temperature[i][0] * numpy.pi / 180
            
            # stop rotating when phi is to small to notice the rotation
            if max(phi) < numpy.pi / 1800:
                #print "breaking"
                break
            
            self.rotateVertices(components, phi)
            if callbackUpdateCanvas: callbackUpdateCanvas()
            if callbackProgress : callbackProgress(min([dirChange[i] for i in range(len(dirChange)) if M[i] != 0]), 9)
            step += 1
    
    def mdsUpdateData(self, components, mds, callbackUpdateCanvas):
        """Translate and rotate the network components to computed positions."""
        component_props = []
        x_mds = []
        y_mds = []
        phi = [None] * len(components)
        self.diag_coors = math.sqrt((min(self.graph.coors[0]) - max(self.graph.coors[0]))**2 + (min(self.graph.coors[1]) - max(self.graph.coors[1]))**2)
        
        if self.mdsType == MdsType.MDS:
            x = [mds.points[u][0] for u in range(self.graph.nVertices)]
            y = [mds.points[u][1] for u in range(self.graph.nVertices)]
            self.graph.coors[0][range(self.graph.nVertices)] =  x
            self.graph.coors[1][range(self.graph.nVertices)] =  y
            if callbackUpdateCanvas:
                callbackUpdateCanvas()
            return
        
        for i in range(len(components)):    
            component = components[i]
            
            if len(mds.points) == len(components):  # if average linkage before
                x_avg_mds = mds.points[i][0]
                y_avg_mds = mds.points[i][1]
            else:                                   # if not average linkage before
                x = [mds.points[u][0] for u in component]
                y = [mds.points[u][1] for u in component]
        
                x_avg_mds = sum(x) / len(x) 
                y_avg_mds = sum(y) / len(y)
                # compute rotation angle
                c = [numpy.linalg.norm(numpy.cross(mds.points[u], [self.graph.coors[0][u],self.graph.coors[1][u]])) for u in component]
                n = [numpy.vdot([self.graph.coors[0][u],self.graph.coors[1][u]], [self.graph.coors[0][u],self.graph.coors[1][u]]) for u in component]
                phi[i] = sum(c) / sum(n)
                #print phi
            
            x = self.graph.coors[0][component]
            y = self.graph.coors[1][component]
            
            x_avg_graph = sum(x) / len(x)
            y_avg_graph = sum(y) / len(y)
            
            x_mds.append(x_avg_mds) 
            y_mds.append(y_avg_mds)

            component_props.append((x_avg_graph, y_avg_graph, x_avg_mds, y_avg_mds, phi))
        
        w = max(self.graph.coors[0]) - min(self.graph.coors[0])
        h = max(self.graph.coors[1]) - min(self.graph.coors[1])
        d = math.sqrt(w**2 + h**2)
        #d = math.sqrt(w*h)
        e = [math.sqrt((self.graph.coors[0][u] - self.graph.coors[0][v])**2 + 
                  (self.graph.coors[1][u] - self.graph.coors[1][v])**2) for 
                  (u, v) in self.graph.getEdges()]
        
        if self.scalingRatio == 0:
            pass
        elif self.scalingRatio == 1:
            self.mdsScaleRatio = d
        elif self.scalingRatio == 2:
            self.mdsScaleRatio = d / sum(e) * float(len(e))
        elif self.scalingRatio == 3:
            self.mdsScaleRatio = 1 / sum(e) * float(len(e))
        elif self.scalingRatio == 4:
            self.mdsScaleRatio = w * h
        elif self.scalingRatio == 5:
            self.mdsScaleRatio = math.sqrt(w * h)
        elif self.scalingRatio == 6:
            self.mdsScaleRatio = 1
        elif self.scalingRatio == 7:
            e_fr = 0
            e_count = 0
            for i in range(self.graph.nVertices):
                for j in range(i + 1, self.graph.nVertices):
                    x1 = self.graph.coors[0][i]
                    y1 = self.graph.coors[1][i]
                    x2 = self.graph.coors[0][j]
                    y2 = self.graph.coors[1][j]
                    e_fr += math.sqrt((x1-x2)**2 + (y1-y2)**2)
                    e_count += 1
            self.mdsScaleRatio = e_fr / e_count
        elif self.scalingRatio == 8:
            e_fr = 0
            e_count = 0
            for i in range(len(components)):
                for j in range(i + 1, len(components)):
                    x_avg_graph_i, y_avg_graph_i, x_avg_mds_i, y_avg_mds_i, phi_i = component_props[i]
                    x_avg_graph_j, y_avg_graph_j, x_avg_mds_j, y_avg_mds_j, phi_j = component_props[j]
                    e_fr += math.sqrt((x_avg_graph_i-x_avg_graph_j)**2 + (y_avg_graph_i-y_avg_graph_j)**2)
                    e_count += 1
            self.mdsScaleRatio = e_fr / e_count       
        elif self.scalingRatio == 9:
            e_fr = 0
            e_count = 0
            for i in range(len(components)):    
                component = components[i]
                x = self.graph.coors[0][component]
                y = self.graph.coors[1][component]
                for i in range(len(x)):
                    for j in range(i + 1, len(y)):
                        x1 = x[i]
                        y1 = y[i]
                        x2 = x[j]
                        y2 = y[j]
                        e_fr += math.sqrt((x1-x2)**2 + (y1-y2)**2)
                        e_count += 1
            self.mdsScaleRatio = e_fr / e_count
        
        diag_mds =  math.sqrt((max(x_mds) - min(x_mds))**2 + (max(y_mds) - min(y_mds))**2)
        e = [math.sqrt((self.graph.coors[0][u] - self.graph.coors[0][v])**2 + 
                  (self.graph.coors[1][u] - self.graph.coors[1][v])**2) for 
                  (u, v) in self.graph.getEdges()]
        e = sum(e) / float(len(e))
        
        x = [mds.points[u][0] for u in range(len(mds.points))]
        y = [mds.points[u][1] for u in range(len(mds.points))]
        w = max(x) - min(x)
        h = max(y) - min(y)
        d = math.sqrt(w**2 + h**2)
        
        if len(x) == 1:
            r = 1
        else:
            if self.scalingRatio == 0:
                r = self.mdsScaleRatio / d * e
            elif self.scalingRatio == 1:
                r = self.mdsScaleRatio / d
            elif self.scalingRatio == 2:
                r = self.mdsScaleRatio / d * e
            elif self.scalingRatio == 3:
                r = self.mdsScaleRatio * e
            elif self.scalingRatio == 4:
                r = self.mdsScaleRatio / (w * h)
            elif self.scalingRatio == 5:
                r = self.mdsScaleRatio / math.sqrt(w * h)
            elif self.scalingRatio == 6:
                r = 1 / math.sqrt(self.graph.nVertices)
            elif self.scalingRatio == 7:
                e_mds = 0
                e_count = 0
                for i in range(len(mds.points)):
                    for j in range(i):
                        x1 = mds.points[i][0]
                        y1 = mds.points[i][1]
                        x2 = mds.points[j][0]
                        y2 = mds.points[j][1]
                        e_mds += math.sqrt((x1-x2)**2 + (y1-y2)**2)
                        e_count += 1
                r = self.mdsScaleRatio / e_mds * e_count
            elif self.scalingRatio == 8:
                e_mds = 0
                e_count = 0
                for i in range(len(components)):
                    for j in range(i + 1, len(components)):
                        x_avg_graph_i, y_avg_graph_i, x_avg_mds_i, y_avg_mds_i, phi_i = component_props[i]
                        x_avg_graph_j, y_avg_graph_j, x_avg_mds_j, y_avg_mds_j, phi_j = component_props[j]
                        e_mds += math.sqrt((x_avg_mds_i-x_avg_mds_j)**2 + (y_avg_mds_i-y_avg_mds_j)**2)
                        e_count += 1
                r = self.mdsScaleRatio / e_mds * e_count
            elif self.scalingRatio == 9:
                e_mds = 0
                e_count = 0
                for i in range(len(mds.points)):
                    for j in range(i):
                        x1 = mds.points[i][0]
                        y1 = mds.points[i][1]
                        x2 = mds.points[j][0]
                        y2 = mds.points[j][1]
                        e_mds += math.sqrt((x1-x2)**2 + (y1-y2)**2)
                        e_count += 1
                r = self.mdsScaleRatio / e_mds * e_count
                
            #r = self.mdsScaleRatio / d
            #print "d", d, "r", r
            #r = self.mdsScaleRatio / math.sqrt(self.graph.nVertices)
            
        for i in range(len(components)):
            component = components[i]
            x_avg_graph, y_avg_graph, x_avg_mds, y_avg_mds, phi = component_props[i]
            
#            if phi[i]:  # rotate vertices
#                #print "rotate", i, phi[i]
#                r = numpy.array([[numpy.cos(phi[i]), -numpy.sin(phi[i])], [numpy.sin(phi[i]), numpy.cos(phi[i])]])  #rotation matrix
#                c = [x_avg_graph, y_avg_graph]  # center of mass in FR coordinate system
#                v = [numpy.dot(numpy.array([self.graph.coors[0][u], self.graph.coors[1][u]]) - c, r) + c for u in component]
#                self.graph.coors[0][component] = [u[0] for u in v]
#                self.graph.coors[1][component] = [u[1] for u in v]
                
            # translate vertices
            if not self.rotationOnly:
                self.graph.coors[0][component] = (self.graph.coors[0][component] - x_avg_graph) / r + x_avg_mds
                self.graph.coors[1][component] = (self.graph.coors[1][component] - y_avg_graph) / r + y_avg_mds
               
        #if callbackUpdateCanvas:
        #    callbackUpdateCanvas()
    
    def mdsCallback(self, a,b=None):
        """Refresh the UI when running  MDS on network components."""
        if not self.mdsStep % self.mdsRefresh:
            self.mdsUpdateData(self.mdsComponents, self.mds, self.callbackUpdateCanvas)
            
            if self.mdsType == MdsType.exactSimulation:
                self.mds.points = [[self.graph.coors[0][i], self.graph.coors[1][i]] for i in range(len(self.graph.coors))]
                self.mds.freshD = 0
            
            if self.callbackProgress != None:
                self.callbackProgress(self.mds.avgStress, self.mdsStep)
                
        self.mdsStep += 1

        if self.stopMDS:
            return 0
        else:
            return 1
            
    def mdsComponents(self, mdsSteps, mdsRefresh, callbackProgress=None, callbackUpdateCanvas=None, torgerson=0, minStressDelta = 0, avgLinkage=False, rotationOnly=False, mdsType=MdsType.componentMDS, scalingRatio=0, mdsFromCurrentPos=0):
        """Position the network components according to similarities among them."""

        if self.vertexDistance == None:
            self.information('Set distance matrix to input signal')
            return 1
        
        if self.graph == None:
            return 1
        
        if self.vertexDistance.dim != self.graph.nVertices:
            return 1
        
        self.mdsComponents = self.graph.getConnectedComponents()
        self.mdsRefresh = mdsRefresh
        self.mdsStep = 0
        self.stopMDS = 0
        self.vertexDistance.matrixType = orange.SymMatrix.Symmetric
        self.diag_coors = math.sqrt((min(self.graph.coors[0]) - max(self.graph.coors[0]))**2 + (min(self.graph.coors[1]) - max(self.graph.coors[1]))**2)
        self.rotationOnly = rotationOnly
        self.mdsType = mdsType
        self.scalingRatio = scalingRatio

        w = max(self.graph.coors[0]) - min(self.graph.coors[0])
        h = max(self.graph.coors[1]) - min(self.graph.coors[1])
        d = math.sqrt(w**2 + h**2)
        #d = math.sqrt(w*h)
        e = [math.sqrt((self.graph.coors[0][u] - self.graph.coors[0][v])**2 + 
                  (self.graph.coors[1][u] - self.graph.coors[1][v])**2) for 
                  (u, v) in self.graph.getEdges()]
        self.mdsScaleRatio = d / sum(e) * float(len(e))
        #print d / sum(e) * float(len(e))
        
        if avgLinkage:
            matrix = self.vertexDistance.avgLinkage(self.mdsComponents)
        else:
            matrix = self.vertexDistance
        
        #if self.mds == None: 
        self.mds = orngMDS.MDS(matrix)
        
        if mdsFromCurrentPos:
            if avgLinkage:
                for u, c in enumerate(self.mdsComponents):
                    x = sum(self.graph.coors[0][c]) / len(c)
                    y = sum(self.graph.coors[1][c]) / len(c)
                    self.mds.points[u][0] = x
                    self.mds.points[u][1] = y
            else:
                for u in range(self.graph.nVertices):
                    self.mds.points[u][0] = self.graph.coors[0][u] 
                    self.mds.points[u][1] = self.graph.coors[1][u]
            
        # set min stress difference between 0.01 and 0.00001
        self.minStressDelta = minStressDelta
        self.callbackUpdateCanvas = callbackUpdateCanvas
        self.callbackProgress = callbackProgress
        
        if torgerson:
            self.mds.Torgerson() 

        self.mds.optimize(mdsSteps, orngMDS.SgnRelStress, self.minStressDelta, progressCallback=self.mdsCallback)
        self.mdsUpdateData(self.mdsComponents, self.mds, callbackUpdateCanvas)
        
        if callbackProgress != None:
            callbackProgress(self.mds.avgStress, self.mdsStep)
        
        del self.rotationOnly
        del self.diag_coors
        del self.mdsRefresh
        del self.mdsStep
        #del self.mds
        del self.mdsComponents
        del self.minStressDelta
        del self.callbackUpdateCanvas
        del self.callbackProgress
        del self.mdsType
        del self.mdsScaleRatio
        del self.scalingRatio
        return 0

    def mdsComponentsAvgLinkage(self, mdsSteps, mdsRefresh, callbackProgress=None, callbackUpdateCanvas=None, torgerson=0, minStressDelta = 0, scalingRatio=0, mdsFromCurrentPos=0):
        return self.mdsComponents(mdsSteps, mdsRefresh, callbackProgress, callbackUpdateCanvas, torgerson, minStressDelta, True, scalingRatio=scalingRatio, mdsFromCurrentPos=mdsFromCurrentPos)

    def saveNetwork(self, fn):
        print "This method is deprecated. You should use orngNetwork.Network.saveNetwork"
        name = ''
        try:
            root, ext = os.path.splitext(fn)
            if ext == '':
                fn = root + '.net'
            
            graphFile = file(fn, 'w+')
        except IOError:
            return 1

        graphFile.write('### This file was generated with Orange Network Visualizer ### \n\n\n')
        if name == '':
            graphFile.write('*Network ' + '"no name" \n\n')
        else:
            graphFile.write('*Network ' + str(name) + ' \n\n')


        #izpis opisov vozlisc
        print "e", self.graph.nEdgeTypes
        graphFile.write('*Vertices %8d %8d\n' % (self.graph.nVertices, self.graph.nEdgeTypes))
        for v in range(self.graph.nVertices):
            graphFile.write('% 8d ' % (v + 1))
#            if verticesParms[v].label!='':
#                self.GraphFile.write(str('"'+ verticesParms[v].label + '"') + ' \t')
#            else:
            try:
                label = self.graph.items[v]['label']
                graphFile.write(str('"' + str(label) + '"') + ' \t')
            except:
                graphFile.write(str('"' + str(v) + '"') + ' \t')
            
            x = self.network.coors[0][v]
            y = self.network.coors[1][v]
            #if x < 0: x = 0
            #if x >= 1: x = 0.9999
            #if y < 0: y = 0
            #if y >= 1: y = 0.9999
            z = 0.5000
            graphFile.write('%.4f    %.4f    %.4f\t' % (x, y, z))
            graphFile.write('\n')

        #izpis opisov povezav
        #najprej neusmerjene
        if self.graph.directed:
            graphFile.write('*Arcs \n')
            for (i, j) in self.graph.getEdges():
                if len(self.graph[i, j]) > 0:
                    graphFile.write('%8d %8d %f' % (i + 1, j + 1, float(str(self.graph[i, j]))))
                    graphFile.write('\n')
        else:
            graphFile.write('*Edges \n')
            for (i, j) in self.graph.getEdges():
                if len(self.graph[i, j]) > 0:
                    graphFile.write('%8d %8d %f' % (i + 1, j + 1, float(str(self.graph[i, j]))))
                    graphFile.write('\n')

        graphFile.write('\n')
        graphFile.close()
        
        if self.graph.items != None and len(self.graph.items) > 0:
            (name, ext) = os.path.splitext(fn)
            self.graph.items.save(name + "_items.tab")
            
        if self.graph.links != None and len(self.graph.links) > 0:
            (name, ext) = os.path.splitext(fn)
            self.graph.links.save(name + "_links.tab")

        return 0
    
    def readNetwork(self, fn, directed=0):
        print "This method is deprecated. You should use orngNetwork.Network.readNetwork"
        network = Network(1,directed)
        net = network.readPajek(fn, directed)
        self.setGraph(net)
        self.graph = net
        return net
    
class NetworkClustering():
    random.seed(0)
    
    def __init__(self, network):
        self.net = network
        
        
    def labelPropagation(self, results2items=0, resultHistory2items=0):
        """Label propagation method from Raghavan et al., 2007"""
        
        vertices = range(self.net.nVertices)
        labels = range(self.net.nVertices)
        lblhistory = []
        #consecutiveStop = 0
        for i in range(1000):
            random.shuffle(vertices)
            stop = 1
            for v in vertices:
                nbh = self.net.getNeighbours(v)
                if len(nbh) == 0:
                    continue
                
                lbls = [labels[u] for u in nbh]
                lbls = [(len(list(c)), l) for l, c in itertools.groupby(lbls)]
                m = max(lbls)[0]
                mlbls = [l for c, l in lbls if c >= m]
                lbl = random.choice(mlbls)
                
                if labels[v] not in mlbls: stop = 0
                labels[v] = lbl
                
            lblhistory.append([str(l) for l in labels])
            # if stopping condition might be satisfied, check it
            if stop:
                for v in vertices:
                    nbh = self.net.getNeighbours(v)
                    if len(nbh) == 0: continue
                    lbls = [labels[u] for u in nbh]
                    lbls = [(len(list(c)), l) for l, c in itertools.groupby(lbls)]
                    m = max(lbls)[0]
                    mlbls = [l for c, l in lbls if c >= m]
                    if labels[v] not in mlbls: 
                        stop = 0
                        break
                if stop: break
                    
        if results2items and not resultHistory2items:
            attrs = [orange.EnumVariable('clustering label propagation', values=list(set([l for l in lblhistory[-1]])))]
            dom = orange.Domain(attrs, 0)
            data = orange.ExampleTable(dom, [[l] for l in lblhistory[-1]])
            self.net.items = data if self.net.items == None else orange.ExampleTable([self.net.items, data])
        if resultHistory2items:
            attrs = [orange.EnumVariable('c'+ str(i), values=list(set([l for l in lblhistory[0]]))) for i,labels in enumerate(lblhistory)]
            dom = orange.Domain(attrs, 0)
            # transpose history
            data = map(list, zip(*lblhistory))
            data = orange.ExampleTable(dom, data)
            self.net.items = data if self.net.items == None else orange.ExampleTable([self.net.items, data])

        return labels