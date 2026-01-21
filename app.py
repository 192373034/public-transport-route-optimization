import streamlit as st
import networkx as nx
import heapq
import matplotlib.pyplot as plt

# =====================================================
# MODULE 1: TRANSPORT NETWORK GRAPH MODELING
# =====================================================
def build_transport_graph():
    G = nx.Graph()

    # (Source, Destination, Time, Cost, Distance)
    routes = [
        ("A", "B", 10, 5, 3),
        ("A", "C", 15, 4, 5),
        ("B", "D", 12, 6, 4),
        ("C", "D", 8, 3, 2),
        ("C", "E", 10, 5, 4),
        ("D", "E", 6, 2, 1),
        ("D", "F", 15, 6, 5),
        ("E", "F", 8, 3, 2),
    ]

    for u, v, time, cost, distance in routes:
        G.add_edge(u, v, time=time, cost=cost, distance=distance)

    return G


# =====================================================
# GRAPH VALIDATION (MODULE 1)
# =====================================================
def validate_graph(graph):
    if graph.number_of_nodes() == 0:
        return False, "Graph has no nodes"

    if graph.number_of_edges() == 0:
        return False, "Graph has no edges"

    for u, v, data in graph.edges(data=True):
        if "time" not in data or "cost" not in data or "distance" not in data:
            return False, f"Missing weights on edge {u} - {v}"

    return True, "Graph validation successful. Module-1 output is complete and ready to be used by Module-2."


# =====================================================
# MODULE 2: MULTI-CRITERIA SHORTEST PATH
# =====================================================
def multi_criteria_dijkstra(graph, source, destination, alpha, beta):
    pq = [(0, source, [])]
    visited = set()

    while pq:
        current_cost, node, path = heapq.heappop(pq)

        if node in visited:
            continue

        path = path + [node]
        visited.add(node)

        if node == destination:
            return current_cost, path

        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                edge = graph[node][neighbor]
                weight = alpha * edge["time"] + beta * edge["cost"]
                heapq.heappush(pq, (current_cost + weight, neighbor, path))

    return float("inf"), []


# =====================================================
# STREAMLIT UI
# =====================================================
st.set_page_config(page_title="Public Transport Optimization", layout="wide")

st.title("🚍 Public Transport Route Optimization")
st.subheader("Multi-Criteria Shortest Path – Live Demonstration")

graph = build_transport_graph()

# =====================================================
# TABS
# =====================================================
tab1, tab2 = st.tabs(
    ["🧩 Module 1: Transport Network Graph", "🚍 Module 2: Route Optimization"]
)

# =====================================================
# MODULE 1 TAB
# =====================================================
with tab1:
    st.header("Module 1 Output: Transport Network Graph")

    st.success(
        "This module constructs the weighted transport network graph (nodes and edges). "
        "Route optimization is performed separately in Module-2 using this graph."
    )

    # -------- Nodes --------
    st.subheader("🚏 Stops (Nodes)")
    st.write(list(graph.nodes))

    # -------- Edges --------
    st.subheader("🛣 Routes with Weights (Edges)")
    for u, v, data in graph.edges(data=True):
        st.write(
            f"{u} ↔ {v} | "
            f"Time: {data['time']} | "
            f"Cost: {data['cost']} | "
            f"Distance: {data['distance']}"
        )

    st.info(
        f"Total Stops (Nodes): {graph.number_of_nodes()} | "
        f"Total Routes (Edges): {graph.number_of_edges()}"
    )

    # -------- Graph Visualization --------
    st.subheader("📊 Transport Network Graph Visualization")

    pos = nx.spring_layout(graph, seed=42)

    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(graph, pos, node_size=1200, node_color="lightblue")
    nx.draw_networkx_edges(graph, pos, width=2)
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight="bold")

    edge_labels = {
        (u, v): f"T:{d['time']} C:{d['cost']} D:{d['distance']}"
        for u, v, d in graph.edges(data=True)
    }

    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8)

    plt.axis("off")
    st.pyplot(plt)

    # -------- Graph Validation --------
    st.subheader("✅ Graph Validation")

    if st.button("Validate Graph"):
        valid, message = validate_graph(graph)
        if valid:
            st.success(message)
        else:
            st.error(message)


# =====================================================
# MODULE 2 TAB
# =====================================================
with tab2:
    st.header("Module 2 Output: Optimized Route")

    col1, col2, col3 = st.columns(3)

    with col1:
        source = st.selectbox("Select Source Stop", graph.nodes)

    with col2:
        destination = st.selectbox("Select Destination Stop", graph.nodes)

    with col3:
        preference = st.radio(
            "Optimization Preference",
            ("Fastest Route (Time)", "Cheapest Route (Cost)")
        )

    if st.button("Compute Optimized Route"):
        alpha, beta = (1, 0) if "Time" in preference else (0, 1)
        cost, route = multi_criteria_dijkstra(
            graph, source, destination, alpha, beta
        )

        st.markdown("## ✅ Optimized Route")
        st.success(" → ".join(route))
        st.info(f"Optimized Weight: {cost}")
