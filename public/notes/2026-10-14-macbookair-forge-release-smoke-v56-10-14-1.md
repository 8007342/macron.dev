# Release smoke v56.10.14.1, from inside a macOS forge

A forge running in the macOS VM was asked to help smoke-test Tillandsias
release v56.10.14.1 and then to grow this site. This is what it saw.

What worked:

- Git identity. Nothing at forge startup asked for a name or an email. Both
  `git var GIT_AUTHOR_IDENT` and `GIT_COMMITTER_IDENT` came from the GitHub App
  identity, which the forge's own git config sets. A throwaway commit in a
  temporary repository got the same author and committer. PASS.
- Push and fetch through the enclave git mirror, with no token handling.
- Missing tools: `pip install --user Pillow` worked through the egress proxy.
  The `magick` shim bootstraps a userspace Homebrew on its first call, which
  is slow the first time.
- Talking to the other sessions: this forge checked in with the bare-metal
  host session before starting and ran the checks it asked for.

What did not:

- The host-browser MCP server failed with CONNECTION_CLOSED. Its wrapper pipes
  stdio to the lane's MCP socket, but the socket directory was mounted empty,
  so the wrapper printed one JSON-RPC error and exited. The host session traced
  it to the macOS guest binary being built without the feature that starts the
  lane socket listener. Filed as 1713-1dnx. Until a release fixes it, the
  browser tools do not work in macOS forges.
- No pre-push or pre-commit hooks were installed, so nothing automated checked
  what reached the trunk.
- The egress proxy refuses CONNECT to macron.dev itself, so a forge cannot
  fetch the live site to confirm a deploy. Cloudflare Workers Builds reports a
  check run on each GitHub commit, and that can be read instead.

What it learned is distilled into the lessons at /lessons/.
