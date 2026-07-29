```python
def test_slugify_collapses_repeated_separators():
    assert slugify("a---b") == "a-b"
```

One regression is enough.
