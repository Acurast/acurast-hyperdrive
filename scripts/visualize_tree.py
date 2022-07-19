import sys
import graphviz
from pytezos import pytezos

client = pytezos.using(shell=sys.argv[1])


def visualize(nodes, states, root):
    graph_attr = {
        "labelloc": "t",
        "fontcolor": "black",
        "fontname": "Liberation Mono",
        "bgcolor": "#ffffff",
        "margin": "0",
    }  # graph attributes

    node_attr = {
        "color": "black",
        "fontcolor": "black",
        "fontname": "Liberation Mono",
        "fontsize": "10",
        "style": "filled",
        "fillcolor": "orange",
        "forcelabels": "true",
    }  # node attributes

    edge_attr = {
        "color": "#565656",
        "fontcolor": "#565656",
        "fontname": "Liberation Mono",
        "fontsize": "8",
    }  # edge attributes

    dot = graphviz.Digraph(
        graph_attr=graph_attr, node_attr=node_attr, edge_attr=edge_attr
    )

    for state in states:
        node_attr = {
            "shape": "box",
            "label": f"""<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
                            <TR>
                                <TD COLSPAN="3"><B>{state}</B></TD>
                            </TR>
                            <TR>
                                <TD COLSPAN="3"><B>Value: </B>{states[state]}</TD>
                            </TR>
                        </TABLE>>""",
        }
        dot.node(name=state, **node_attr)

    for node in nodes:
        node_attr = {
            "label": f"""<<B>{node}</B>>""",
            "fillcolor": "#82dfb0" if node == root else "#70a6ff",
            "color": "red" if node == root else "black",
        }
        dot.node(name=node, **node_attr)

    link(dot, root, nodes)

    return dot


def link(dot, hash, nodes):
    if hash in nodes:
        node = nodes[hash]

        dot.edge(
            hash,
            node["left"]["node"],
            label=f'({node["left"]["key"]["length"]}) {node["left"]["key"]["data"]}',
        )
        link(dot, node["left"]["node"], nodes)

        dot.edge(
            hash,
            node["right"]["node"],
            label=f'({node["right"]["key"]["length"]}) {node["right"]["key"]["data"]}',
        )
        link(dot, node["right"]["node"], nodes)


def pp_bytes(b):
    return b.hex()


tree = client.contract(sys.argv[2]).storage()["tree"]

states = {}
for state in tree["states"]:
    states[pp_bytes(state)] = pp_bytes(tree["states"][state])

nodes = {}
for node in tree["nodes"]:
    left = {**tree["nodes"][node][0], "node": pp_bytes(tree["nodes"][node][0]["node"])}
    right = {**tree["nodes"][node][1], "node": pp_bytes(tree["nodes"][node][1]["node"])}

    nodes[node.hex()] = {"left": left, "right": right}

visualize(nodes, states, pp_bytes(tree["root"])).render(
    filename="merkle_tree", format="svg", view=False, cleanup=True
)

print(f"total states: {len(states)}")
