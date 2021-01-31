import math
import matplotlib.pyplot as plt
from networkx import *
import networkx.utils
import random
import os
import tqdm as tqdm
import pickle
import numpy as np

N=50
m=2

n=20
p=0.01

G=barabasi_albert_graph(N,m)


#nx.draw(G, node_color='r', with_labels=True)
#plt.show()

lamb = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
paths={}

#select number of initially removed nodes
x = math.floor(N*p)
if x == 0:
    x=1

inrem=[]



for i in range(n):
    nodedeck=list(range(0,N))
    rem=[]
    for j in range(0,x):
        random.shuffle(nodedeck)      
        rem.append(nodedeck.pop())


    inrem.append(rem)


for i in tqdm.tqdm(G):
    for j in G:
        if i<j:
            paths[(i,j)]=[p for p in all_shortest_paths(G,i,j)]


def flowcount(G):

    global paths
    global ded0

    Gr = G.copy()

    for i in Gr:
        Gr.nodes[i]['load']=0

    for i in Gr:
        for j in Gr:
            if i > j:
                for shopat in paths[(j,i)]:
                    if (any(x in ded0 for x in shopat)):
                        paths[(j,i)] = [p for p in all_shortest_paths(Gr,j,i)]
                        patnum= len(paths[(j,i)])
                        for shopat2 in paths[(j,i)]:
                            for k in shopat2[:-1]:
                                Gr.nodes[k]['load']=Gr.nodes[k]['load']+(1/patnum)
                    
                        break
                    else:
                        patnum= len(paths[(j,i)])
                        for k in shopat[:-1]:
                            Gr.nodes[k]['load']=Gr.nodes[k]['load']+(1/patnum)

            elif i < j:
                for shopat in paths[(i,j)]:
                    if (any(x in ded0 for x in shopat)):
                        paths[(i,j)] = [p for p in all_shortest_paths(Gr,i,j)]
                        patnum= len(paths[(i,j)])
                        for shopat2 in paths[(i,j)]:
                            for k in shopat2[1:]:
                                Gr.nodes[k]['load']=Gr.nodes[k]['load']+(1/patnum)
                    
                        break
                    else:
                        patnum= len(paths[(i,j)])
                        for k in shopat[1:]:
                            Gr.nodes[k]['load']=Gr.nodes[k]['load']+(1/patnum)

    return Gr

def initg(G,lam,initrem):

    global ded
    global ded0

    #we have selected the number of ndoes that will be removed

    #Lets find initial capacity for each node

    #We set initial load to zero for all nodes

    #We are finding initial load

    #We are finding capacity and setting L0=Li

    for i in G:
        
        G.nodes[i]['inload']=G.nodes[i]['load']
        G.nodes[i]['cap']=G.nodes[i]['inload']*lam


    #INITIATION OF THE CASCADE

    Gr = G.copy()
    
    inirem=[]
    for i in initrem:

        if len(Gr[i])==0:
            pass
            
        else:
            distload = Gr.nodes[i]['load']/len(Gr[i])

            for j in Gr[i]:
                Gr.nodes[j]['load']=Gr.nodes[j]['load']+distload
        
        Gr.remove_node(i)
        ded0.append(i)

    ded.append(inirem)
    

    components = sorted(connected_components(Gr))
    if len(components)>1:
        for n in components[1:]:
            for m in list(n):
                Gr.remove_node(m)
    

    #We check if we have created some components and remove them if yes

    components = sorted(connected_components(Gr))

    if len(components)>1:
        for n in components[1:]:
            for m in list(n):
                Gr.remove_node(m)

    return Gr

def propag(G):
    global ded
    global ded0

    Gr = G.copy()

    #We first remove the overloaded nodes
    x=[]
    for i in Gr:
        if Gr.nodes[i]['load']>Gr.nodes[i]['cap']:
            x.append(i)
            ded0.append(i)

    ded.append(x)

    for i in x:
        if len(Gr[i])==0:
            pass
            
        else:
            distload = Gr.nodes[i]['load']/len(Gr[i])

            for j in Gr[i]:
                Gr.nodes[j]['load']=Gr.nodes[j]['load']+distload
        
        Gr.remove_node(i)
        ded0.append(i)

    #Now we check if the giant component is harmed

    components = sorted(connected_components(Gr))
    if len(components)>1:
        for n in components[1:]:
            for m in list(n):
                Gr.remove_node(m)
    
    #We removed all components except the largest one

    return Gr



data=[]
ded0=[]

G = flowcount(G)

for lam in tqdm.tqdm(lamb):
    print('Starting: '+str(lam))
    lamlist=[]
    for m in tqdm.tqdm(range(n)):
        
        W=[]
        ded=[]
        
            
        holddata=[]
        ded0=[]
        W.append(G)
        W.append(initg(G,lam, inrem[m]))

        t=1

        print(ded0)
        while len(W[t]) != len(W[t-1]):
            W.append(propag(W[t]))

            print('W['+str(t)+']')
            print(str(len(W[t]))+' nodes left')
            
            t=t+1
            
        holddata.append(W)
        holddata.append(ded)
        
        lamlist.append(holddata)
    data.append(lamlist)

filename = 'data'
outfile = open(filename,'wb')
pickle.dump(data,outfile)
outfile.close()


ratios=[]
for i in range(len(lamb)):
    y=0
    for j in range(n):
        x = len(data[i][j][0][-1])
        x = x / N
        y=y+x
    y=y/n
    ratios.append(y)

print(ratios)

plt.plot(lamb,ratios)

plt.title('Motter Simulation N='+str(N)+'n='+str(n))
plt.xlabel('Capacity Coefficient')
plt.ylabel('G`/G')

plt.savefig('Motter_N='+str(N)+'.pdf')
