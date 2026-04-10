#!/usr/bin/env python3
"""Build a marketing knowledge graph from a brand report and intent questions.

Usage:
  python marketing_graph_builder.py \
    --brand-name "婺女洲度假区" \
    --report-file report.txt \
    --questions-file questions.txt \
    --out-dir output
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


@dataclass
class Node:
    id: str
    type: str
    name: str
    attrs: Dict[str, str]


@dataclass
class Edge:
    source: str
    target: str
    type: str
    attrs: Dict[str, str]


KEYWORD_CATALOG = {
    "PainPoint": [
        "不爬山",
        "带娃",
        "带老人",
        "怕累",
        "商业化",
        "性价比",
        "避坑",
        "排队",
        "人挤人",
    ],
    "Scenario": [
        "微度假",
        "两日游",
        "夜游",
        "周末",
        "国庆",
        "中秋",
        "自驾",
        "高铁",
    ],
    "SellPoint": [
        "打铁花",
        "实景演艺",
        "《遇见·婺源》",
        "摇橹船",
        "水上乐园",
        "一站式",
        "徽文化",
        "夜景",
        "汉服",
    ],
    "Competitor": ["庐山", "三清山", "篁岭", "乌镇", "拈花湾", "景德镇", "陶溪川"],
}


def normalize_lines(lines: Iterable[str]) -> List[str]:
    return [re.sub(r"\s+", " ", x).strip() for x in lines if x.strip()]


def read_questions(path: Path) -> List[str]:
    lines = normalize_lines(path.read_text(encoding="utf-8").splitlines())
    questions = [x for x in lines if "？" in x or "?" in x]
    return questions


def infer_nodes_from_text(text: str) -> Dict[str, Set[str]]:
    found: Dict[str, Set[str]] = {k: set() for k in KEYWORD_CATALOG}
    for category, keywords in KEYWORD_CATALOG.items():
        for kw in keywords:
            if kw in text:
                found[category].add(kw)
    return found


def infer_question_tags(question: str, category_map: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    tags: Dict[str, List[str]] = {}
    for category, values in category_map.items():
        matched = [v for v in values if v in question]
        if matched:
            tags[category] = matched
    return tags


def build_graph(brand_name: str, report_text: str, questions: List[str]) -> Tuple[List[Node], List[Edge]]:
    nodes: List[Node] = []
    edges: List[Edge] = []

    def mk_id(prefix: str, n: int) -> str:
        return f"{prefix}_{n:04d}"

    id_counter = 1
    index: Dict[Tuple[str, str], str] = {}

    def get_or_create(node_type: str, name: str, attrs: Dict[str, str] | None = None) -> str:
        nonlocal id_counter
        key = (node_type, name)
        if key in index:
            return index[key]
        node_id = mk_id("N", id_counter)
        id_counter += 1
        node = Node(id=node_id, type=node_type, name=name, attrs=attrs or {})
        nodes.append(node)
        index[key] = node_id
        return node_id

    brand_id = get_or_create("Brand", brand_name)

    extracted = infer_nodes_from_text(report_text)

    # create nodes from report keywords
    for cat, vals in extracted.items():
        for value in sorted(vals):
            node_id = get_or_create(cat, value)
            relation = {
                "SellPoint": "HAS_SELL_POINT",
                "PainPoint": "RELATES_TO_PAIN",
                "Scenario": "FIT_FOR_SCENARIO",
                "Competitor": "COMPARES_WITH",
            }[cat]
            edges.append(Edge(source=brand_id, target=node_id, type=relation, attrs={"source": "report"}))

    # intent question nodes and links
    for i, q in enumerate(questions, start=1):
        q_id = get_or_create("IntentQuestion", q, {"order": str(i)})
        edges.append(Edge(source=q_id, target=brand_id, type="ASKS_ABOUT", attrs={"source": "question_set"}))
        q_tags = infer_question_tags(q, extracted)
        for cat, vals in q_tags.items():
            for value in vals:
                target_id = index[(cat, value)]
                edges.append(
                    Edge(
                        source=q_id,
                        target=target_id,
                        type="MENTIONS",
                        attrs={"category": cat},
                    )
                )

    return nodes, edges


def export_graph(nodes: List[Node], edges: List[Edge], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    graph = {
        "nodes": [asdict(n) for n in nodes],
        "edges": [asdict(e) for e in edges],
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
    }
    (out_dir / "marketing_graph.json").write_text(
        json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    with (out_dir / "nodes.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "type", "name", "attrs"])
        writer.writeheader()
        for n in nodes:
            writer.writerow(
                {
                    "id": n.id,
                    "type": n.type,
                    "name": n.name,
                    "attrs": json.dumps(n.attrs, ensure_ascii=False),
                }
            )

    with (out_dir / "edges.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "type", "attrs"])
        writer.writeheader()
        for e in edges:
            writer.writerow(
                {
                    "source": e.source,
                    "target": e.target,
                    "type": e.type,
                    "attrs": json.dumps(e.attrs, ensure_ascii=False),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build marketing graph from report + intent questions")
    parser.add_argument("--brand-name", required=True)
    parser.add_argument("--report-file", type=Path, required=True)
    parser.add_argument("--questions-file", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("output"))
    args = parser.parse_args()

    report_text = args.report_file.read_text(encoding="utf-8")
    questions = read_questions(args.questions_file)
    nodes, edges = build_graph(args.brand_name, report_text, questions)
    export_graph(nodes, edges, args.out_dir)

    print(f"Done. nodes={len(nodes)} edges={len(edges)} out={args.out_dir}")


if __name__ == "__main__":
    main()
