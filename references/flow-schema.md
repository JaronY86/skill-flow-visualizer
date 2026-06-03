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
  "nodes": [
    {
      "id": "input",
      "title": "Resolve Input",
      "type": "input",
      "description": "Collect the required user input.",
      "details": ["Supported input formats"]
    }
  ],
  "edges": [
    {
      "from": "input",
      "to": "next-step",
      "label": "input ready"
    }
  ]
}
```

Supported node `type` values:

- `input`
- `process`
- `check`
- `decision`
- `figma`
- `output`

Node codes are generated from `flowCodePrefix + two digits`, for example `SF01`, unless a node has an explicit `code` field.
