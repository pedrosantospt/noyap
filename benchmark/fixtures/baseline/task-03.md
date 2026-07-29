The repeated formatting can be moved into one helper and then reused by the callers. This avoids changing the display format in multiple places later.

```typescript
export function formatPrice(cents: number, currency = "USD") {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(cents / 100);
}

export const subtotalLabel = (cents: number) => formatPrice(cents);
export const totalLabel = (cents: number) => formatPrice(cents);
```

No new dependency is needed because the platform already has currency formatting.
