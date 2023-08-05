from Products.CMFCore.utils import getToolByName
from tempfile import mktemp
import os
import sys
from os.path import basename, splitext, join
from config import bin_search_path, DOT_EXE
from zope.i18n import translate


# following 2 method is copied form PortalTranforms 
# Owners of PortalTransforms own the copyright of these 2 functions
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


def getObjectTitle(object, REQUEST=None):
    """Get a state/transition title to be displayed in the graph
    """

    if REQUEST is not None:
        only_ids = REQUEST.get('only_ids', False)
        translate = REQUEST.get('translate', False)
    else:
        only_ids = False
        translate = False

    id = object.getId()
    title = object.title

    if translate:
        id = object.translate(default=id, msgid=id)
        title = object.translate(default=title, msgid=title)
    if not title or only_ids:
        title = id
    else:
        title = '%s\\n(%s)'%(title, id)
    return title

def getPOT(self, wf_id="", REQUEST=None):
    """ get the pot, copy from:
         "dcworkfow2dot.py":http://awkly.org/Members/sidnei/weblog_storage/blog_27014
        and Sidnei da Silva owns the copyright of the this function
    """
    out = []
    transitions = {}

    if wf_id:
        w_tool = getToolByName(self, 'portal_workflow')
        wf = getattr(w_tool, wf_id)
    else:
        wf = self

    if REQUEST is None:
        REQUEST = self.REQUEST

    out.append('digraph "%s" {' % wf.title)
    transitions_with_init_state = []
    for s in wf.states.objectValues():
        s_id = s.getId()
        s_title = getObjectTitle(s, REQUEST)
        out.append('%s [shape=box,label="%s",style="filled",fillcolor="#ffcc99"];' % (s_id, s_title))
        for t_id in s.transitions:
            transitions_with_init_state.append(t_id)
            try:
                t = wf.transitions[t_id]
            except KeyError:
                out.append(('# transition %s from state %s '
                            'is missing' % (t_id, s_id)))
                continue

            new_state_id = t.new_state_id
            # take care of 'remain in state' transitions
            if not new_state_id:
                new_state_id = s_id
            key = (s_id, new_state_id)
            value = transitions.get(key, [])
            t_title = getObjectTitle(t, REQUEST)
            value.append(t_title)
            transitions[key] = value

    # iterate also on transitions, and add transitions with no initial state
    for t in wf.transitions.objectValues():
        t_id = t.getId()
        if t_id not in transitions_with_init_state:
            new_state_id = t.new_state_id
            if not new_state_id:
                new_state_id = None
            key = (None, new_state_id)
            value = transitions.get(key, [])
            t_title = getObjectTitle(t, REQUEST)
            value.append(t_title)
            transitions[key] = value

    for k, v in transitions.items():
        out.append('%s -> %s [label="%s"];' % (k[0], k[1],
                                               ',\\n'.join(v)))

    out.append('}')
    return '\n'.join(out)

def getGraph(self, wf_id="", format="png", REQUEST=None):
    """show a workflow as a graph, copy from:
"OpenFlowEditor":http://www.openflow.it/wwwopenflow/Download/OpenFlowEditor_0_4.tgz
    """
    pot = getPOT(self, wf_id, REQUEST)
    try:
        encoding = self.portal_properties.site_properties.getProperty('default_charset', 'utf-8')
    except AttributeError:
        # no portal_properties or site_properties, fallback to:
        encoding = self.management_page_charset.lower()
    pot = pot.encode(encoding)
    infile = mktemp('.dot')
    f = open(infile, 'w')
    f.write(pot)
    f.close()
    
    if REQUEST is None:
        REQUEST = self.REQUEST
    response = REQUEST.RESPONSE
        
    if format != 'dot':
        outfile = mktemp('.%s' % format)
        os.system('%s -T%s -o %s %s' % (bin_search(DOT_EXE), format, outfile, infile))
        out = open(outfile, 'rb')
        result = out.read()
        out.close()
        os.remove(outfile)
        response.setHeader('Content-Type', 'image/%s' % format)
    else:
        result = open(infile, 'r').read()
        filename = wf_id or self.getId()
        response.setHeader('Content-Type', 'text/x-graphviz')
        response.setHeader('Content-Disposition',
                           'attachment; filename=%s.dot' % filename)
        
    os.remove(infile)
    return result



