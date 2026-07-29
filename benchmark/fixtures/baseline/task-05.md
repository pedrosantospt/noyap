I would add one focused regression test that covers repeated separators, while keeping the normal case readable.

```python
def test_slugify_collapses_repeated_separators():
    assert slugify("Hello---world") == "hello-world"
    assert slugify("Hello world") == "hello-world"
```

That gives the helper a clear guard without creating a broad test matrix.
