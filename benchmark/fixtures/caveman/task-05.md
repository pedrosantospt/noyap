Regression test added.

```python
def test_slugify_collapses_repeated_separators():
    assert slugify("Hello---world") == "hello-world"
```
