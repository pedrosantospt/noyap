Added regression test.
Not run.

```python
def test_slugify_collapses_repeated_separators():
    assert slugify("Hello---world") == "hello-world"
```
