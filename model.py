import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import math
xrespb = 1/2
maxeinflussB = 1
maxeinflussA = 1/2
negativeinfluss = 0.01

bounded = 2.5


class Agent:
    def __init__(self, i, awareness, responsibility, bereitschaft, openness):
        self.awareness = awareness
        self.responsibility = responsibility
        self.bereitschaft = bereitschaft
        self.i = i
        self.openness = openness
        self.lastupdate = 0
    
        
   # A trifft auf B

    def update(self, other):
        self.lastupdate = 0
        op = (self.openness)/10
        if isinstance(other, AgentB) == True:
            self.awareness = self.awareness + op * maxeinflussB 
            self.awareness = max(0,min(self.awareness,10))
            self.responsibility = self.responsibility + (op* maxeinflussB * xrespb) 
            self.responsibility = max(0,min(self.responsibility,10))
        
        
                
        # A trifft auf A 
        
        elif isinstance(other, Agent) == True:
            if (other.bereitschaft - self.bereitschaft) >= -bounded and (other.bereitschaft - self.bereitschaft) < 0:
                self.responsibility = self.responsibility - op* maxeinflussA
                self.awareness = self.awareness - xrespb* op* maxeinflussA
            if (other.bereitschaft - self.bereitschaft) <= bounded and (other.bereitschaft - self.bereitschaft) > 0:
                self.responsibility = self.responsibility + op* maxeinflussA
                self.awareness = self.awareness + xrespb * op* maxeinflussA 
            self.responsibility = max(0,min(self.responsibility,10))
            self.awareness = max(0,min(self.awareness,10))

           
        self.bereitschaft = (self.awareness * self.responsibility)**0.5
        self.bereitschaft = max(0,min(self.bereitschaft,10))

    def update_non_interaction(self):
         self.lastupdate = self.lastupdate + 1
         if self.lastupdate > 4:
            self.awareness = self.awareness - negativeinfluss
            self.awareness = max(0,min(self.awareness,10))
            self.bereitschaft = (self.awareness * self.responsibility)**0.5
            self.bereitschaft = max(0,min(self.bereitschaft,10))
             


class AgentB:
     def __init__(self, i):
            self.i = i
class Model_with_network:
    def __init__(self, n_agents, node_degree, rewiring_prob, notopen_Anzahl, anzahl_ABlink, n_agentsb, frequence, seed): 
        np.random.seed(seed)
        # Assign Parameters 
        
        self.n_agents = n_agents
        self.node_degree = node_degree   
        self.rewiring_prob = rewiring_prob
        self.notopen_Anzahl = notopen_Anzahl
        self.anzahl_ABlink = anzahl_ABlink
        self.n_agentsb = n_agentsb
        self.frequence = frequence

        # initialise agents
        
        listAgents = []
        for i in range(self.n_agents):
            if i <= self.notopen_Anzahl:
                ag = Agent(i = i, awareness = 0, responsibility = 0, bereitschaft = 0, openness = 0)
            else:
                ag = Agent(i = i, awareness = np.random.uniform() * 10,
                                 responsibility= np.random.uniform() * 10,
                            bereitschaft = np.random.uniform() * 10, openness = np.random.uniform() * 10)
            listAgents.append (ag)
        np.random.shuffle(listAgents)
        self.agents = listAgents
        ids = [ag.i for ag in self.agents]
        self.agentsdict = dict (zip(ids,self.agents))
        self.network = nx.watts_strogatz_graph(self.n_agents, self.node_degree, self.rewiring_prob, seed)
        self.network.edges
        
        
        # die Agenten B haben erstmal keine Eigenschaften, sondern dienen nur als Sender
        
        self.agentsb = [AgentB (i = i + self.n_agents) for i in range(self.n_agentsb)]
        idsb = [ag.i for ag in self.agentsb]
        self.agentsbdict = dict (zip(idsb,self.agentsb))
        #self.networkb = nx.watts_strogatz_graph(self.n_agentsb, self.node_degree, self.rewiring_prob)
        
        # Graph für Agent und Agent B 
        self.g = nx.Graph()
        self.g.add_nodes_from(range(0, len(self.agents) + len(self.agentsb)))   
        for i in range (self.anzahl_ABlink) :
            u = np.random.choice(self.agents)
            v = np.random.choice(self.agentsb)
            self.g.add_edge(u.i, v.i)
        self.g.add_edges_from (self.network.edges, weight = 0.3) 
            
        self.agentsalldict = self.agentsdict.copy()
        self.agentsalldict.update(self.agentsbdict)        
            
    def update_step(self):
        ids = [ag.i for ag in self.agents]
        np.random.shuffle(ids)  # shuffles the entries in the id-list (in-place)
        # loop through all the agents (in random order) and let them (potentially) update their opinions.
        for i in ids:
            # select interaction partners:
            ag = self.agents[i]  # listener
            if np.random.random() <= self.frequence:
                potentialnachbar = list(self.g.neighbors(ag.i))
                if not potentialnachbar == []: 
                    idsspeaker = np.random.choice(potentialnachbar)
                    speaker = self.agentsalldict[idsspeaker]    # speaker randomly selected NEIGHBOUR 

                    ag.update(other= speaker)
            else:
                ag.update_non_interaction()

m = Model_with_network (n_agents= 100, node_degree = 6, rewiring_prob = 0.1, notopen_Anzahl = 10, anzahl_ABlink = 20, n_agentsb = 50, frequence = 0.5, seed = 6)
