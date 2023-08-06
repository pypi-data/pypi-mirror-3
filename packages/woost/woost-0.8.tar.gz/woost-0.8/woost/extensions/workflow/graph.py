#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cStringIO import StringIO
from subprocess import Popen, PIPE
from cocktail.translations import translations

p = Popen(["which", "dot"], stdout=PIPE)
graphviz_command = p.communicate()[0].replace("\n", "") or None
del p

def workflow_graph(states):
    """Renders the graph for the given workflow.
    
    :param states: The root states to include in the graph.
    :type states: `State`

    :return: DOT markup for the given workflow, to be rendered with Graphviz.
    :rtype: str
    """
    source = ["digraph workflow {"]
    source.append("\trankdir=LR;")
    source.append("\tnode [shape=ellipse];")
    source.append("\tedge [arrowsize=0.7];")
    
    def state_name(state):
        return "state%d" % state.id
    
    visited = set()

    def traverse(state):
        if state in visited:
            return
        
        visited.add(state)
        
        source.append(
            '\t%s [label="%s", id="%d"];'
            % (state_name(state), translations(state), state.id)
        )

        for transition in state.outgoing_transitions:
            if transition.target_state is not None:
                source.append('\t%s -> %s [label="%s", id="%d"];' % (
                    state_name(state),
                    state_name(transition.target_state),
                    transition.title,
                    transition.id
                ))
            traverse(transition.target_state)

    for state in states:
        traverse(state)

    source.append("}")
    return "\n".join(source)

def render_graph(markup, dest, format, command = graphviz_command):
    """Writes the specified DOT markup to the indicated file."""
    
    dest_is_path = isinstance(dest, basestring)    
    
    cmd = [command, "-T", format]
    if dest_is_path:
        cmd.append("-o")
        cmd.append(dest)

    proc = Popen(
        cmd,
        stdin = PIPE,
        stdout = PIPE if not dest_is_path else None
    )    
    stdout, stderr = proc.communicate(markup.encode("utf-8"))
    
    if not dest_is_path:
        dest.write(stdout)


if __name__ == "__main__":
    
    import sys
    import os
    from cocktail.translations import set_language
    from woost.extensions.workflow.state import State
    import testproject.models

    dest = sys.stdout if len(sys.argv) < 2 else sys.argv[1]
    format = None
    
    if len(sys.argv) >= 3:
        format = sys.argv[2]
    elif isinstance(dest, basestring):
        format = os.path.splitext(dest)[1]
        if format:
            format = format[1:]

    if not format:
        format = "svg"

    set_language("ca")
    working = State.require_instance(qname = "testproject.working_state")
    graph = workflow_graph(working)
    render_graph(graph, dest, format)

