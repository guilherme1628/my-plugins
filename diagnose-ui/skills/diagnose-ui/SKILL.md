---
name: diagnose-ui
description: Systematic diagnostic process for fixing visual bugs, layout issues, spacing problems, or anything that looks wrong in the UI. Use when fixing CSS, layout, overflow, alignment, or visual inconsistencies.
---

# Diagnose UI

Systematic diagnostic process for fixing UI/UX issues. Follow every step before writing any fix.

## When to Use

Any time you need to fix a visual bug, layout issue, spacing problem, or anything that "looks wrong" in the interface.

## The Rule

**Do NOT touch code until you complete Steps 1-3.** Jumping to a fix without diagnosis is how we get whack-a-mole CSS patches that break other things.

---

## Step 0: Understand the Problem

Before anything, state clearly:
- **What is wrong?** (e.g. "the table scrolls the entire page instead of just the table body")
- **What should happen instead?** (e.g. "only the table body should scroll, header and footer stay sticky")
- **Where?** (exact file path and component)

If you cannot articulate all three, ask the user before proceeding.

---

## Step 1: Trace the Layout Chain

Starting from the viewport, trace every ancestor of the broken element. For each node, note:

```
viewport (100vh)
  └─ root layout (h-svh? overflow-hidden? flex?)
       └─ page container (flex-1? min-h-0?)
            └─ section/container (??? | ???)
                 └─ broken element (??? | ???)
```

For each ancestor, record:
1. **Display mode** — flex, grid, or block?
2. **Overflow** — hidden, auto, scroll, or visible?
3. **Size constraints** — h-*, min-h-*, max-h-*, flex-1?
4. **The critical question: is THIS the container that controls the behavior I'm trying to fix?**

**The fix almost always belongs on an ancestor, not on the element itself.** If you find yourself adding CSS to the broken element, STOP and re-check — you're probably targeting the wrong node.

### Common Layout Chain Breaks
- Missing `min-h-0` on a flex child → child ignores parent's overflow constraint
- Missing `overflow-hidden` on page root → content pushes viewport
- Missing `flex-1` → container doesn't fill available space
- `min-h-svh` instead of `h-svh` → allows growth beyond viewport
- `min-w-0` has no effect in table cells — use `w-full overflow-hidden` instead

---

## Step 2: Check Inherited and Applied Styles

Before adding ANY new CSS, understand what's already there.

### 2a: Read the component source
If the element uses a UI library component (shadcn, Bits UI, etc.), read its source file. Check for default classes that may conflict with your fix.

**Common gotchas:**
- Table header cells often have semi-transparent backgrounds — bleeds through on scroll
- Table row hover applies to ALL cells including headers
- Card/Dialog components have default padding — don't double up
- Table cells may have `whitespace-nowrap` — prevents text wrapping but allows overflow

### 2b: Check global CSS
Read the global stylesheet for custom classes, CSS variable definitions, and styles that may affect the element.

### 2c: Check the design system
If a design system exists (e.g. `system.md`, design tokens), recall the spacing scale, border radius, depth, and typography conventions.

**Never use arbitrary values** (`h-[347px]`, `mt-[13px]`) when a design token exists.

### 2d: Check component patterns
If the issue involves reactivity, props, or component behavior (not just CSS), consult framework-specific documentation or skills.

---

## Step 3: Diagnose Root Cause

Ask: **"Why does this look wrong?"** — not "How do I make it look right?"

| Symptom | Likely Root Cause | Investigation |
|---------|------------------|---------------|
| Content overflows viewport | Broken flex chain — missing `min-h-0` or `overflow-hidden` on an ancestor | Trace layout chain (Step 1) |
| Element wrong size/position | Fixing the wrong container — the parent or grandparent controls this | Identify controlling container (Step 1) |
| Spacing looks off | Token violation or inherited padding | Check design system + component defaults (Step 2) |
| Hover/focus looks wrong | Inherited styles from component library or Tailwind defaults | Read component source (Step 2a) |
| Column overflow in tables | `table-layout: fixed` without `overflow-hidden` on cells, or `min-w-0` used in table context (no-op) | Use `w-full overflow-hidden` on cell content |
| Color/shadow/border inconsistency | Design system violation | Check design tokens |
| Component behaves unexpectedly | Wrong API usage or framework reactivity issue | Check framework docs (Step 2d) |

**Red flags that you're about to fix a symptom:**
- You're adding `calc()` with magic numbers
- You're using `!important` without understanding what you're overriding
- You're adding negative margins
- You're using absolute positioning to escape layout flow
- You're adding `max-h-[calc(100vh-XXXpx)]` instead of using flex containment
- The fix works on one page but you're not sure it'll work on others

---

## Step 4: Fix at the Correct Level

Now — and only now — write the fix.

1. **Apply the fix to the controlling container** identified in Step 1
2. **Use design system tokens**, never arbitrary values
3. **Match existing patterns** — if another page solves the same problem, use the same approach
4. **Check the fix doesn't break siblings** — changing a parent's layout affects all children

---

## Step 5: Verify

Check ALL of these after the fix. Not just "it looks right now."

- [ ] **Scroll states** — scroll to top, middle, bottom. Does the fix hold?
- [ ] **Hover states** — hover over the fixed element AND its siblings. Any bleed-through?
- [ ] **Empty state** — what does it look like with no data?
- [ ] **Full state** — what does it look like with lots of data?
- [ ] **Responsive** — does it work at different viewport sizes?
- [ ] **Dark mode** — if applicable, check dark mode too
- [ ] **Other pages** — if you changed a shared component, check all pages that use it
