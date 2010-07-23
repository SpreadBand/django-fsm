#!/usr/bin/env python
"""
Generate a NetworkX DiGraph from a python source code

	Each classes generate a DiGraph.
	Each functions generate an edge between the source and the target.

	That implementation is composed of two compiler.visitor.ASTVisitor.
"""
__author__ = """Thomas Dulu, thomas@spreadband.com"""
__date__ = "$Date: 2010-07-23 12:48:10 -0600 (Fry, 23 Jul 2010) $"
__credits__ = """"""
__revision__ = "$Revision: 1 $"


import compiler, ast

import matplotlib.pyplot
import networkx

class MyVisitorOfClasses(compiler.visitor.ASTVisitor):
     """
     This Visitor will separate each classes from the source for rendering a Digraph.
     It takes a file path in parameters and returns a list of Digraph.
     """
     def __init__(self,filename):
          compiler.visitor.ASTVisitor.__init__(self)
	  self.arbre = compiler.parseFile(filename)
	  self.graphes = {}

     def analyze(self):
	  compiler.walk(self.arbre,self)
	  return self.graphes

     def visitClass(self,classe):
	  self.graphes[classe.name] = MyVisitorOfFunction(classe).analyze()

class MyVisitorOfFunction(compiler.visitor.ASTVisitor):
     """
     This Visitor will fill up a DiGraph with each elements composing the class.
     It takes an empty DiGraph in parameters and returns a finished DiGraph.
     """
     def __init__(self, arbre):
          compiler.visitor.ASTVisitor.__init__(self)
          self.graph = networkx.DiGraph()
	  self.arbre = arbre

     def analyze(self):
          """
	  Analyze the constructed DiGraph for replacing '*' by all nodes.
	  """
          compiler.walk(self.arbre, self)

          for node in self.graph.nodes():
               if node == "*":
                    for depart in self.graph.nodes():
                         if depart != node:
                              for arrivee in self.graph.neighbors(node):
                                   self.graph.add_edge(depart, arrivee)
                    self.graph.delete_node(node)
       
          for edge in self.graph.edges():
               print edge

          return self.graph

     def visitFunction(self, node):
          nodes = {}
          if node.decorators == None:
               return

	  for dec in node.decorators:
               if not hasattr(dec, 'node') or dec.node.name != "transition":
	            continue

	       from_field = dec.args[0].expr
               to_field = dec.args[1].expr
               if hasattr(from_field, "nodes"):
                    from_field = [x.value for x in from_field]
               else:
                    from_field = [from_field.value]
               to_field = to_field.value
               
               for field in from_field:
                    if not self.graph.has_node(field):
                         self.graph.add_node(field)
               if not self.graph.has_node(to_field):
                    self.graph.add_node(to_field)

               for depart in from_field:
                    self.graph.add_edge(depart, to_field)

if __name__ == '__main__':
      import sys
      from networkx import to_agraph

      if len(sys.argv) == 2:
           fichier = sys.argv[1]
      else:
	   print "Please give a file path"
	   sys.exit(1)	   

      visi = MyVisitorOfClasses(fichier)
      graphs = visi.analyze()

      for name, graph in graphs.items():
	      graphviz = to_agraph(graph)
	      graphviz.draw("%s.png" % name, prog="dot")
	      print "Graphe", name, "drawn in", format
