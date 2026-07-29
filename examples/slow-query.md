# Slow Postgres query

**Task:** "My Postgres query got slow after the table grew to a few million rows.
How do I figure out why?"

Real Claude Haiku 4.5 output — no-skill arm vs NoYap arm (`skills/noyap/SKILL.md`
as system prompt). Blank lines inside code trimmed for display; token counts are
of the full response. Reproduce by running the prompt with and without the skill.

## Without NoYap, 300 tokens

> Start with `EXPLAIN ANALYZE` on the slow query to see the actual execution plan:
>
> ```sql
> EXPLAIN ANALYZE SELECT ... your query ...;
> ```
>
> Look for these red flags in the output:
> - **Sequential scans** when an index should be used (high row estimates or actual rows)
> - **High planning/execution time** ratio (suggests table stats are stale)
> - **Nested loop joins** when hash/merge joins would be better
>
> Then check:
>
> 1. **Is the table analyzed?** Run `ANALYZE table_name;` if stats are stale
> 2. **Are indexes present and being used?** Run `\d table_name` to list them; if EXPLAIN shows seq scan instead of index scan, the planner may think a scan is cheaper
> 3. **Index bloat?** Run:
>    ```sql
>    SELECT schemaname, tablename, ROUND(100 * (CASE WHEN otta > 0 THEN sml.relpages - otta ELSE 0 END) / sml.relpages, 2) AS table_waste_percent
>    FROM pgstattuple('table_name');
>    ```
>    High bloat might mean `VACUUM FULL` or `REINDEX`
> 4. **Missing index?** If EXPLAIN shows a seq scan and the WHERE clause filters on a column, add:
>    ```sql
>    CREATE INDEX idx_name ON table_name (column);
>    ```
>
> Post the EXPLAIN ANALYZE output if you're stuck — the plan tells the full story of what's slow and why.

## With NoYap, 201 tokens

> Run EXPLAIN ANALYZE on the query to see the plan and spot full table scans or missing indexes:
>
> ```sql
> EXPLAIN ANALYZE SELECT ... your query ...;
> ```
>
> Look for:
> - **Seq Scan** on large tables (bad; should be Index Scan or Index Only Scan).
> - **actual rows >> estimated rows** (planner is wrong; run `ANALYZE table_name;` to rebuild stats).
> - **high actual execution time** on specific nodes.
>
> Quick fixes:
> 1. **Missing index**: `CREATE INDEX idx_name ON table(column);` for WHERE/JOIN/ORDER BY columns.
> 2. **Stale stats**: `ANALYZE table_name;` updates row count estimates.
> 3. **Wrong join order**: Add `/*+ BitmapScan(table) */` hint or rewrite the JOIN.
> 4. **N+1 queries**: If running in a loop, batch or use a JOIN instead.
>
> Paste the EXPLAIN ANALYZE output and the query if you need help reading it.

**300 → 201 tokens.** Same first move (`EXPLAIN ANALYZE`), same real fixes.
NoYap drops the speculative `pgstattuple` bloat query — a heavy tangent before
the plan has even been read — and keeps the diagnosis path tight.
