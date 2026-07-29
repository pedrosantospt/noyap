# Security

NoYap is prompt/instruction content plus a local benchmark runner.

## Reporting

Open a private security advisory if available. Otherwise, open an issue with:

- affected file
- reproduction steps
- impact
- suggested fix, if known

## Benchmark Safety

- Do not add benchmark code that executes untrusted fixture output.
- Do not exfiltrate environment variables.
- Do not read API keys unless a live provider runner explicitly needs them.
- Do not silently fall back from live mode to fixture mode.
