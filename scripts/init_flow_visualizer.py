#!/usr/bin/env python3
"""Scaffold a reusable Skill flow visualizer inside a target Skill."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


def slugify(value: str, fallback: str = "main") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or fallback


def read_skill_name(skill_md: str, target_dir: Path) -> str:
    match = re.search(r"^name:\s*([^\n]+)", skill_md, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return target_dir.name


def read_skill_title(skill_md: str, skill_name: str) -> str:
    match = re.search(r"^#\s+(.+)$", skill_md, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return skill_name


def workflow_section(skill_md: str) -> str:
    match = re.search(r"^##\s+Workflow\s*$([\s\S]*?)(?=^##\s+|\Z)", skill_md, re.MULTILINE)
    if match:
        return match.group(1)
    return skill_md


def infer_type(title: str, index: int, total: int) -> str:
    lower = title.lower()
    if index == 0 or any(word in lower for word in ["input", "upload", "resolve", "ask", "collect"]):
        return "input"
    if index == total - 1 or any(word in lower for word in ["report", "return", "export", "output"]):
        return "output"
    if any(word in lower for word in ["check", "verify", "validate", "confirm"]):
        return "check"
    if any(word in lower for word in ["decide", "review", "choose", "approval", "target"]):
        return "decision"
    if "figma" in lower:
        return "figma"
    return "process"


def infer_steps(skill_md: str) -> list[dict[str, object]]:
    section = workflow_section(skill_md)
    matches = list(re.finditer(r"^\s*(\d+)\.\s+(.+?)\s*$", section, re.MULTILINE))
    if not matches:
        return [
            {
                "title": "Resolve Input",
                "description": "Collect required user input and context.",
                "details": ["Generated starter node"],
            },
            {
                "title": "Execute Workflow",
                "description": "Run the main Skill workflow.",
                "details": ["Replace with real steps"],
            },
            {
                "title": "Report Result",
                "description": "Return outputs and next steps to the user.",
                "details": ["Keep concise"],
            },
        ]

    steps: list[dict[str, object]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        block = section[start:end]
        bullets = [
            re.sub(r"^\s*-\s+", "", line).strip()
            for line in block.splitlines()
            if re.match(r"^\s*-\s+", line)
        ]
        title = match.group(2).strip().rstrip(".")
        steps.append(
            {
                "title": title,
                "description": bullets[0] if bullets else title,
                "details": bullets[1:3] if len(bullets) > 1 else bullets[:1],
            }
        )
    return steps


def build_flow(skill_md: str, target_dir: Path, flow_id: str, prefix: str, title: str | None) -> dict[str, object]:
    skill_name = read_skill_name(skill_md, target_dir)
    flow_title = title or f"{read_skill_title(skill_md, skill_name)} Flow"
    steps = infer_steps(skill_md)
    total = len(steps)
    nodes = []
    for index, step in enumerate(steps):
        node_title = str(step["title"])
        nodes.append(
            {
                "id": slugify(node_title, f"step-{index + 1}"),
                "title": node_title,
                "type": infer_type(node_title, index, total),
                "description": step["description"],
                "details": step["details"],
            }
        )
    edges = [
        {
            "from": nodes[index]["id"],
            "to": nodes[index + 1]["id"],
            "label": "next",
        }
        for index in range(max(0, len(nodes) - 1))
    ]
    return {
        "skillName": skill_name,
        "title": flow_title,
        "flowCodePrefix": prefix.upper(),
        "version": 1,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "nodes": nodes,
        "edges": edges,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a Skill flow visualizer.")
    parser.add_argument("target_skill_dir", help="Target Skill directory containing SKILL.md")
    parser.add_argument("--output-dir", default="visualizer", help="Visualizer folder relative to the target Skill")
    parser.add_argument("--flow-id", default="main", help="Route ID for the generated flow")
    parser.add_argument("--prefix", default="SF", help="Node code prefix, such as BF or IF")
    parser.add_argument("--title", default=None, help="Flow title shown above the route")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated files")
    args = parser.parse_args()

    target_dir = Path(args.target_skill_dir).expanduser().resolve()
    skill_md_path = target_dir / "SKILL.md"
    if not skill_md_path.exists():
        raise SystemExit(f"Missing SKILL.md: {skill_md_path}")

    script_dir = Path(__file__).resolve().parent
    template_path = script_dir.parent / "assets" / "visualizer-template" / "index.html"
    if not template_path.exists():
        raise SystemExit(f"Missing visualizer template: {template_path}")

    output_dir = target_dir / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    index_path = output_dir / "index.html"
    if args.force or not index_path.exists():
        shutil.copy2(template_path, index_path)

    flow_id = slugify(args.flow_id)
    flow_path = output_dir / f"flow-{flow_id}.json"
    runtime_path = output_dir / "runtime-state.json"
    manifest_path = output_dir / "flows.json"

    skill_md = skill_md_path.read_text(encoding="utf-8")
    flow = build_flow(skill_md, target_dir, flow_id, args.prefix, args.title)

    if args.force or not flow_path.exists():
        flow_path.write_text(json.dumps(flow, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    active_code = f"{args.prefix.upper()}01"
    if args.force or not runtime_path.exists():
        runtime_path.write_text(json.dumps({"activeNodeCode": active_code}, indent=2) + "\n", encoding="utf-8")

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"runtimePath": "runtime-state.json", "flows": []}

    manifest["runtimePath"] = manifest.get("runtimePath") or "runtime-state.json"
    entry = {"id": flow_id, "flowPath": flow_path.name}
    flows = [item for item in manifest.get("flows", []) if item.get("id") != flow_id]
    flows.append(entry)
    manifest["flows"] = flows
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Visualizer ready: {output_dir}")
    print("Start preview from that folder, for example: python3 -m http.server 5188")
    print("==============================")
    print("🌐 打开节点图： http://127.0.0.1:5188/")
    print("==============================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
