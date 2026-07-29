Fixed duplicate refresh branch.
Not run.

```typescript
export function refresh(session: Session) {
  if (!session.refreshToken) return null;
  return isExpired(session.accessToken)
    ? issueAccessToken(session.refreshToken)
    : session.accessToken;
}
```
