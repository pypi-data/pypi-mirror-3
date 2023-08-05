from Products.CMFCore.utils import getToolByName
from tempfile import mktemp
import os
import sys
from os.path import basename, splitext, join
from config import bin_search_path, DOT_EXE


# bin_search() and getPOT() are copied form PortalTranforms 
# Owners of PortalTransforms own the copyright for these 2 functions
class MissingBinary(Exception): pass

def bin_search(binary):
    """search the bin_search_path  for a given binary
    returning its fullname or None"""
    result = None
    mode   = os.R_OK | os.X_OK
    for p in bin_search_path:
        path = join(p, binary)
        if os.access(path, mode) == 1:
            result = path
            break
    else:
        raise MissingBinary('Unable to find binary "%s"' % binary)
    return result


# Rank states according to indegree, outdegree, and name.  Returns a list
# of states in an order which *hopefully* will make an nice graph.
def rankstates( states, transitions, debugmsgs=None):
    indegree = {}   # number of edges in to each state
    outdegree = {}  # number of edges out of each state
    statepairs = [] # tuples of (in-degree/out-degree, state)

    # Initialize degree hashes.
    for s in states:
        myId = s.getId()
        indegree[myId] = 0
        outdegree[myId] = 0

    # Compute degrees.
    for sourceId,destId in transitions:
        indegree[sourceId] += 1
        outdegree[destId] += 1

    # Compute ranks.
    for s in states:
        myId = s.getId()

        # Initialize rank.
        ins = indegree[myId]
        outs = outdegree[myId]
        rank = abs(outs - ins)

        # Adjust rank with crazy scoring functions.
        if myId.lower().find( 'priv') >= 0:
            rank = rank - 5
        if myId.lower().find( 'pub') >= 0:
            rank = rank + 5

        # Debugging info.
        if debugmsgs is not None:
            m = '# node %s has indegree %d, outdegree %d, rank %d'
            m = m % (myId, indegree, outdegree, rank)
            debugmsgs.append( m)

        # Store rank.
        statepairs.append( (rank, s))

    # Sort states by rank.
    statepairs.sort()
    newstates = []
    for r,s in statepairs:
        newstates.append( s)

    # Done.
    return newstates
    

def getPOT(self, wf_id=""):
    """ get the pot, copy from:
         "dcworkfow2dot.py":http://awkly.org/Members/sidnei/weblog_storage/blog_27014
        and Sidnei da Silva owns the copyright of the this function
    """
    out = []
    transitions = {}

    # Get states.
    if wf_id:
        w_tool = getToolByName(self, 'portal_workflow')
        wf = getattr(w_tool, wf_id)
    else:
        wf = self
    states = wf.states.objectValues()

    # Start Graph
    out.append('digraph "%s" {' % wf.title)

    # Get states and sort by out-degree / (in-degree+1).
    for s in states:

        # Get transitions.
        for t in s.transitions:
            try:
                trans = wf.transitions[t]
            except KeyError:
                out.append('# transition %s from state %s is missing'
                           % (t, s.getId()))
                continue

            key = (s.getId(), trans.new_state_id)
            value = transitions.get(key, [])
            value.append(trans.actbox_name)
            transitions[key] = value

    # Order states and add them to graph.
    states = rankstates( states, transitions)
    for s in states:
        out.append('%s [shape=box,label="%s (%s)"];'
                   % (s.getId(), s.title, s.getId().capitalize()))

    # Add transitions.
    for k, v in transitions.items():
        out.append('%s -> %s [label="%s"];' % (k[0], k[1],
                                           ', '.join(v)))

    # Finish graph.
    out.append('}')
    return '\n'.join(out)

def getGraph(self, wf_id="", format="gif", REQUEST=None):
    """show a workflow as a graph, copy from:
"OpenFlowEditor":http://www.openflow.it/wwwopenflow/Download/OpenFlowEditor_0_4.tgz
    """
    pot = getPOT(self, wf_id)
    infile = mktemp('.dot')
    f = open(infile, 'w')
    f.write(pot)
    f.close()
    outfile = mktemp('.%s' % format)
    os.system('%s -T%s -o %s %s' % (bin_search(DOT_EXE), format, outfile, infile))
    out = open(outfile, 'rb')
    result = out.read()
    out.close()
    os.remove(infile)
    os.remove(outfile)
    return result
