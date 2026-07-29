Added trust-boundary validation.
Not run.

```python
def update_profile(profile, data):
    name = data.get("name", "").strip()
    age = data.get("age")
    if not name:
        raise ValueError("name is required")
    if not isinstance(age, int) or not 0 <= age <= 130:
        raise ValueError("age is invalid")
    profile.update(name=name, age=age)
    return profile
```
