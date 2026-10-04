# Blueprints

A blueprint is the lifecycle of one product type: its phases, the skills each
phase runs, and the artifact that proves the phase is finished. See
`architecture/BLUEPRINTS-AND-STORIES.md` for the model.

| Blueprint | For |
| --- | --- |
| `full-stack-app` | web + mobile + backend API from one set of stories |
| `web-app` | web application with a backend API |
| `mobile-app` | Expo mobile app with a backend API |

```sh
e2e blueprint list                      # what is available
e2e blueprint check                     # validate against the skill registry
e2e blueprint status full-stack-app     # where this project stands
e2e orchestrate "build the app" --blueprint full-stack-app
e2e orchestrate "sign in" --blueprint full-stack-app --story STORY-002
```

## Schema

```json
{
  "name": "web-app",
  "description": "…",
  "inputs": ["PRD.md"],
  "phases": [
    {
      "id": "build",
      "objective": "…",
      "depends_on": ["contracts"],
      "skills": ["backend-developer", {"skill": "react-js-developer", "platforms": ["web"]}],
      "produces": ["ARTIFACT.md"],
      "requires_stories_done": true,
      "approval": "owner"
    }
  ]
}
```

- `inputs`: artifacts that must exist before any phase starts.
- `depends_on`: earlier phases that must be complete. Only backward references are valid.
- `skills`: registry names. A `platforms` tag drops the skill when the story being built targets none of them.
- `produces`: files (or directories, with a trailing `/`) whose presence completes the phase. Each must be declared in the `produces:` contract of a skill in the phase.
- `requires_stories_done`: the phase completes when every story is `done`.
- `approval: owner`: the plan flags that a release owner must approve; the engine never approves on its own.

Every phase needs `produces` or `requires_stories_done`.

## Deployment targets

The `preview` and `release` phases use `app-deployment`, which supports Vercel, Firebase, Supabase, Railway, AWS, GCP, Azure, and a VPS. The target is chosen per project and recorded in `DEPLOYMENT.md`; the blueprint does not need editing to change it.

## Changing the stack

Copy a blueprint and swap skills: `react-native-cli-developer` for
`expo-developer`, `frontend-developer` for `react-js-developer`. Project
blueprints in `.e2e/workflows/` or a path in `E2E_BLUEPRINTS_PATH` are found
too. Run `e2e blueprint check` after any edit.
