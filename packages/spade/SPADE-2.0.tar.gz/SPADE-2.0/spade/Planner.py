
# encoding: utf-8


import AID
from DF import Service
from Behaviour import EventBehaviour
import content
import copy
import thread
import time
import sys

import Agent

from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import *
from pygraph.algorithms.heuristics.euclidean import *
from pygraph.algorithms.minmax import *
from pygraph.classes.exceptions import NodeUnreachable


class TrustHeuristic:
    def optimize(self, graph):
        self.graph = graph

    def __call__(self,start,end):
        #try:
        return 1 #self.engine.searchService(p).trust
            
'''            ###Dijkstra
            #st,sd = shortest_path(self.graph,start)
            #if end in sd.keys():
            #    return sd[end]
            ###Full search
            #h = Heuristic()
            #path = heuristic_search(self.graph,str(start),str(end),h)
            #result = 0
            #for p in path:
            #    s = self.engine.searchService(p) 
            #    result+=s[0].trust
            #return result
'''
            
class Planner(Agent.Agent):
    """
    Service Planner Agent
    """

    def _setup(self):
        self.wui.start()
        self.servicesdb      = {}
        self.graph           = digraph()
        self._services_mutex = thread.allocate_lock()
        
        self.subscribeToEvent("DF:Service:Register",   self._registerServiceEvent())
        self.subscribeToEvent("DF:Service:UnRegister", self._unregisterServiceEvent())        
        
        composeservice = Service()
        composeservice.setName("Compose_Service")
        composeservice.addP("kb")
        composeservice.addP("goal")
        composeservice.addQ("composed_plan")
        self.registerService(composeservice, self._composePlan)
        
    class _registerServiceEvent(EventBehaviour):
        def _process(self):
            self.myAgent.DEBUG("Received DF:Service:Register Event")
            msg = self._receive(True)
            event = msg.getTag("event")
            items=None
            for child in event.getChildren():
                if child.getAttr("node")=="DF:Service:Register":
                    items = child.getChildren()
                    break
            for item in items:
                self.myAgent.DEBUG("Service extracted")
                node = item.getPayload()[0]
                co = content.Node2CO(node)
                dad = DF.DfAgentDescription(co=co)
                service = DF.Service(dad=dad)
                service.trust=0
                name = service.getName()
                
                self._services_mutex.acquire()
                self.servicesdb[name] = service
                self.graph.add_node(name)
                for n,s in self.servicesdb.items():
                    if str(s.getQ()) == str(service.getP()):
                            wt = service.trust #int(s[s.find("(")+1:s.find(")")])
                            self.graph.add_edge((n,name) , wt=wt)
                    elif s.getP() == service.getQ():
                            wt = service.trust #int(s[s.find("(")+1:s.find(")")])
                            self.graph.add_edge((name,n) , wt=wt)
                            
                self._services_mutex.release()
                
    class _unregisterServiceEvent(EventBehaviour):
        def _process(self):
            self.myAgent.DEBUG("Received DF:Service:UnRegister Event")
            msg = self._receive(True)
            event = msg.getTag("event")
            items=None
            for child in event.getChildren():
                if child.getAttr("node")=="DF:Service:UnRegister":
                    items = child.getChildren()
                    break
            for item in items:
                self.myAgent.DEBUG("Service extracted")
                node = item.getPayload()[0]
                co = content.Node2CO(node)
                dad = DF.DfAgentDescription(co=co)
                service = DF.Service(dad=dad)
                name = service.getName()

                self._services_mutex.acquire()
                del self.servicesdb[name]
                self.graph.del_node(name)
                for e in self.graph.edges():
                    if e[0] == name or e[1] == name: self.graph.del_edge(e)
                self._services_mutex.release()

    def searchService(name=None,P=None,Q=None):
        results=[]
        for s in self.servicesdb.items():
            if name:
                if s.getName()!=name: continue
            if P:
                if P != s.getP(): continue
            if Q:
                if Q != s.getQ(): continue
            results.append(s)
        return results
    
    def _composePlan(kb=[],goal=None):

        t1 = time.time()
        #search for end node and start nodes
        end = None
        start = []
        for s in self.servicesdb.values():
            if goal in s.getQ():
                end = s
            matches=True
            for p in s.getP():
                if not p in kb:
                    matches=False
            if matches: start.append(s)

        #make heuristic search
        paths = list()
        h = TrustHeuristic()
        h.optimize(self.graph)
        for end_node in end:
            for start_node in start:
                try:
                   result = heuristic_search(self.graph,str(start_node),str(end_node.name),h)
                   paths.append(result)
                except Exception, e:
                    self.DEBUG("No path from "+ str(start_node) + " to " + end_node.name,"warn","plan")
                    
        if len(paths)==0: return {"composed_plan":None}
        else:
            #choose best plan (with best reputation)
            plan = None
            reputation = None
            for p in paths:
                l = len(p)
                t = 0
                for s in p:
                    servs = self.searchService(name=s)
                    if len(servs)>0:
                        serv = servs[0]
                        t += (500 - serv.trust)
                if plan == None or reputation < (t-l):
                    plan = p
                    reputation = t-l


        if len(plan)==0: return {"composed_plan":None}

        searchP= self.searchService(name=plan[0])
        if len(searchP)>0: P = searchP[0].getP()
        else: return {"composed_plan":None}

        services = []
        for n in plan:
            s = self.searchService(name=n)
            if len(s)>0: services.append(s[0].asContentObject())
            else: return {"composed_plan":None}

        self.DEBUG("Plan composed in " + str(time.time()-t1) + " seconds")

        return {"composed_plan":{'P':P, 'Q':goal, 'services':services, 'reputation':reputation}}


if __name__ == "__main__":
        if len(sys.argv) < 2:
                host = "127.0.0.1"
        else:
                host = sys.argv[1]
        a = Planner("planner@"+host, "secret")
        a.setDebugToScreen()
        a.start()

        alive = True
        while alive:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                alive=False
        a.stop()
        sys.exit(0)
