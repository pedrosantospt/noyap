```python
def update_profile(profile, data):
    name, age = data.get("name", "").strip(), data.get("age")
    if not name or not isinstance(age, int) or not 0 <= age <= 130:
        raise ValueError("invalid profile")
    profile.update(name=name, age=age)
    return profile
```

Kept boundary validation; no schema layer needed.
