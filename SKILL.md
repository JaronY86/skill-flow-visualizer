---
name: skill-flow-visualizer
description: Create, attach, and maintain a live node-flow visualizer for a target Skill's end-user runtime workflow. Use when the user asks to show what an existing or planned Skill does as nodes, display multiple business routes together, track the current active runtime node, jump to node codes, debug or style a workflow graph, scaffold visualizer files for another Skill, or visualize a Skill such as image background removal, Figma writeback, document processing, or other user-facing capability flows. Do not visualize the Agent's process of authoring, testing, packaging, or delivering the Skill unless the user explicitly asks for an authoring/development workflow.
---

# Skill Flow Visualizer

Use this skill to attach a reusable live node-flow visualizer to a target business Skill.

The visualizer is a local HTML canvas that reads static flow files plus one global runtime-state file. It is meant to show what the target Skill does for its end user, not how the Agent creates that Skill.

## Core Rule

Default to the target Skill's runtime/business workflow.

For example, if the user is making an image background removal Skill, visualize:

1. User provides an image.
2. Resolve the input image.
3. Run local BiRefNet/background removal.
4. Verify transparent output.
5. Return or insert the result.

Do not visualize these authoring steps by default:

- understand intent
- research/interview
- write `SKILL.md`
- design tests
- run evaluations
- package and deliver `.skill`

Only visualize the authoring/development workflow when the user explicitly says they want the process of making the Skill, developing the Skill, packaging the Skill, or debugging the Skill authoring flow.

## Pre-Authoring Mode

Use this mode when this visualizer Skill is loaded before the target business Skill exists.

1. Wait for or infer the target Skill's intended user-facing capability.
   - Examples: remove image background with BiRefNet, insert an image into Figma, generate event skin assets, summarize documents.
   - Treat this intended capability as the target workflow.

2. As the Agent later creates the target Skill, keep the node graph focused on what that target Skill will do when invoked by an end user.
   - If the Agent is writing `SKILL.md` for a BiRefNet background removal Skill, the graph node should be about "Run local BiRefNet", not "Write SKILL.md".
   - If the Agent is creating `scripts/remove_bg.py`, the graph node should be about "Generate transparent PNG", not "Create script file".
   - If the Agent is packaging the Skill, the graph node should remain on the target runtime flow or final result, not become "Package Skill".

3. The active node represents the part of the target Skill's runtime workflow currently being designed, implemented, tested, or discussed.
   - Designing the upload requirement means active node like `Resolve Input Image`.
   - Implementing the model script means active node like `Run Local BiRefNet`.
   - Testing the output means active node like `Verify Transparent PNG`.

4. If no target capability has been stated yet, ask one concise clarification:
   - "这个节点图要展示哪个 Skill 被用户使用时的功能流程？"

## Target Skill

1. Identify the target Skill from the user's request or current workspace.
   - If another Skill was just discussed or modified, use that Skill as the target.
   - If the user says "当前 Skill", use the Skill being built as a product and visualize what that Skill will do for its end user.
   - If multiple candidates exist, prefer the one most recently mentioned.
   - If the target Skill is not yet written, infer the runtime workflow from the user's intended capability description.

2. Separate target runtime flow from Agent authoring flow.
   - Runtime flow means the steps that happen when an end user invokes the target Skill.
   - Agent authoring flow means the steps the Agent follows to create, test, package, or install the Skill.
   - Unless explicitly requested, never use Agent authoring flow as the displayed node graph.

3. Do not change the target Skill's business logic unless the user asks.
   - The visualizer only adds or updates visualization files and lightweight instructions.
   - Keep target workflow files separate from scripts, model code, Figma logic, and output assets.

## Target Selection With Multiple Skills

Use these rules when multiple Skills are loaded, installed, mentioned, or potentially relevant.

1. If the user explicitly names a Skill, visualize that Skill.
   - Example: "给 `birefnet-figma-cutout` 画节点图" means target `birefnet-figma-cutout`.
   - Example: "打开 activity-skin 的节点图" means target the activity skin Skill.

2. If the conversation has one clear business goal, visualize the Skill for that goal.
   - Example: if the user has been discussing image cutout/background removal, target the image cutout Skill even if Figma or browser Skills are also loaded.
   - Supporting Skills, such as Figma, browser, GitHub, or this visualizer itself, are not the target unless the user explicitly says so.

3. If several business Skills are plausible and the user only says "打开节点图", "显示流程", or another ambiguous request, ask one concise clarification before creating or switching the graph:
   - "你想查看哪个 Skill 的运行流程？"
   - Offer likely candidates if they are known.

4. Never select `skill-flow-visualizer` itself as the target by default.
   - This Skill is the dashboard/instrumentation layer.
   - Only visualize this Skill's own workflow if the user explicitly asks to inspect or debug the visualizer Skill itself.

If the user asks to show all current business Skills, display multiple target Skill routes together on the same canvas and keep one global `activeNodeCode`.

## Visualizer Files

Create these files inside the target Skill, usually in `visualizer/` or another user-specified folder:

```text
visualizer/
├── index.html
├── flows.json
├── runtime-state.json
└── flow-<route-id>.json
```

- `index.html`: copy from `assets/visualizer-template/index.html`.
- `flows.json`: lists every route to display together.
- `runtime-state.json`: global runtime state for the entire canvas.
- `flow-<route-id>.json`: one static route definition.

Only one node can be `active` across all routes. Store this in the global runtime file:

```json
{
  "activeNodeCode": "BF01"
}
```

## Scaffolding

Prefer the bundled script when starting or attaching a visualizer:

```bash
python scripts/init_flow_visualizer.py /absolute/path/to/target-skill \
  --output-dir visualizer \
  --flow-id main \
  --prefix SF
```

The script copies the visualizer template, creates `flows.json`, creates `runtime-state.json`, and generates a starter `flow-<route-id>.json` from the target Skill's `## Workflow` section when available.

Before running the script, confirm that the target `SKILL.md` describes the target Skill's runtime workflow. If its `## Workflow` section is about making a Skill, testing a Skill, or packaging a Skill, do not use that section as the default route. Instead, create the route from the user's target capability description or ask one concise clarification.

If a target Skill already has flow files, preserve them unless the user explicitly asks to regenerate them.

## Live Updates

When the Agent starts, completes, jumps to, or pauses at a step:

1. Map the step to its node code.
2. Write only the global runtime state:

```json
{
  "activeNodeCode": "<CODE>"
}
```

3. Do not write derived `status` fields into route files.
4. Let the frontend derive statuses:
   - nodes before `activeNodeCode` in the matching route are `done`
   - the matching node is `active`
   - nodes after it are `pending`
   - all nodes in non-active routes are `pending` unless the route file explicitly defines a static status

## Multiple Routes

Show all listed routes together. Add future routes by:

1. Creating another `flow-<route-id>.json`.
2. Adding it to `flows.json`.
3. Keeping the same global `runtime-state.json`.

Use route-specific prefixes such as `BF`, `IF`, `AS`, or `KV` so node codes stay unique across routes.

## Runtime Display

For local preview, serve the visualizer folder with a local web server:

```bash
python3 -m http.server 5188
```

Start the server from the visualizer folder. If the port is occupied, use another port and tell the user the URL.

## Schema

Read `references/flow-schema.md` when creating or debugging flow JSON.
