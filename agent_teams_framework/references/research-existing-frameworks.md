# Research Report: Existing Frameworks, Strategies & Best Practices for Multi-Agent Development Workflows

**Date**: 2026-03-30
**Researcher**: Frameworks Researcher (Agent Teams Research)

---

## 1. Claude Code Ecosystem

### 1.1 Built-in Agent Teams (Native Feature)

Claude Code v2.1.32+ includes experimental Agent Teams. Released with Opus 4.6 on February 5, 2026.

**Architecture:**
- **Team Lead**: Main Claude Code session that spawns and orchestrates teammates
- **Teammates**: Independent Claude Code processes, each with own context window and full tool access (2-16 agents)
- **Shared Task List**: Coordination backbone with statuses, ownership, and dependency relationships
- **Mailbox System**: Peer-to-peer messaging via SendMessage tool

**Validated strengths:**
- Works well for parallel, loosely coupled tasks (code review, research, independent modules)
- Anthropic's own case study: 16 agents built a 100,000-line C compiler (compiles Linux 6.9) over ~2,000 sessions at $20K cost
- Trivial parallelization when there are many distinct failing tests (each agent picks a different test)
- Enables specialization: one agent for dedup, one for perf, one for code quality

**Known problems (validated by multiple sources):**
- No session recovery: if terminal closes/crashes, teammates don't recover; `/resume` only restores the lead
- One session = one team (no parallel teams, no nesting)
- Communication failures: teammates sometimes don't receive messages; team lead loses track of stuck agents
- ~3-7x token overhead vs single session
- Permissions friction: asks for write permission on everything, amplified with multiple agents
- Research depth thinner than dedicated orchestrators (fewer sources, less thorough exploration)
- Tightly coupled tasks (frontend + backend sharing contracts) work better with a single agent

**Sources:**
- https://code.claude.com/docs/en/agent-teams
- https://www.anthropic.com/engineering/building-c-compiler
- https://claudefa.st/blog/guide/agents/agent-teams
- https://medium.com/@derekcashmore/claude-code-agent-teams-vs-claude-flow-a-real-world-bake-off-97e24f6ca9b9
- https://addyosmani.com/blog/claude-code-agent-teams/

### 1.2 Superpowers Plugin (obra/superpowers)

The most popular Claude Code plugin. Provides a structured software development methodology with composable skills.

**Relevant capabilities:**
- Subagent-driven development: dispatches fresh subagents per task with two-stage review (spec compliance, then code quality)
- Skills for TDD, systematic debugging, brainstorming, planning, code review
- Subagents get custom system prompts, specific tool access, and independent permissions
- Skills distributed with plugins, auto-update

**Current limitation:** As of March 2026, Superpowers has skills for subagent-driven development but lacks awareness of the newer Agent Teams primitives (TeammateTool, SendMessage, TaskList). There are open GitHub issues (#429, #469) requesting this integration.

**Sources:**
- https://github.com/obra/superpowers
- https://github.com/obra/superpowers/issues/429
- https://github.com/obra/superpowers/issues/469
- https://blog.devgenius.io/superpowers-explained-the-claude-plugin-that-enforces-tdd-subagents-and-planning-c7fe698c3b82

### 1.3 Conductor Plugin (wshobson/agents)

Part of a massive 72-plugin system with 112 specialized agents.

**Architecture:**
- Implements "Context-Driven Development": Context -> Spec & Plan -> Implement
- Track-based development: generates specifications and phased implementation plans
- Agent Teams plugin included with preset teams: review, debug, feature, fullstack, research, security, migration
- Originated from Google's Conductor (built for Gemini CLI), adapted for Claude Code

**Assessment:** Very comprehensive but potentially over-engineered for most workflows. The sheer number of agents (112) and skills (146) suggests quantity over curation.

**Sources:**
- https://github.com/wshobson/agents
- https://github.com/wshobson/agents/tree/main/plugins/conductor
- https://github.com/wshobson/agents/tree/main/plugins/agent-teams

### 1.4 Other Claude Code Orchestration Projects

| Project | Approach | Notes |
|---------|----------|-------|
| **oh-my-claudecode** | Teams-first orchestration, 32 agents, 40+ skills, Ultrapilot mode (5 concurrent workers) | Auto model routing (Haiku for simple, Opus for complex) saves 30-50% tokens |
| **claude-code-workflow-orchestration** (barkain) | Hook-based framework enforcing task delegation to specialized agents | Supports native Agent Teams for real-time collaboration |
| **claude-mpm** | Multi-channel orchestration, GitHub-first SDK mode, 47+ agents | Heavy on project management |
| **ruflo** | "Kubernetes for AI agents" — distributed swarm intelligence, RAG integration | Ambitious scope, unclear real-world validation |
| **code-conductor** (ryanmac) | GitHub-native orchestration, parallel subagents, no conflicts | Focused on shipping speed |
| **ComposioHQ/agent-orchestrator** | Each agent gets own worktree, branch, and PR | Clean isolation model |
| **Claude-Code-Workflow** (catlog22) | JSON-driven multi-agent cadence-team framework | Context-first architecture |

---

## 2. Broader Multi-Agent Frameworks

### 2.1 Framework Comparison

| Framework | Orchestration Model | State Management | Sweet Spot |
|-----------|-------------------|------------------|------------|
| **LangGraph** | Directed graphs with conditional edges | Built-in checkpointing with time travel | Maximum control, compliance, production-grade state |
| **CrewAI** | Role-based crews with process types | Sequential task output passing | Fast prototyping, lowest learning curve (~20 lines to start) |
| **AutoGen/AG2** | Conversational GroupChat | Conversation history (in-memory default) | Iterative refinement, code gen, research, creative tasks |

### 2.2 Key Patterns from Broader Frameworks

**Role Assignment (CrewAI pattern):**
Each agent gets a role, goal, and backstory. Tasks are assigned to specific roles. Simple mental model, works well for well-defined workflows. Limitation: rigid role boundaries can cause gaps.

**Graph-Based Orchestration (LangGraph):**
Workflows as directed graphs with conditional routing. Supports cycles, branching, and merging. Best for complex state machines. Limitation: high complexity ceiling.

**Conversational Coordination (AutoGen):**
Agents communicate through conversation in GroupChat. Each turn is an LLM call with accumulated history. Natural feeling but expensive — a 4-agent debate with 5 rounds = 20+ LLM calls minimum.

**Hub-and-Spoke / Orchestrator-Worker:**
Primary agent coordinates specialist sub-agents. Each sub-agent gets isolated context (only relevant info). Prevents cross-contamination. This is the dominant pattern in Claude Code ecosystem.

**Sources:**
- https://dev.to/pockit_tools/langgraph-vs-crewai-vs-autogen-the-complete-multi-agent-ai-orchestration-guide-for-2026-2d63
- https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen

### 2.3 Transferable Insights

**What works across frameworks:**
- Task decomposition before parallelization
- Isolated context per agent (no shared mega-context)
- Explicit dependency management between tasks
- Single-writer rule for shared resources

**What doesn't transfer well to Claude Code:**
- LangGraph's graph-based state machines (Claude Code agents are more free-form)
- CrewAI's rigid role DSL (Claude Code agents are general-purpose)
- AutoGen's conversational GroupChat (Claude Code uses task lists + messages, not open chat)

---

## 3. Context Generation Strategies

### 3.1 CLAUDE.md / AGENTS.md as Context

**Best practice (validated):**
- CLAUDE.md should contain as few instructions as possible — only universally applicable ones
- Task-specific instructions go in separate markdown files (building_the_project.md, running_tests.md, code_conventions.md)
- AGENTS.md provides high-level architectural overviews, coding style, known bugs/solutions
- Each subagent should only see files relevant to its task (isolated context prevents cross-contamination)

**Source:** https://www.humanlayer.dev/blog/writing-a-good-claude-md

### 3.2 Context Compression Techniques

**ACON (Agent Context Optimization):**
- Treats compression as optimization using paired trajectory analysis
- Finds cases where full context succeeded but compressed context failed
- Revises compression prompts to preserve critical information classes
- 26-54% reduction in peak token usage, gradient-free, works with any API model

**Agentic Context Engineering (ACE):**
- Treats contexts as evolving playbooks that accumulate and refine strategies
- Avoids "brevity bias" (dropping domain insights for concise summaries) and "context collapse" (iterative rewriting eroding details)

**Critical finding:** 65% of enterprise AI failures in 2025 were attributed to context drift or memory loss during multi-step reasoning — not raw context exhaustion. The problem is quality, not quantity.

**Sources:**
- https://arxiv.org/abs/2510.04618
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html

### 3.3 Practical Context Strategies for Multi-Agent

1. **Contextual delegation to subagents**: Run tests, fetch docs, process logs in subagent context; only summary returns to main conversation
2. **Dynamic model selection**: Route simple tasks to cheaper models (Haiku), complex reasoning to premium (Opus) — 40-60% cost reduction
3. **Prompt caching**: Reuse system prompts/CLAUDE.md across requests; cached reads cost a fraction
4. **Auto-compaction**: Summarize conversation history when approaching context limits (built into Claude Code)
5. **Compound learning via AGENTS.md**: Accumulate patterns and gotchas across sessions so every session makes the next one better

---

## 4. Worktree-Based Development Patterns

### 4.1 Git Worktree Isolation

**Pattern (validated, widely adopted):**
- Each agent gets its own git worktree (separate checkout, own branch, own working directory, own index)
- Use `--worktree` (`-w`) flag in Claude Code or `isolation: worktree` in agent frontmatter
- Worktrees auto-cleanup when subagent finishes without changes
- Especially valuable for batched code migrations: spawn N agents, each handling M files

**Sources:**
- https://code.claude.com/docs/en/common-workflows
- https://claudefa.st/blog/guide/development/worktree-guide
- https://github.com/spillwavesolutions/parallel-worktrees

### 4.2 Conflict Prevention & Resolution

**Clash (clash-sh/clash):**
- Rust CLI that detects merge conflicts between all worktree pairs in real-time
- Uses `git merge-tree` via gix library — 100% read-only, never modifies repository
- Designed specifically for multi-AI-agent workflows
- Detects conflicts before Claude Code writes a file
- Resolution suggestions planned for future version

**Strategies for preventing conflicts:**
1. **Single-writer rule**: Designate one agent as owner of shared/hotspot files
2. **Merge early and often**: Don't let branches diverge for days
3. **Sequential merge**: Merge first completed branch into main, rebase remaining branches

**Source:** https://github.com/clash-sh/clash

### 4.3 Gas Town (steveyegge/gastown)

**Architecture (promising, significant community interest):**
- "Kubernetes for AI coding agents"
- Uses Git as state machine — all state persists in "Beads" (git-backed issue tracking)
- Operational roles: Mayor (orchestrator), Polecats (workers), Witness/Deacon (monitors), Refinery (merges)
- Each worker gets a git worktree + a task from Beads
- Bead IDs use prefix + 5-char alphanumeric format (e.g., gt-abc12)
- Full provenance: agents query past beads through task graphs and SQL-addressable data plane

**Sources:**
- https://github.com/steveyegge/gastown
- https://maggieappleton.com/gastown
- https://softwareengineeringdaily.com/2026/02/12/gas-town-beads-and-the-rise-of-agentic-development-with-steve-yegge/

---

## 5. Emerging Patterns & Real-World Usage

### 5.1 The 3 Amigo Agents Pattern

**Pattern:** Three specialized agents — PM Agent (requirements), UX Designer Agent (design), Claude Code (implementation).

**Claims:** Reduced development from weeks to hours. Based on Anthropic's research showing 90.2% performance improvement with multi-agent over single-agent systems.

**Assessment:** Interesting concept but the "weeks to hours" claim needs skepticism. Works best for greenfield MVPs where requirements are clear. Less applicable to maintenance, debugging, or incremental feature work.

**Source:** https://medium.com/@george.vetticaden/the-3-amigo-agents-the-claude-code-development-pattern-i-discovered-while-implementing-anthropics-67b392ab4e3f

### 5.2 The Ralph Loop Pattern (from Addy Osmani)

**Pattern:** Breaks development into small atomic tasks. Runs an agent in a stateless-but-iterative loop:
1. Pick a task
2. Implement
3. Validate
4. Commit if passing
5. Reset context
6. Repeat

**Assessment:** Promising for routine, well-defined tasks. Context reset prevents drift. Not suitable for tasks requiring deep accumulated understanding.

**Source:** https://addyosmani.com/blog/code-agent-orchestra/

### 5.3 Conductor vs Orchestrator Model (Addy Osmani)

**Conductor model:** One agent, synchronous, context window as hard ceiling. Engineer guides in real time.

**Orchestrator model:** Multiple agents with own context windows, working asynchronously. Engineer plans and checks in.

The engineer's role evolves from implementer to conductor to orchestrator.

**Sources:**
- https://addyosmani.com/blog/future-agentic-coding/
- https://www.oreilly.com/radar/conductors-to-orchestrators-the-future-of-agentic-coding/

### 5.4 Token Cost Realities

| Approach | Token Multiplier | Notes |
|----------|-----------------|-------|
| Single session | 1x | Baseline |
| Agent Teams (plan mode) | ~7x | Each teammate has own context |
| Agent Teams (practical) | ~3-4x | Real-world for 3 teammates |
| With model routing | ~2-3x | Haiku for simple, Opus for complex |
| With prompt caching | Further 30-50% reduction | Reusing system prompts |

---

## 6. Assessment Matrix

### Validated (Evidence + Working Examples)

| Finding | Evidence |
|---------|----------|
| **Worktree isolation is the right approach for parallel agents** | Adopted by Claude Code natively, Gas Town, Clash, multiple orchestrators |
| **Hub-and-spoke (orchestrator-worker) is the dominant pattern** | Used by Agent Teams, Superpowers, oh-my-claudecode, conductor, most frameworks |
| **Task lists with dependencies beat open-ended conversation** | Claude Code Agent Teams, Gas Town Beads, LangGraph state |
| **Single-writer rule for shared files prevents conflicts** | Clash documentation, Intility engineering blog, multiple practitioners |
| **Context isolation per agent is critical** | Every framework implements this; 65% of failures come from context drift |
| **Agent Teams work best for loosely coupled, parallel tasks** | Anthropic C compiler study, multiple comparison blog posts |
| **3-7x token overhead is real and unavoidable** | Multiple independent measurements |

### Promising (Worth Exploring, Not Fully Proven)

| Finding | Why Promising |
|---------|--------------|
| **Git-as-state-machine (Gas Town Beads)** | Elegant persistence model, full provenance, but Gas Town is complex and Go-based |
| **ACON context compression** | 26-54% token reduction in research; no Claude Code integration yet |
| **Dynamic model routing** | oh-my-claudecode claims 30-50% savings; validated concept but requires careful tuning |
| **Ralph Loop (stateless iteration)** | Prevents context drift for routine tasks; unclear how well it handles complex cross-cutting work |
| **Clash for real-time conflict detection** | Solves a real problem; still young (no resolution, only detection) |
| **Compound learning via AGENTS.md** | Good concept; limited tooling for automatic accumulation |

### Overhyped (Sound Good, Don't Work Well in Practice)

| Finding | Why Overhyped |
|---------|---------------|
| **"112 agents, 146 skills" mega-frameworks** | Quantity != quality. Most tasks need 3-5 well-defined roles, not 112. Maintenance burden is enormous |
| **AutoGen-style conversational GroupChat for code** | Expensive (20+ LLM calls for simple debates), hard to control, agents talk past each other |
| **Rigid role-based DSL (CrewAI-style)** | Too constraining for Claude Code's general-purpose agents; real tasks don't fit neat role boxes |
| **"Weeks to hours" productivity claims** | Greenfield MVPs only. Maintenance, debugging, and integration work doesn't see these gains |
| **Nested agent teams (teams spawning sub-teams)** | Not supported by Claude Code, and for good reason — coordination overhead grows exponentially |
| **Universal orchestration frameworks** | Every project's needs differ; a framework that handles everything handles nothing well |
| **"Kubernetes for AI agents" analogies** | Sounds impressive but agents aren't containers — they have context, drift, and judgment; orchestrating them is fundamentally different |

---

## 7. Key Takeaways for Our Framework

### What to Build On
1. **Worktree isolation is table stakes** — every serious approach uses it
2. **Task list with dependencies** is the right coordination primitive (not free-form chat)
3. **Context generation should be minimal and targeted** — each agent gets only what it needs
4. **Start with 3-5 agent roles**, not 112
5. **Hub-and-spoke with a team lead** is the proven pattern
6. **Git-backed state** for durability (learn from Gas Town without the complexity)

### What to Avoid
1. Don't over-engineer agent roles — keep them general enough to be useful
2. Don't build an "everything framework" — focus on the workflows that actually matter
3. Don't ignore token costs — build cost awareness into the framework from day one
4. Don't assume agents will coordinate perfectly — build in health checks and recovery
5. Don't try to replicate LangGraph/CrewAI patterns — Claude Code's Agent Teams already provides the primitives

### Gaps in the Ecosystem
1. **No good recovery story** for crashed/lost agent sessions
2. **No standard context generation tooling** for multi-agent workflows
3. **Conflict prevention is detection-only** (Clash) — no automated resolution
4. **No framework bridges Superpowers skills with Agent Teams primitives**
5. **Token cost monitoring** is ad-hoc — no built-in budget management per agent
6. **No standard pattern for agents accumulating and sharing learnings** across sessions
