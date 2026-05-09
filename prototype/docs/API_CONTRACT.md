# API Contract (sourov/v2)

Base path: /wp-json/sourov/v2

## Design rules

1. Resource nouns and action sub-resources.
2. Explicit version path segment.
3. Mutating requests accept Idempotency-Key.
4. Every error returns a normalized envelope.
5. Pagination via page and per_page.

## Error envelope

```json
{
  "error": {
    "code": "badRequest",
    "message": "Human-readable developer message.",
    "target": "date",
    "details": {
      "reason": "date_must_be_future"
    },
    "request_id": "req_123"
  }
}
```

## Endpoint table

| Method | Path | Purpose |
| --- | --- | --- |
| GET | /health | Public plugin health |
| GET | /info | Plugin and capability info |
| GET | /posts | List posts with filters and pagination |
| POST | /posts | Create post, default draft |
| GET | /posts/{id} | Read single post |
| PATCH | /posts/{id} | Update content fields, direct publish blocked |
| DELETE | /posts/{id} | Soft delete by default |
| POST | /posts/{id}/publish | Explicit publish action |
| POST | /posts/{id}/schedule | Schedule with future-date validation |
| POST | /posts/{id}/unschedule | Return future post to draft |
| POST | /posts/bulk | Bulk create with per-item results |
| GET | /categories | List allowed categories |
| POST | /categories | Create category only if allowed by profile |
| GET | /audit-log | Read latest mutation audit entries |
| GET | /templates/{name} | Return article template data |

## Request conventions

- Headers:
  - Content-Type: application/json
  - Authorization: Basic base64(user:app_password) when used
  - X-Sourov-Key: optional plugin key fallback
  - Idempotency-Key: required on POST, PATCH, DELETE in production profile
- Query:
  - page: integer, min 1
  - per_page: integer, min 1, max 100

## Response conventions

- Success payloads include api_version and request_id.
- List responses include pagination metadata.
- Mutations include audit_id where relevant.

## Status code usage

- 200: read or action success.
- 201: resource created.
- 204: successful delete with empty response.
- 400: malformed input.
- 401: unauthenticated.
- 403: authenticated but not allowed.
- 404: not found.
- 409: idempotency conflict.
- 422: semantic validation failure.
- 429: rate limit exceeded.
- 500: internal server failure.
- 503: temporary overload.
