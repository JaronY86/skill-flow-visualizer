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
- For Chinese-facing visualizers, every visible flow title, node title, node description, node detail, and edge label should include `i18n.zh` in the route JSON. The language toggle translates UI chrome, but route-specific business content comes from the flow data.
- Keep node-face copy concise: short titles, 1-2 line descriptions, one short detail/chip, and compact edge labels. Longer explanations belong in docs or secondary details, because the visualizer truncates visible text to keep it inside the node card.

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

## Node Selection Export

The visualizer supports user-selected node exports for capturing temporary Skill-rule ideas.

Expected interaction:

- Click one node to select it.
- Shift-click, Command-click, or Ctrl-click nodes to add or remove multiple nodes.
- Drag on the canvas background to box-select nodes. Hold Shift while box-selecting to add to the current selection.
- Use the `导出 MD` / `Export MD` button to create a Markdown rule draft from the selected nodes.

The generated Markdown must be self-contained, because the user may paste it into a different Agent conversation that has never seen this visualizer. It must read like a reusable Skill rule-fragment package, not like a tool export log. Start with a main feature title and rule-package purpose, then include enough context to explain what the selection means without requiring the user to re-explain it:

- Do not foreground `skill-flow-visualizer` in the opening section. Put the export tool name only in a final metadata section.
- Explain that this is a partial rule-fragment package extracted from a target Skill workflow, not a complete Skill.
- Include the source Skill name, source route, selected node count/codes, and whether the export is a partial fragment rather than a full Skill.
- Add a direct "Agent handling" section that tells the next Agent how to merge, rewrite, or preserve the fragment.
- Adjacent upstream/downstream nodes should be grouped into one cooperative fragment that explains handoff and functional continuity.
- Non-adjacent nodes should be written as independent capability fragments that can be saved and assembled later.
- Keep node codes in the Markdown so the user and Agent can map each rule fragment back to the graph.
- Include practical "拼接建议" / assembly notes so fragments can later be merged into a complete Skill.
- Include raw selected node data and a compact full-route reference, so another Agent can understand the selected nodes' position in the original workflow.

Static browser pages cannot directly send messages into the Agent chat. For true local handoff, start the visualizer with `scripts/serve_visualizer.py`; the export button will POST selected node Markdown and JSON to `/api/selection-export`, and the bridge will write:

```text
visualizer/exports/selected-nodes-latest.md
visualizer/exports/selected-nodes-latest.json
```

If the page is served by a plain static server, the button must fall back to copying the Markdown to the clipboard and offering a browser download.

## Current Selection Handoff

When the user refers to "这个节点", "当前选中的节点", "刚才选的节点", "这些节点", or asks to modify a node without naming a node code, use the visualizer's current selection state before asking the user to repeat node IDs.

Selection state source:

```text
visualizer/exports/selection-state-latest.json
```

If the visualizer is served by `scripts/serve_visualizer.py`, the page updates this file whenever the mouse selection changes. The same state is also available at `/api/selection-state`.

Required Agent behavior:

1. Read the latest selection state when it is available.
2. If no node is selected or the state file is missing/stale, ask the user to select a node or provide a node code.
3. If exactly one node is selected, confirm before editing:
   - Name the selected node code, title, and route.
   - Restate the user's requested change if they already gave one.
   - Ask for confirmation that this is the node they meant.
4. If multiple nodes are selected, do not assume one edit strategy. Ask whether the user wants:
   - one batch rule applied to all selected nodes, or
   - separate per-node modifications.
5. Before modifying any node definition, validate workflow continuity:
   - Read each selected node's upstream and downstream relationships from the selection state or flow JSON.
   - Explain the expected input/output handoff before and after the change.
   - Ask the user to confirm that the modified node behavior should keep, replace, or remove each affected handoff.
6. Only update flow JSON, Skill rules, or exported MD after this confirmation step.

The confirmation should be concise and concrete, for example:

```text
我看到当前选中的是 `FI02`「生成图片」，位于 Figma 图片组件插入运行流程。
你想把它改成“优先复用本地素材，缺失时再生图”。修改前我会保持 `FI01 -> FI02 -> FI03` 的输入输出衔接：FI01 提供提示词/尺寸，FI02 产出素材，FI03 保存并校验尺寸。确认按这个方向改吗？
```

## Runtime Display

After creating or updating a visualizer, make the graph immediately visible.

Priority order:

1. Start or reuse a local preview server from the visualizer folder.
2. Directly open the visualizer URL for the user.
   - If Browser or in-app browser tooling is available, navigate it to the local URL.
   - Otherwise use the platform's URL opener, such as `open <url>` on macOS, when permitted.
3. If automatic opening is blocked, unavailable, or ambiguous, send the URL in a highly visible standalone banner. In assistant chat, the URL must be a Markdown link and must not be placed inside a fenced code block, so the user can click it directly. Escape the separator equal signs in Markdown so they render as plain separators instead of heading syntax:

\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=
📌 打开节点图：[http://127.0.0.1:5189/](http://127.0.0.1:5189/)
\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=

Do not bury the URL inside a normal paragraph or a long file summary. Never wrap the banner in triple backticks or any code block. Use a raw URL only for terminal or script stdout; convert it to a Markdown link in the assistant message. The user should immediately understand that the link is clickable and is the next action.

For local preview, serve the visualizer folder with a local web server:

```bash
python3 /absolute/path/to/skill-flow-visualizer/scripts/serve_visualizer.py \
  --root /absolute/path/to/target-skill/visualizer \
  --port 5188
```

Use this bridge server when possible so selected-node Markdown can be written to `exports/`. If the bridge script is unavailable, fall back to `python3 -m http.server 5188`; selection export will still copy or download Markdown in the browser. If the port is occupied, use another port. Prefer `127.0.0.1` in the displayed URL.

## Success Guidance Banner

After the user successfully installs `skill-flow-visualizer`, or after the first successful visualizer creation/opening in a conversation, include a compact usage guidance banner. Use it once for that success moment, not after every routine node update.

In assistant chat, render the banner as normal Markdown, not a fenced code block. Escape the separator equal signs so they display as visual dividers. Keep the copy eye-catching, practical, and short:

\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=
✅ `skill-flow-visualizer` 已就绪  
🎯 你可以这样使用它：  
• “把当前 Skill 整理成节点图”  
• “打开 `<Skill 名>` 的节点图”  
• “把当前节点切到 `FI05`”  
• “调整节点图样式/交互”  
📌 默认展示目标 Skill 的业务运行流程；如果要看开发或打包流程，请明确说出来。  
\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=

If a visualizer URL is also available and automatic opening did not happen, include the clickable URL banner from "Runtime Display" before or after this guidance banner. Do not merge them into a long paragraph.

## Schema

Read `references/flow-schema.md` when creating or debugging flow JSON.
