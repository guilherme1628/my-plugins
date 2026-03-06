---
name: convex-best-practices
description: Convex development best practices for writing queries, mutations, and actions. Apply when working in convex/**/*.ts or convex/**/*.js files. Covers query optimization, argument validation, authentication, async handling, schema design, error handling, function organization, pagination, schedulers, Date.now() in queries, "use node" directive, and custom functions for data protection.
---

# Convex Development Best Practices

Apply these rules when writing or reviewing code in `convex/` directories.

---

## 1. Query Optimization — Use Indexes, Not `.filter()`

`.filter()` performs full table scans. Use `.withIndex()` instead.

**Bad:**
```typescript
const user = await ctx.db
  .query("users")
  .filter(q => q.eq(q.field("email"), email))
  .first();
```

**Good:**
```typescript
// schema.ts
users: defineTable({
  email: v.string(),
}).index("by_email", ["email"]),

// function
const user = await ctx.db
  .query("users")
  .withIndex("by_email", q => q.eq("email", email))
  .first();
```

For small result sets where an index isn't warranted, collect first then filter in TypeScript:
```typescript
const allUsers = await ctx.db.query("users").collect();
const filtered = allUsers.filter(user => user.age > 18);
```

---

## 2. Argument Validation — Always Validate Args and Returns

All public `query`, `mutation`, and `action` functions MUST define validators for both `args` and `returns`:

```typescript
export const createTask = mutation({
  args: {
    text: v.string(),
    userId: v.id("users"),
    priority: v.optional(v.union(v.literal("low"), v.literal("medium"), v.literal("high"))),
  },
  returns: v.id("tasks"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("tasks", { ...args, completed: false });
  },
});
```

Internal functions can skip validators if only called by trusted backend code. Enforce with `@convex-dev/require-argument-validators` ESLint rule.

---

## 3. Authentication — Check Auth in All Protected Functions

Every public function accessing user data MUST verify authentication AND ownership.

**Queries — verify auth, scope to user:**
```typescript
export const getMyTasks = query({
  args: {},
  returns: v.array(v.object({ /* ... */ })),
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx); // throws if not authenticated
    return await ctx.db
      .query("tasks")
      .withIndex("by_user", q => q.eq("userId", user._id))
      .collect();
  },
});
```

**Mutations — verify auth AND ownership before modifying:**
```typescript
export const deleteTask = mutation({
  args: { taskId: v.id("tasks") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new Error("Task not found");
    if (task.userId !== user._id) throw new Error("Unauthorized");
    await ctx.db.delete(args.taskId);
    return null;
  },
});
```

**Auth alone is not enough.** Checking `getUserIdentity()` without verifying the user owns the resource means any authenticated user can modify any record. Always:
- Verify ownership: `task.userId !== user._id`
- Use unguessable IDs (Convex IDs or UUIDs), never spoofable data like emails
- Never trust client-provided IDs without verification

---

## 4. Async Handling — Always Await Promises

Always `await` all promises. Missing awaits on `ctx.db.patch`, `ctx.db.insert`, `ctx.scheduler.runAfter`, etc. cause silent failures.

**Bad:**
```typescript
ctx.db.patch(args.userId, { name: args.name }); // Missing await!
```

**Good:**
```typescript
await ctx.db.patch(args.userId, { name: args.name });
```

Enable the `no-floating-promises` ESLint rule.

---

## 5. Schema Design — Flat, Relational, Indexed

Design schemas as **document-relational**: flat documents with relationships via IDs.

Key principles:
- **Keep documents flat** — avoid deeply nested arrays of objects
- **Use relationships** — link via IDs across tables
- **Add indexes early** — index foreign keys (userId, teamId) from the start
- **Limit array sizes** — arrays are capped at 8,192 items

**Bad (deep nesting):**
```typescript
posts: defineTable({
  comments: v.array(v.object({
    replies: v.array(v.object({ ... }))
  }))
})
```

**Good (relational):**
```typescript
posts: defineTable({ authorId: v.id("users"), title: v.string() })
  .index("by_author", ["authorId"]),
comments: defineTable({ postId: v.id("posts"), authorId: v.id("users"), text: v.string() })
  .index("by_post", ["postId"]),
```

---

## 6. Error Handling

- **Throw** for exceptional cases (auth failure, not found, unauthorized)
- **Return null** for expected absences (optional lookups)
- Use clear, specific error messages: `"Email already registered"` not `"Error"`
- Don't expose internal details to clients
- Log errors with context for debugging

---

## 7. Function Organization — Keep Wrappers Thin

Put business logic in plain TypeScript functions. Keep `query`/`mutation`/`action` wrappers thin:

```typescript
// convex/lib/auth.ts
export async function getCurrentUser(ctx: QueryCtx | MutationCtx) {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) throw new Error("Not authenticated");
  return await ctx.db
    .query("users")
    .withIndex("by_token", q => q.eq("tokenIdentifier", identity.tokenIdentifier))
    .unique();
}

// convex/posts.ts
export const createPost = mutation({
  args: { title: v.string(), content: v.string() },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    return await createPostInternal(ctx, user._id, args);
  },
});
```

---

## 8. Pagination — Never `.collect()` Unbounded Queries

Use cursor-based pagination for large datasets:

```typescript
export const listTasks = query({
  args: { paginationOpts: paginationOptsValidator },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_creation")
      .paginate(args.paginationOpts);
  },
});
```

Client side:
```typescript
const { results, status, loadMore } = usePaginatedQuery(
  api.tasks.listTasks, {}, { initialNumItems: 25 }
);
```

---

## 9. Scheduler Safety — Only Schedule Internal Functions

Never schedule public `api` functions. Always use `internal`:

**Bad:**
```typescript
await ctx.scheduler.runAfter(0, api.emails.send, { to: "user@example.com" });
```

**Good:**
```typescript
await ctx.scheduler.runAfter(0, internal.emails.send, { to: "user@example.com" });
```

Scheduled functions bypass client auth and validation.

---

## 10. No `Date.now()` in Queries

`Date.now()` in queries breaks caching and reactivity. Solutions:

1. **Pass time as argument:** `args: { now: v.number() }`
2. **Use status fields** updated by cron/scheduled functions
3. **Use coarser granularity** (pass today's date string)

---

## 11. "use node" Directive

Files with `"use node"` can ONLY contain `action` and `internalAction`. Never put `query` or `mutation` in a `"use node"` file.

```typescript
"use node";
import { action } from "./_generated/server";

export const callExternalAPI = action({
  args: { url: v.string() },
  handler: async (ctx, args) => {
    const response = await fetch(args.url);
    return await response.json();
  },
});
```

---

## 12. Custom Functions for Data Protection (Convex's RLS)

Instead of Row Level Security, use custom function wrappers from `convex-helpers`:

```typescript
import { customQuery, customMutation } from "convex-helpers/server/customFunctions";
import { query, mutation } from "../_generated/server";

export const authedQuery = customQuery(query, {
  args: {},
  input: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    return { ctx: { ...ctx, user }, args };
  },
});

// Usage — ctx.user automatically available
export const getTasks = authedQuery({
  handler: async (ctx) => {
    return await ctx.db.query("tasks")
      .withIndex("by_user", q => q.eq("userId", ctx.user._id))
      .collect();
  },
});
```

Compose wrappers for RBAC, multi-tenant, and resource ownership patterns.

---

## 13. TypeScript Strict Mode — No `any`

Enable `"strict": true` in tsconfig.json. Convex provides end-to-end type safety from schema to client — don't undermine it with `any`.

Use proper types: `Doc<"users">`, `Id<"tasks">`, `QueryCtx`, `MutationCtx`, `ActionCtx`.
