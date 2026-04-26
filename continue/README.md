# AION Analytics Continue Configs

Continue Hub and local config assets for using `AION Analytics — News-to-Signal` inside Continue.

Files:

- `aion-news-to-signal-india.yaml`:
  Uses the installed console entrypoint:
  `aion-news-to-signal-mcp`

- `aion-news-to-signal-uvx.yaml`:
  Uses `uvx` to run the MCP server from PyPI without a manual package install.

Recommended install path for the standard config:

```bash
pip install aion-news-to-signal
```

Then add the YAML to:

```text
~/.continue/mcpServers/
```

Or publish the same YAML as a public Continue Hub config.
