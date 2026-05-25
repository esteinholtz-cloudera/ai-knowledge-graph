#!/usr/bin/env python3
"""
Utility script to convert a Turtle (RDF) knowledge graph file to an HTML visualization.
This allows testing the visualization features without running the full pipeline.
"""

import os
import sys

# Add the src directory to Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rdflib import Graph, Literal
from rdflib.namespace import RDF, RDFS, OWL

from knowledge_graph.visualization import visualize_knowledge_graph


def ttl_to_html(ttl_file, output_file):
    """
    Convert a Turtle RDF knowledge graph to an HTML visualization.

    Skips RDF/OWL structural triples (rdf:type owl:Class, rdfs:label, etc.)
    so the graph shows only the domain content from the document.

    Args:
        ttl_file: Path to Turtle (.ttl) file
        output_file: Path to save the HTML visualization
    """
    # Predicates that are ontology/infrastructure — not domain relationships
    _SKIP_PREDICATES = {
        str(RDF.type),
        str(RDFS.label),
        str(RDFS.comment),
        str(OWL.imports),
    }

    try:
        g = Graph()
        g.parse(ttl_file, format="turtle")

        triples = []
        for subject, predicate, obj in g:
            pred_str = str(predicate)

            # Skip ontology structure triples
            if pred_str in _SKIP_PREDICATES:
                continue

            # Use the local name of the URI as a human-readable label
            subj_label = _local_name(str(subject))
            pred_label = _local_name(pred_str)

            # Objects can be URIs (entities) or Literals (plain values)
            if isinstance(obj, Literal):
                obj_label = str(obj)
            else:
                obj_label = _local_name(str(obj))

            triples.append({"subject": subj_label, "predicate": pred_label, "object": obj_label})
            print(f"  {subj_label} --[{pred_label}]--> {obj_label}")

        print(f"\nLoaded {len(triples)} triples from {ttl_file}")

        stats = visualize_knowledge_graph(triples, output_file)

        print(f"Generated HTML visualization: {output_file}")
        print("Graph Statistics:")
        print(f"  Nodes:      {stats.get('nodes', 'N/A')}")
        print(f"  Edges:      {stats.get('edges', 'N/A')}")
        print(f"  Inferred:   {stats.get('inferred_edges', 'N/A')}")
        print(f"  Communities:{stats.get('communities', 'N/A')}")
        print(f"\nOpen in browser: file://{os.path.abspath(output_file)}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def _local_name(uri: str) -> str:
    """Extract the human-readable local name from a URI."""
    # Take the fragment (#) part first, then the last path segment
    if "#" in uri:
        name = uri.split("#")[-1]
    elif "/" in uri:
        name = uri.split("/")[-1]
    else:
        name = uri
    # Replace underscores with spaces for readability
    return name.replace("_", " ")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ttl_to_html.py <input.ttl> <output.html>")
        print("Example: python ttl_to_html.py data/graph.ttl graph.html")
        sys.exit(1)

    ttl_to_html(sys.argv[1], sys.argv[2])
