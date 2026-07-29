# HTTP timeout

**Task:** "How do I add a timeout to an HTTP request in Python?"

Real Claude Haiku 4.5 output — no-skill arm vs NoYap arm (`skills/noyap/SKILL.md`
as system prompt). Blank lines inside code trimmed for display; token counts are
of the full response. Reproduce by running the prompt with and without the skill.

## Without NoYap, 314 tokens

> The simplest approach is using the `requests` library with the `timeout` parameter:
>
> ```python
> import requests
> response = requests.get('https://api.example.com/data', timeout=5)
> response = requests.get('https://api.example.com/data', timeout=(3.05, 10))
> ```
>
> The `timeout` argument:
> - **Single value** (e.g., `timeout=5`): raises `requests.exceptions.Timeout` if the request takes >5 seconds
> - **Tuple** (e.g., `timeout=(3.05, 10)`): first value is connect timeout, second is read timeout
> - `None`: no timeout (default)
>
> **For other libraries:**
>
> **urllib (stdlib):**
> ```python
> import urllib.request
> urllib.request.urlopen('https://api.example.com/data', timeout=5)
> ```
>
> **httpx (modern, supports async):**
> ```python
> import httpx
> httpx.get('https://api.example.com/data', timeout=5.0)
> ```
>
> **aiohttp (async):**
> ```python
> import aiohttp
> timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=10)
> async with aiohttp.ClientSession(timeout=timeout) as session:
>     async with session.get('https://api.example.com/data') as resp:
>         pass
> ```
>
> For most cases, `requests` with `timeout=5` (or whatever duration suits your use case) is the standard approach.

## With NoYap, 170 tokens

> Use the `timeout` parameter with the `requests` library:
>
> ```python
> import requests
> response = requests.get('https://api.example.com/data', timeout=5)
> response = requests.get('https://api.example.com/data', timeout=(3, 10))
> ```
>
> First number is connection timeout, second is read timeout. Omit one for symmetrical:
>
> ```python
> timeout=(3, 3)  # or just timeout=3
> ```
>
> For `urllib.request` (stdlib):
>
> ```python
> import urllib.request
> response = urllib.request.urlopen(url, timeout=5)
> ```
>
> Without `timeout`, requests hang indefinitely on unresponsive servers. Common practice: 5–30 seconds depending on use case.

**314 → 170 tokens.** The question was "how do I add a timeout" — NoYap answers
it (requests + the stdlib fallback + *why* it matters) and stops. The plain
agent adds `httpx` and `aiohttp` tours nobody asked for.
