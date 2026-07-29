The API call should use a finite timeout and convert timeout failures into a readable integration error.

```python
from urllib import error, request


def fetch_json(url, timeout=5):
    try:
        with request.urlopen(url, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except TimeoutError as exc:
        raise RuntimeError("api request timed out") from exc
    except error.URLError as exc:
        raise RuntimeError(f"api request failed: {exc.reason}") from exc
```

This prevents the process from hanging forever on a slow remote service.
