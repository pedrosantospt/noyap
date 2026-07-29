I found the duplicate refresh-token branch and would fix it by merging the repeated condition into a single path. This keeps the behavior identical while preventing the second branch from becoming unreachable.

```typescript
export function refresh(session: Session) {
  if (!session.refreshToken) {
    return null;
  }

  if (isExpired(session.accessToken)) {
    return issueAccessToken(session.refreshToken);
  }

  return session.accessToken;
}
```

You should also keep the existing expiry tests around this helper because token behavior is easy to regress.
