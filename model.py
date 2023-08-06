# Import der benötigten Bibliotheken
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import math

# Import von einigen Parametern für das Modell
xrespb = 1/2 # Relativer Einfluss auf Verantwortungsbewusstsein (A-B-Interaktion) und relativer Einfluss auf Problembewusstsein (A-A-Interaktion) 
maxeinflussB = 1 # Maximaler Einfluss von B-Agent auf A-Agent, d.h. auf dessen Problembe-wusstsein.
maxeinflussA = 1/2 # Maximaler Einfluss von A-Agent auf A-Agent, d.h. auf dessen Verantwor-tungsbewusstsein.
negativeinfluss = 0.01 # Negativer Einfluss auf das Problembewusstsein bei keiner Interaktion
bounded = 2.5 # Eingeschränkter Vertrauensradius

# Definition der Klasse "Agent" für A-Agenten
class Agent:
    def __init__(self, i, awareness, responsibility, bereitschaft, openness):
        self.awareness = awareness
        self.responsibility = responsibility
        self.bereitschaft = bereitschaft
        self.i = i
        self.openness = openness
        self.lastupdate = 0
    
        
   # Aktualisierung des Verantwortungs- und Problembewusstseins, wenn A-Agent auf A- oder B-Agenten trifft
    def update(self, other):
        self.lastupdate = 0
        op = (self.openness)/10

        # A-Agent trifft auf B-Agenten
        if isinstance(other, AgentB) == True:
            self.awareness = self.awareness + op * maxeinflussB 
            self.awareness = max(0,min(self.awareness,10))
            self.responsibility = self.responsibility + (op* maxeinflussB * xrespb) 
            self.responsibility = max(0,min(self.responsibility,10))
        
        # A-Agent trifft auf A-Agenten 
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

    # Aktualisierung des Problembewusstsein, wenn A-Agent nicht interagiert
    def update_non_interaction(self):
         self.lastupdate = self.lastupdate + 1
         if self.lastupdate > 4:
            self.awareness = self.awareness - negativeinfluss
            self.awareness = max(0,min(self.awareness,10))
            self.bereitschaft = (self.awareness * self.responsibility)**0.5
            self.bereitschaft = max(0,min(self.bereitschaft,10))
             
# Definition der Klasse "AgentB" für B-Agenten
class AgentB:
     def __init__(self, i):
            self.i = i
         
# Definition der Klasse für das Modell mit Netzwerk
class Model_with_network:
    def __init__(self, n_agents, node_degree, rewiring_prob, notopen_Anzahl, anzahl_ABlink, n_agentsb, frequence, seed): 
        np.random.seed(seed)
        
        # Parameter zuweisen 
        self.n_agents = n_agents #Anzahl A-Agenten
        self.node_degree = node_degree # durchschnittliche Anzahl der Links pro A-Agent
        self.rewiring_prob = rewiring_prob # Umverdrahtungswahrscheinlichkeit
        self.notopen_Anzahl = notopen_Anzahl # Anzahl "unbeeinflussbarer verweigernder" A-Agenten
        self.anzahl_ABlink = anzahl_ABlink # Anzahl Links zwischen A- und B-Agenten
        self.n_agentsb = n_agentsb # Anzahl B-Agenten
        self.frequence = frequence # Interaktionswahrscheinlichkeit

        # A-Agenten initialisieren
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
        
        # B-Agenten initialisieren (haben keine Eigenschaften, sondern dienen nur als Sender)
        self.agentsb = [AgentB (i = i + self.n_agents) for i in range(self.n_agentsb)]
        idsb = [ag.i for ag in self.agentsb]
        self.agentsbdict = dict (zip(idsb,self.agentsb))
      
        
        # Graph für A-Agenten und B-Agenten erstellen
        self.g = nx.Graph()
        self.g.add_nodes_from(range(0, len(self.agents) + len(self.agentsb)))   
        for i in range (self.anzahl_ABlink) :
            u = np.random.choice(self.agents)
            v = np.random.choice(self.agentsb)
            self.g.add_edge(u.i, v.i)
        self.g.add_edges_from (self.network.edges, weight = 0.3) 

        # alle Agenten in einem Dictionary speichern
        self.agentsalldict = self.agentsdict.copy()
        self.agentsalldict.update(self.agentsbdict)  
        
   # Aktualisierung (ein Zeitschritt)     
    def update_step(self):
        ids = [ag.i for ag in self.agents]
        np.random.shuffle(ids)  # mischt die Einträge in der id-Liste (in-place)
        # Schleife durch alle Agenten (in zufälliger Reihenfolge) und (möglicherweise) aktualisieren sie ihre Meinungen.
        for i in ids:
            # Interaktionspartner auswählen:
            ag = self.agents[i]  # Empfänger
            if np.random.random() <= self.frequence:
                potentialnachbar = list(self.g.neighbors(ag.i))
                if not potentialnachbar == []: 
                    idsspeaker = np.random.choice(potentialnachbar)
                    speaker = self.agentsalldict[idsspeaker]    # Sprecher zufällig ausgewählter Nachbar

                    ag.update(other= speaker)
            else:
                ag.update_non_interaction()
                
# Basismodell
m = Model_with_network (n_agents= 100, node_degree = 6, rewiring_prob = 0.1, notopen_Anzahl = 10, anzahl_ABlink = 20, n_agentsb = 50, frequence = 0.5, seed = 6)
