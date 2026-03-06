---
name: convex-project-setup
description: Convex project setup and tooling configuration. Use when setting up ESLint, TypeScript config, development commands, agent mode, or Convex components for a Convex project.
---

# Convex Project Setup & Tooling

## ESLint — Required for Every Convex Project

Install and configure ESLint with the official Convex plugin:

```bash
npm install -D eslint @convex-dev/eslint-plugin
```

```javascript
// eslint.config.mjs
import convexPlugin from "@convex-dev/eslint-plugin";

export default [
  ...convexPlugin.configs.recommended,
];
```

This catches: missing `await`, missing argument validators, `.filter()` instead of indexes, missing table names, `.collect()` without pagination.

## Development Commands

- **Development:** `npx convex dev` — watches files, auto-reloads, uses dev deployment
- **Production:** `npx convex deploy` — only for production deployments
- **Never** use `npx convex deploy` during development

## Agent Mode (Cloud Coding Agents Only)

For cloud agents (Jules, Devin, Cursor Cloud) that can't log in locally:

```bash
# .env.local
CONVEX_AGENT_MODE=anonymous
```

**Not needed for:** local development, Claude Code CLI, your own terminal. Just use `npx convex dev` normally.

## Components for Encapsulation

Use Convex components to encapsulate features as self-contained mini-backends:

- Sandboxed — can't access main app tables unless explicitly passed
- Self-contained — own schema, functions, and data
- npm-installable or local

```typescript
// convex.config.ts
import { defineApp } from "convex/server";
import rateLimit from "@convex-dev/rate-limiter/convex.config";

const app = defineApp();
app.use(rateLimit);
export default app;
```

Popular components: `@convex-dev/rate-limiter`, `@convex-dev/crons`, `@convex-dev/aggregate`.
