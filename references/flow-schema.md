# Flow Visualizer Schema

## flows.json

```json
{
  "runtimePath": "runtime-state.json",
  "flows": [
    {
      "id": "main",
      "flowPath": "flow-main.json"
    }
  ]
}
```

- `runtimePath`: path to the single global runtime-state file.
- `flows`: routes shown together on the same canvas.
- `id`: stable route ID used for layout scoping.
- `flowPath`: route JSON path relative to the visualizer folder.

## runtime-state.json

```json
{
  "activeNodeCode": "SF01"
}
```

Only one `activeNodeCode` should exist for the whole canvas.

## flow-<route-id>.json

```json
{
  "skillName": "example-skill",
  "title": "Example Flow",
  "flowCodePrefix": "SF",
  "version": 1,
  "updatedAt": "2026-06-03T00:00:00+08:00",
  "i18n": {
    "zh": {
      "title": "示例流程",
      "caption": "SF 路线"
    }
  },
  "nodes": [
    {
      "id": "input",
      "title": "Resolve Input",
      "type": "input",
      "description": "Collect the required user input.",
      "details": ["Supported input formats"],
      "i18n": {
        "zh": {
          "title": "解析输入",
          "description": "收集用户输入和必要上下文。",
          "details": ["支持的输入格式"]
        }
      }
    }
  ],
  "edges": [
    {
      "from": "input",
      "to": "next-step",
      "label": "input ready",
      "i18n": {
        "zh": {
          "label": "输入已就绪"
        }
      }
    }
  ]
}
```

## i18n

The visualizer reads localized content from the static route JSON. UI chrome such as status labels is translated by the template, but business content must be provided by the flow data.

Supported localized fields:

- Flow-level `i18n.<lang>.title`
- Flow-level `i18n.<lang>.caption` or `i18n.<lang>.routeLabel`
- Node-level `i18n.<lang>.title`
- Node-level `i18n.<lang>.description`
- Node-level `i18n.<lang>.details`
- Edge-level `i18n.<lang>.label`

When creating a flow for a Chinese-facing user, include at least `i18n.zh` for every visible flow title, node title, node description, node detail, and edge label. Do not rely on the language toggle to machine-translate node content.

## Visible Text Budget

Node cards are intentionally compact. Keep the visible node-face text short:

- Normal node size is fixed at `280 x 126`. Do not enlarge nodes to solve copy length.
- Node titles: up to 6 Chinese characters or about 16 English characters.
- Node descriptions: up to 28 Chinese characters or about 58 English characters. Use line breaks naturally, but write copy short enough to fully display.
- First detail/chip line: up to 12 Chinese characters or about 28 English characters.
- Edge labels: up to 6 Chinese characters or about 16 English characters.

The frontend enforces these budgets with width-aware wrapping, truncation, and a node-level clip path, so overflow should never escape the card. However, the intended behavior is complete display inside the fixed card: write visible node copy within the capacity budget and put longer explanations in the target Skill docs or in secondary details, not on the node face.

Supported node `type` values:

- `input`
- `process`
- `check`
- `decision`
- `figma`
- `output`

Node codes are generated from `flowCodePrefix + two digits`, for example `SF01`, unless a node has an explicit `code` field.
