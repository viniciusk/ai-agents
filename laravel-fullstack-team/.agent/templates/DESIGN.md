# Design — {{feature-slug}}

> Produced by `architect` in Phase 2. Must be approved by the user before Phase 3 begins. This is the contract the tdd-specialist writes tests against and the developer implements against. If any section is ambiguous, the architect halts and asks; agents downstream MUST NOT improvise.

## Inputs Consumed

- `./BACKLOG.md` (rev: {{rev_number}})
- Project `README.md` at repo root
- Existing domain models referenced: {{list or "none"}}

## Design Summary

One paragraph. What is being built, in plain language, and the core architectural stance (e.g. "New Action class + Inertia page + single DB table; no new middleware").

## Domain Model (DDD)

### Entities
| Name | Attributes | Identity | Notes |
|---|---|---|---|
| `{{EntityName}}` | `{{typed list}}` | `{{id field}}` | {{notes}} |

### Value Objects
| Name | Shape | Invariants |
|---|---|---|
| `{{ValueObjectName}}` | `{{typed fields}}` | {{rule(s)}} |

### Domain Services / Actions
| Class | Responsibility | Inputs | Outputs | Side Effects |
|---|---|---|---|---|
| `App\Actions\{{ActionName}}` | {{single responsibility, one sentence}} | `{{typed params}}` | `{{return type}}` | {{db writes / events / none}} |

> SOLID note: controllers must not contain logic. All business behavior lives in Actions or domain services above.

## Data Layer

### Migrations
- `{{YYYY_MM_DD_HHMMSS}}_create_{{table}}.php` — {{columns, indexes, FKs}}

### Models
- `App\Models\{{ModelName}}` — fillable: `{{list}}`; casts: `{{list}}`; relations: `{{list}}`.

### Seeders / Factories
- `{{ModelName}}Factory` — required for tests.

## HTTP Layer

### Routes
| Method | URI | Name | Controller@Action | Middleware |
|---|---|---|---|---|
| GET | `/{{path}}` | `{{route.name}}` | `{{Controller}}@{{method}}` | `auth`, `{{extra}}` |

### Inertia Responses
Each controller action must declare the exact prop shape it renders.

```ts
// Page: {{PascalPageName}}.vue — rendered by {{Controller}}@{{method}}
interface Props {
  {{propA}}: {{Type}};
  {{propB}}: {{Type}};
}
```

## Frontend Layer (Vue 3 + TS + Tailwind v4)

### Pages / Components Created
| File | Purpose | Props interface |
|---|---|---|
| `resources/js/Pages/{{PageName}}.vue` | {{purpose}} | see above |
| `resources/js/Components/{{ComponentName}}.vue` | {{purpose}} | `{{interface}}` |

### Forms
If a form is involved, specify the `useForm` shape:

```ts
const form = useForm({
  {{field}}: {{initialValue}},
});
```

### Styling Strategy
- Tailwind v4 utility classes only; no ad-hoc CSS.
- New CSS variables introduced: {{list or "none"}}.

## Testing Contract (what Phase 3 must cover)

The tdd-specialist will generate the following tests. If any are missing or misnamed, Phase 5 fails.

- **Feature tests** (`tests/Feature/`):
  - `{{TestClass}}::{{test_method}}` — {{assertion summary}}
- **Unit tests** (`tests/Unit/Actions/`):
  - `{{ActionTestClass}}::{{test_method}}` — {{assertion summary}}

## File Paths Contract

Exhaustive list of files the developer will create. The developer must not add files outside this list without updating this section first (that is an architectural drift event).

- `app/Actions/{{ActionName}}.php`
- `app/Http/Controllers/{{Controller}}.php`
- `app/Models/{{Model}}.php`
- `database/migrations/{{timestamp}}_create_{{table}}.php`
- `resources/js/Pages/{{PageName}}.vue`
- `tests/Feature/{{Test}}.php`
- `tests/Unit/Actions/{{Test}}.php`

## Explicit Non-Decisions

Architectural choices the architect considered and rejected, with reasoning. Prevents re-litigating during Phase 4.

- **Repository Pattern:** rejected — single data source, Eloquent is sufficient.
- **{{Pattern}}:** rejected — {{reason}}.

## Open Questions

If any remain after user approval, they must be resolved before Phase 3 starts.

- {{question — or "none"}}
