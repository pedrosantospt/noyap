The profile update function needs validation before it writes user-controlled fields. I would reject empty names and invalid ages before mutating the profile.

```python
def update_profile(profile, data):
    name = data.get("name", "").strip()
    age = data.get("age")
    if not name:
        raise ValueError("name is required")
    if not isinstance(age, int) or age < 0 or age > 130:
        raise ValueError("age is invalid")
    profile["name"] = name
    profile["age"] = age
    return profile
```

This keeps the validation close to the trust boundary and avoids saving bad values.
