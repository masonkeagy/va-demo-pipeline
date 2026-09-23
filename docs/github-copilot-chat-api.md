# GitHub Copilot change chat API

The GitHub Pages console is a static client. It must not contain a GitHub token,
private key, or Copilot credential. Configure the optional
`window.VA_CHAT_API_URL` value at deploy time to point to a separately hosted
service backed by a GitHub App.

The service owns authentication, authorization, repository access, and the
Copilot integration. It must create a branch and pull request for every
accepted change; it must not write directly to the default branch.

At deploy time, define the public API origin before the page script loads:

```html
<script>
  window.VA_CHAT_API_URL = "https://api.example.com";
</script>
```

Do not put secrets in this value. It is only a public service URL.

## `POST /api/chat`

Request:

```json
{
  "repository": "masonkeagy/va-demo-pipeline",
  "request": "Add a validation step for the PCF control",
  "conversationId": "optional-session-id"
}
```

The service should authenticate the caller (for example, with GitHub OAuth or
an organization identity), verify that the caller is allowed to request changes
in the repository, and validate the repository against an allowlist. The
request body is untrusted input and must be size-limited and logged without
secrets.

Successful response:

```json
{
  "conversationId": "session-id",
  "message": "I created a pull request with the requested validation step.",
  "pullRequest": {
    "number": 42,
    "title": "Add PCF control validation",
    "url": "https://github.com/masonkeagy/va-demo-pipeline/pull/42"
  }
}
```

Errors should return JSON with a user-safe `message` and an appropriate HTTP
status, for example `401` for an unauthenticated caller, `403` for an
unauthorized repository request, `413` for an oversized request, and `502` when
the Copilot or GitHub service is unavailable.

## Security and delivery requirements

- Keep the GitHub App private key and installation credentials only in the
  backend secret store.
- Use least-privilege installation permissions: repository contents (read/write),
  pull requests (read/write), metadata (read), and checks/actions read access
  only when needed for status reporting.
- Create a uniquely named branch from the current default branch, commit the
  reviewed changes, and open a PR with the generated summary and test results.
- Run the repository's required CI checks before a maintainer merges the PR.
- Apply rate limits, request size limits, audit logging, and abuse protection.
- Configure CORS to allow only the deployed GitHub Pages origin.
