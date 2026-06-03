# Skill Flow Visualizer

A reusable Codex Skill for attaching a live node-flow visualizer to another Skill.

This Skill helps an Agent turn a target Skill's end-user workflow into a visual node graph. It is useful when you want to see, debug, or explain what a Skill does at runtime, such as:

- removing an image background with a local model
- inserting generated assets into Figma
- processing documents
- generating design assets
- showing multiple business routes in one canvas

## What It Visualizes

By default, this Skill visualizes the target Skill's user-facing runtime flow.

For example, for a BiRefNet background-removal Skill, the graph should look like:

```text
User provides image
→ Resolve input image
→ Run local BiRefNet
→ Verify transparent PNG
→ Return result or insert into Figma
```

It should not visualize the Agent's authoring process unless explicitly requested.

This means the graph should not default to:

```text
Understand intent
→ Write SKILL.md
→ Create script file
→ Run tests
→ Package Skill
```

That distinction is the core behavior of this Skill.

## Choosing The Target Skill

When multiple Skills are loaded or mentioned, the visualizer follows these rules:

- if the user names a Skill, visualize that Skill
- if the conversation has one clear business goal, visualize the Skill for that goal
- if several business Skills are plausible, ask which Skill to show
- never choose `skill-flow-visualizer` itself as the target unless explicitly requested

If the user asks to show all current business Skills, display those routes together on one canvas with one global active node.

## Included Files

```text
skill-flow-visualizer/
├── SKILL.md
├── README.md
├── assets/
│   └── visualizer-template/
│       └── index.html
├── references/
│   └── flow-schema.md
└── scripts/
    └── init_flow_visualizer.py
```

## How It Works

The visualizer is a local HTML page that reads JSON files from a target Skill:

```text
target-skill/
└── visualizer/
    ├── index.html
    ├── flows.json
    ├── runtime-state.json
    └── flow-<route-id>.json
```

`flows.json` lists all routes that should appear together.

`runtime-state.json` stores one global active node:

```json
{
  "activeNodeCode": "BF01"
}
```

Only one node should be active across all routes. The frontend derives all node statuses from that one active code.

## Initialize A Target Skill

Run the scaffold script from this Skill folder:

```bash
python scripts/init_flow_visualizer.py /absolute/path/to/target-skill \
  --output-dir visualizer \
  --flow-id main \
  --prefix SF
```

The script will:

- copy the visualizer HTML template
- create `flows.json`
- create `runtime-state.json`
- create a starter `flow-main.json`
- infer starter nodes from the target Skill's `## Workflow` section when appropriate

If the target Skill's `## Workflow` describes how to create or package a Skill, do not use it as the default graph. The graph should describe what the target Skill does for the end user.

## Preview Locally

Serve the generated visualizer folder:

```bash
cd /absolute/path/to/target-skill/visualizer
python3 -m http.server 5188
```

Then open:

```text
http://localhost:5188/
```

## Multiple Routes

Add more routes by creating additional `flow-*.json` files and registering them in `flows.json`:

```json
{
  "runtimePath": "runtime-state.json",
  "flows": [
    {
      "id": "birefnet-cutout",
      "flowPath": "flow-birefnet-cutout.json"
    },
    {
      "id": "image-to-figma",
      "flowPath": "flow-image-to-figma.json"
    }
  ]
}
```

Use different prefixes for different routes, such as `BF`, `IF`, `KV`, or `AS`.

## Runtime Updates

To move the active node, update only `runtime-state.json`:

```json
{
  "activeNodeCode": "IF03"
}
```

Do not write `done`, `active`, or `pending` status fields into flow files. Flow files should remain static route definitions.

## Schema

See [`references/flow-schema.md`](references/flow-schema.md) for the full JSON schema.

## Packaging

From the parent directory:

```bash
zip -r skill-flow-visualizer.zip skill-flow-visualizer
```

The zip should contain the `skill-flow-visualizer/` folder with `SKILL.md` at its root.

## Notes For Agents

If this Skill is loaded before the target business Skill exists, infer the target runtime workflow from the user's intended capability.

Example:

If the user says they want to build a Skill that removes image backgrounds with BiRefNet, visualize the image background-removal workflow, even while the Agent is still writing `SKILL.md` or creating scripts.

The active node represents the part of the target Skill's runtime workflow currently being designed, implemented, tested, or discussed.
