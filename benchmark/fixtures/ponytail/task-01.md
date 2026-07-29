```typescript
export function refresh(session: Session) {
  if (!session.refreshToken) return null;
  return isExpired(session.accessToken) ? issueAccessToken(session.refreshToken) : session.accessToken;
}
```

Skipped duplicate branch; one condition covers it.
