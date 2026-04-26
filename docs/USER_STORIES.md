# CarryMem User Stories

**Understanding our users and their needs**

---

## User Personas

### 1. Alex - The AI-Powered Developer

**Background**:
- Full-stack developer at a tech startup
- Uses multiple AI coding assistants (Cursor, Windsurf, GitHub Copilot)
- Works on 3-5 projects simultaneously
- Frustrated by repeating preferences to AI

**Goals**:
- AI remembers coding style preferences
- Consistent experience across tools
- Project-specific memory isolation

**Pain Points**:
- ❌ Repeats "I prefer TypeScript" every conversation
- ❌ AI forgets corrections from previous sessions
- ❌ Switching tools means starting from scratch

**Quote**: *"I spend more time teaching AI my preferences than actually coding."*

---

### 2. Sarah - The Product Manager

**Background**:
- Product manager at a SaaS company
- Uses AI for brainstorming, documentation, analysis
- Needs AI to remember project decisions
- Works with distributed team across timezones

**Goals**:
- AI remembers project decisions and context
- Easy to share memory profiles with team
- Track decision history

**Pain Points**:
- ❌ AI doesn't remember previous decisions
- ❌ Team members get inconsistent AI responses
- ❌ No way to export/share AI context

**Quote**: *"I wish AI could remember what we decided last week."*

---

### 3. Dr. Chen - The Researcher

**Background**:
- PhD researcher in machine learning
- Uses AI for literature review, code experiments
- Needs AI to remember research context
- Works on long-term projects (months/years)

**Goals**:
- AI remembers research context and findings
- Long-term memory persistence
- Integration with note-taking tools (Obsidian)

**Pain Points**:
- ❌ AI forgets research context between sessions
- ❌ No integration with existing knowledge base
- ❌ Can't track how understanding evolved

**Quote**: *"My research spans months, but AI's memory spans minutes."*

---

## Core User Stories

### Story 1: Remember My Coding Style

**As** Alex (Developer)  
**I want** AI to remember my coding preferences  
**So that** I don't have to repeat them every conversation

**Acceptance Criteria**:
- ✅ Store preference: "I prefer TypeScript over JavaScript"
- ✅ AI automatically applies preference in future conversations
- ✅ Works across different AI tools (Cursor, Windsurf)

**Example**:
```python
# First conversation
cm.store("I prefer using TypeScript")
cm.store("I like functional programming style")

# Next conversation (even in different tool)
memories = cm.recall("coding style")
# AI generates TypeScript with functional style
```

**Success Metric**: 90%+ of coding preferences remembered and applied

---

### Story 2: Correct AI Mistakes

**As** Alex (Developer)  
**I want** AI to remember my corrections  
**So that** it doesn't make the same mistake twice

**Acceptance Criteria**:
- ✅ Store correction: "No, I meant Python 3.11, not 3.10"
- ✅ AI remembers correction for future
- ✅ High confidence (0.95+) for corrections

**Example**:
```python
# Correction
cm.store("No, I use PostgreSQL, not MySQL")

# Later
memories = cm.recall("database")
# AI knows: PostgreSQL, not MySQL
```

**Success Metric**: 95%+ of corrections remembered

---

### Story 3: Project Isolation

**As** Alex (Developer)  
**I want** separate memories for different projects  
**So that** project A's decisions don't affect project B

**Acceptance Criteria**:
- ✅ Create namespace per project
- ✅ Memories don't leak between namespaces
- ✅ Easy to switch between projects

**Example**:
```python
# Project A
cm_a = CarryMem(namespace="project-a")
cm_a.store("Use React for frontend")

# Project B
cm_b = CarryMem(namespace="project-b")
cm_b.store("Use Vue for frontend")

# No interference!
```

**Success Metric**: 100% isolation between namespaces

---

### Story 4: Cross-Tool Portability

**As** Alex (Developer)  
**I want** to use same memories across different AI tools  
**So that** I don't lose context when switching tools

**Acceptance Criteria**:
- ✅ Export memories from Cursor
- ✅ Import memories to Windsurf
- ✅ All memories preserved

**Example**:
```python
# In Cursor
cm_cursor = CarryMem()
cm_cursor.export_memories("my_memories.json")

# In Windsurf
cm_windsurf = CarryMem()
cm_windsurf.import_memories("my_memories.json")
# All memories restored!
```

**Success Metric**: 100% of memories successfully transferred

---

### Story 5: Team Memory Sharing

**As** Sarah (Product Manager)  
**I want** to share memory profiles with my team  
**So that** everyone gets consistent AI responses

**Acceptance Criteria**:
- ✅ Export team decisions as memory profile
- ✅ Team members can import profile
- ✅ Consistent AI behavior across team

**Example**:
```python
# Sarah exports team decisions
cm.export_memories("team_decisions.json", 
                   filters={"type": "decision"})

# Team member imports
cm_member = CarryMem(namespace="team")
cm_member.import_memories("team_decisions.js``

**Success Metric**: 80%+ team adoption

---

### Story 6: Decision History

**As** Sarah (Product Manager)  
**I want** to view history of project decisions  
**So that** I can track how we got here

**Acceptance Criteria**:
- ✅ List all decisions chronologically
- ✅ Filter by date range
- ✅ Export as readable format

**Example**:
```python
# View decisions
decisions = cm.recall("", filters={"type": "decision"})
for d in decisions:
    print(f"{d['created_at']}: {d['content']}")

# Export as Markdown
cm.export_memories("decisions.md", 
                   format="markdown",
                   filters={"type": "decision"})
```

**Success Metric**: 100% of decisions trackable

---

### Story 7: Knowledge Base Integration

**As** Dr. Chen (Researcher)  
**I want** AI to access my Obsidian notes  
**So that** it has full research context

**Acceptance Criteria**:
- ✅ Index Obsidian vault
- ✅ Query notes semantically
- ✅ Combine with personal memories

**Example**:
```python
from memory_classification_engine.adapters import ObsidianAdapter

cm = CarryMem(knowledge_adapter=ObsidianAdapter("/path/to/vault"))
cm.index_knowledge()

# Query both memories and notes
results = cm.recall_from_knowledge("transformer architecture")
```

**Success Metric**: 90%+ relevant notes found

---

### Story 8: Long-Term Persistence

**As** Dr. Chen (Researcher)  
**I want** memories to persist for months/years  
**So that** AI remembers long-term research context

**Acceptance Criteria**:
- ✅ No automatic expiration for important memories
- ✅ Memories survive system upgrades
- ✅ Backup and restore capability

**Example**:
```python
# Store important research f.declare("Key finding: Attention mechanism improves accuracy by 15%")
# confidence=1.0, never expires

# Months later
memories = cm.recall("attention mechanism")
# Still there!
```

**Success Metric**: 100% of declared memories persist

---

## User Journey Map

### Alex's Journey: From Frustration to Flow

**Phase 1: Discovery** (Day 1)
- 😤 Frustrated by repeating preferences
- 🔍 Discovers CarryMem
- ⚡ Installs in 5 minutes

**Phase 2: First Use** (Day 1-3)
- 📝 Stores first preferences
- ✅ AI remembers them!
- 😊 Saves 10+ minutes per day

**Phase 3: Adoption** )
- 🚀 Uses across multiple projects
- 🔄 Exports/imports between tools
- 💡 Realizes full value

**Phase 4: Advocacy** (Month 1+)
- ⭐ Recommends to team
- 📢 Shares on social media
- 🤝 Contributes to project

---

## Pain Points → Solutions

| Pain Point | CarryMem Solution |
|------------|-------------------|
| AI forgets preferences | Auto-classification + storage |
| Repeating same info | Smart recall |
| Switching tools loses context | Export/import |
| No project isolation | Namespaces |
| Can't share with team | Memory profiles |
| No decision history | Filterable recall |
| Disconnected from notes | Obsidian integration |
| Short-term memory only | Long-term persistence |

---

## Success Metrics

### User Satisfaction
- **Time Saved**: 10-30 minutes per day
- **Frustration Reduced**: 80%+
- **Tool Switching**: Seamless
- **Team Collaboration**: Improved

### Technical Metrics
- **Classification Accuracy**: 90.6%
- **Recall Latency**: <100ms
- **Memory Persistence**: 100%
- **Cross-Tool Compatibility**: 100%

---

## Feature Prioritization

### Must Have (P0)
- ✅ Auto-class- ✅ Smart recall
- ✅ Export/import
- ✅ Namespaces

### Should Have (P1)
- ✅ CLI tools
- ✅ Memory profiles
- ⏳ Team sharing
- ⏳ Obsidian integration

### Nice to Have (P2)
- ⏳ Web UI
- ⏳ Cloud sync
- ⏳ Analytics dashboard
- ⏳ Mobile app

---

## Next Steps

- 📊 Conduct user interviews
- 📈 Track usage metrics
- 🔄 Iterate based on feedback
- 🚀 Build P1 features

---

**Understanding users drives better product decisions** 🎯
