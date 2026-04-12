# MCP Server Beta Testing Guide

<p align="center">
  <a href="./BETA_TESTING_GUIDE_ZH.md">中文</a> ·
  <strong>English</strong>
</p>

---

## 🎯 Testing Objectives

Thank you for participating in the Memory Classification Engine MCP Server Beta test!

Your feedback will help us improve the product and make it better serve Claude Code users.

---

## 📦 Testing Package Contents

### 1. Project Repository

```bash
# Clone the repository
git clone https://github.com/lulin70/memory-classification-engine.git
cd memory-classification-engine
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# Or: venv\Scripts\activate  # Windows

# Install the project
pip install -e .

# Download models (required for first run)
python download_model.py
```

### 3. Configure Claude Code

```bash
# 1. Find Claude Code configuration directory
# macOS: ~/.config/claude/
# Windows: %APPDATA%/Claude/

# 2. Create or edit config.json
cat > ~/.config/claude/config.json << 'EOF'
{
  "mcpServers": {
    "memory-classification-engine": {
      "command": "python",
      "args": ["-m", "memory_classification_engine", "mcp"],
      "env": {
        "MCE_CONFIG_PATH": "$(pwd)/config/config.yaml",
        "MCE_DATA_PATH": "$(pwd)/data",
        "HF_DATASETS_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "HF_HOME": "$(pwd)/models"
      }
    }
  }
}
EOF

# 3. Restart Claude Code
```

---

## 🧪 Testing Scenarios

### Scenario 1: Basic Functionality Test (5 minutes)

**Objective**: Verify MCP Server works correctly

**Steps**:
1. Start Claude Code
2. Check MCP tools list (should show 8 tools)
3. Send a message: "I prefer using double quotes"
4. Observe if it automatically classifies and stores the memory

**Expected Results**:
- Claude Code displays available tools
- Message is correctly classified as user_preference
- Memory is stored

### Scenario 2: Memory Retrieval Test (5 minutes)

**Objective**: Verify memories can be correctly retrieved

**Steps**:
1. Tell Claude: "Remember, I prefer Python over JavaScript"
2. After a few minutes, ask: "What programming language did I say I preferred?"
3. Observe if Claude can recall your preference

**Expected Results**:
- Claude can retrieve previous memories
- Response accurately reflects your preference

### Scenario 3: Long Conversation Test (10 minutes)

**Objective**: Verify memory persistence across multiple conversation rounds

**Steps**:
1. Have 5-10 rounds of technical discussion
2. Naturally express preferences and decisions during conversation
   - "I think this solution is too complex"
   - "Our team uses PostgreSQL"
   - "Alice handles backend development"
3. Later in the conversation, ask about previous discussion topics

**Expected Results**:
- Important information is automatically remembered
- Claude can connect context
- Doesn't repeatedly ask for known information

### Scenario 4: Edge Case Test (5 minutes)

**Objective**: Test error handling

**Steps**:
1. Send a very short message: "ok"
2. Send a very long message (paste a large code block)
3. Send a meaningless message: "asdfgh"

**Expected Results**:
- Short/meaningless messages are correctly ignored
- Long messages are handled normally
- System doesn't crash

---

## 📊 Feedback Collection

### Required Questions

Please copy and fill out the following template:

```markdown
## Beta Testing Feedback

### Basic Information
- Test Date: 2026-XX-XX
- Claude Code Version: 
- Operating System: macOS/Windows/Linux
- Python Version: 

### Functionality Testing
1. Did MCP Server start normally?
   - [ ] Yes
   - [ ] No
   - Issue description: 

2. Do all 8 Tools work properly?
   - [ ] Yes
   - [ ] No
   - Which Tool has issues: 

3. Is memory classification accurate?
   - [ ] Very accurate
   - [ ] Quite accurate
   - [ ] Average
   - [ ] Not very accurate
   - Examples: 

4. Is memory retrieval effective?
   - [ ] Very effective
   - [ ] Quite effective
   - [ ] Average
   - [ ] Not very effective
   - Examples: 

### Performance Experience
5. How is the response speed?
   - [ ] Very fast (< 1 second)
   - [ ] Quite fast (1-3 seconds)
   - [ ] Average (3-5 seconds)
   - [ ] Slow (> 5 seconds)

6. Did you encounter any lag or crashes?
   - [ ] No
   - [ ] Occasionally
   - [ ] Frequently
   - Issue description: 

### Overall Evaluation
7. Would you recommend this to friends?
   - [ ] Definitely
   - [ ] Probably
   - [ ] Not sure
   - [ ] Probably not
   - [ ] Definitely not

8. Top 3 features you're most satisfied with:
   1. 
   2. 
   3. 

9. Top 3 areas that need improvement:
   1. 
   2. 
   3. 

10. Other suggestions:
    
```

---

## 🐛 Issue Reporting

If you encounter any issues, please submit an Issue on GitHub:

```
https://github.com/lulin70/memory-classification-engine/issues/new
```

**Issue Template**:

```markdown
**Title**: [Bug] Brief description

**Environment**:
- OS: 
- Python: 
- Claude Code Version: 

**Reproduction Steps**:
1. 
2. 
3. 

**Expected Result**:

**Actual Result**:

**Error Logs**:
```

---

## 💡 Usage Tips

### 1. Make Memories More Accurate

- Express preferences clearly: "I like...", "I prefer..."
- Express corrections clearly: "No, it should be..."
- Express decisions clearly: "We decided..."

### 2. Optimize Retrieval Effectiveness

- Use keyword queries: "My previous Python preference"
- Provide context: "Regarding the code style discussion"

### 3. Avoid Misclassification

- Avoid vague expressions: "This is okay"
- Avoid temporary thoughts: "Maybe we could try..."

---

## 📞 Contact Information

If you have any questions, you can contact us through:

- GitHub Issues: https://github.com/lulin70/memory-classification-engine/issues
- GitHub Discussions: https://github.com/lulin70/memory-classification-engine/discussions
- Email: [your email]

---

## 🎁 Thank You

Thank you again for participating in the Beta test!

Your feedback is very important to us and will directly influence the final form of the product.

After completing the test, you will:
- Get priority access to the official release
- Be listed in the project Contributors
- Receive a detailed test report

---

**Testing Package Version**: v0.1.0-beta  
**Last Updated**: 2026-04-11  
**Estimated Testing Time**: 30-60 minutes
