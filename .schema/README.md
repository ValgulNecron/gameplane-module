# Editor schemas for module YAML

JSON Schemas that give editors (VS Code's `redhat.vscode-yaml`, and any
`yaml-language-server` client) validation and autocomplete for the two YAML
files in every module — and stop the extension from guessing an unrelated
schema from its schema store (it used to mis-match `template.yaml` against the
AWS SAM schema and flag valid fields).

Each module file opts in with a first-line modeline:

```yaml
# yaml-language-server: $schema=../.schema/gametemplate.schema.json   # template.yaml
# yaml-language-server: $schema=../.schema/module.schema.json         # module.yaml
```

The relative path resolves whether this repo is opened on its own or as the
`modules/` submodule of the Gameplane repo.

| File | Schema | Source |
| --- | --- | --- |
| `template.yaml` | `gametemplate.schema.json` | **Generated** from the GameTemplate CRD in the Gameplane repo. Do not hand-edit. |
| `module.yaml` | `module.schema.json` | Hand-maintained; mirrors `docs/module-authoring.md`. |

## Regenerating `gametemplate.schema.json`

`template.yaml` is a `GameTemplate` custom resource, so its schema is the CRD's
`openAPIV3Schema`. When the CRD changes (new spec fields), regenerate from the
**Gameplane** repo — the submodule doesn't carry the CRD:

```sh
make module-schema      # runs hack/gen-module-schema.py, writes modules/.schema/gametemplate.schema.json
```

Then commit the updated file here (and bump the submodule pointer in the
Gameplane repo).
