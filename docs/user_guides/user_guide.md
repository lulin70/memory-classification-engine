# Memory Classification Engine User Guide

## 1. Introduction

Memory Classification Engine is an intelligent memory management system that automatically classifies, stores, and retrieves user memories. This guide will help you understand how to use the various features of the Memory Classification Engine to fully leverage its capabilities.

## 2. Basic Usage

### 2.1 Initializing the Engine

```python
from memory_classification_engine import MemoryClassificationEngine

# Initialize the engine
engine = MemoryClassificationEngine()
```

### 2.2 Processing Messages

```python
# Process user message
user_message = "Remember, I don't like using dashes in code"
result = engine.process_message(user_message)
print(result)
# Output: {"matched": true, "memory_type": "user_preference", "tier": 2, "content": "Don't like using dashes in code", "confidence": 1.0, "source": "rule:0"}
```

### 2.3 Retrieving Memories

```python
# Retrieve memories
memories = engine.retrieve_memories("code style")
print(memories)
```

### 2.4 Processing Feedback

```python
# Process user feedback
memory_id = "your_memory_id"
feedback = {"type": "positive", "comment": "This memory is accurate"}
result = engine.process_feedback(memory_id, feedback)
print(result)
```

### 2.5 Optimizing the System

```python
# Optimize the system
result = engine.optimize_system()
print(result)
```

### 2.6 Compressing Memories

```python
# Compress memories
tenant_id = "your_tenant_id"
result = engine.compress_memories(tenant_id)
print(result)
```

## 3. Agent Framework Usage

### 3.1 Registering an Agent

```python
# Register an agent
agent_config = {
    'adapter': 'claude_code',  # Supported adapters: claude_code, work_buddy, trae, openclaw
    'api_key': 'your_api_key'  # API key if needed
}
result = engine.register_agent('my_agent', agent_config)
print(result)
```

### 3.2 Listing Agents

```python
# List all registered agents
result = engine.list_agents()
print("Registered agents:", result)
```

### 3.3 Processing Messages with an Agent

```python
# Process message with agent
result = engine.process_message_with_agent('my_agent', "Hello, world!")
print("Agent processing result:", result)
```

### 3.4 Unregistering an Agent

```python
# Unregister an agent
result = engine.unregister_agent('my_agent')
print(result)
```

## 4. Knowledge Base Integration

### 4.1 Writing Memories Back to Knowledge Base

```python
# Write memory back to knowledge base
memory_id = "your_memory_id"
result = engine.write_memory_to_knowledge(memory_id)
print("Write back to knowledge base result:", result)
```

### 4.2 Getting Knowledge from Knowledge Base

```python
# Get relevant knowledge from knowledge base
result = engine.get_knowledge("science fiction novels")
print("Knowledge base retrieval result:", result)
```

### 4.3 Synchronizing Knowledge Base

```python
# Synchronize knowledge base
result = engine.sync_knowledge_base()
print("Knowledge base synchronization result:", result)
```

### 4.4 Getting Knowledge Base Statistics

```python
# Get knowledge base statistics
result = engine.get_knowledge_statistics()
print("Knowledge base statistics:", result)
```

## 5. Advanced Features

### 5.1 VS Code Extension

#### 5.1.1 Installation and Configuration

1. **Install the extension**:
   - Open VS Code or Cursor
   - Click on the extensions icon (left sidebar)
   - Search for "Memory Classification Engine"
   - Click "Install"

2. **Configure the extension**:
   - Open VS Code settings (File → Preferences → Settings)
   - Search for "Memory Classification Engine"
   - Configure the MCP server address (default is http://localhost:8000)

#### 5.1.2 Using the Extension

1. **Viewing memories**:
   - Click on the "Memory Classification Engine" icon in the left sidebar
   - Expand different memory types to view memories

2. **Memory operations**:
   - Right-click on a memory and select "Recall" to view details
   - Right-click on a memory and select "Forget" to delete it
   - Click the "Export" button at the top to export memories
   - Click the "Import" button at the top to import memories

### 5.2 Memory Quality Dashboard

#### 5.2.1 Accessing the Dashboard

1. **Start the server**:
   ```bash
   cd memory-classification-engine
   python3 -m memory_classification_engine.api.server
   ```

2. **Access the dashboard**:
   - Open a browser and go to http://localhost:8000/dashboard/
   - View memory quality statistics and charts

#### 5.2.2 Using the Dashboard

1. **Time range filtering**:
   - Select different time ranges (7 days, 30 days, 90 days)
   - Click the "Refresh" button to update data

2. **Viewing detailed information**:
   - View memory quality trend charts
   - View memory type distribution
   - View memory quality details table

### 5.3 Pending Memories

#### 5.3.1 Adding Pending Memories

```python
# Add pending memory
memory = {
    'memory_type': 'user_preference',
    'content': 'I prefer using Python',
    'confidence': 0.95
}
memory_id = engine.add_pending_memory(memory)
print(f"Pending memory ID: {memory_id}")
```

#### 5.3.2 Processing Pending Memories

```python
# Get pending memories
pending_memories = engine.get_pending_memories()
print(f"Pending memories: {len(pending_memories)}")

# Approve memory
if pending_memories:
    memory_id = pending_memories[0]['id']
    success = engine.approve_memory(memory_id)
    print(f"Approved memory: {success}")

# Reject memory
if pending_memories:
    memory_id = pending_memories[0]['id']
    success = engine.reject_memory(memory_id)
    print(f"Rejected memory: {success}")

# Get pending memory count
count = engine.get_pending_count()
print(f"Pending memories count: {count}")
```

### 5.4 Nudge Mechanism

#### 5.4.1 Getting Nudge Candidates

```python
# Get nudge candidates
nudge_candidates = engine.get_nudge_candidates(limit=5)
print(f"Nudge candidates: {len(nudge_candidates)}")

# Generate nudge prompt
if nudge_candidates:
    prompt = engine.generate_nudge_prompt(nudge_candidates[0])
    print("Nudge prompt:")
    print(prompt)
```

#### 5.4.2 Recording Nudge Interactions

```python
# Record nudge interaction
if nudge_candidates:
    memory_id = nudge_candidates[0]['id']
    success = engine.record_nudge_interaction(memory_id, 'confirm')
    print(f"Recorded nudge interaction: {success}")

# Check if we should nudge
should_nudge = engine.should_nudge()
print(f"Should nudge: {should_nudge}")
```

### 5.5 Multi-tenant Management

```python
# Create tenant
tenant_id = "company_tenant"
result = engine.tenant_manager.create_tenant(
    tenant_id,
    "Company Tenant",
    "enterprise",
    user_id="admin"
)
print("Create tenant result:", result)

# Get tenant
tenant = engine.tenant_manager.get_tenant(tenant_id)
print("Tenant information:", tenant)

# List all tenants
tenants = engine.tenant_manager.list_tenants()
print("All tenants:", tenants)
```

### 5.6 Privacy Settings

```python
# Set user privacy settings
user_id = "user1"
settings = {
    "data_retention_days": 30,
    "enable_encryption": True,
    "share_with_agents": False
}
result = engine.privacy_manager.set_user_settings(user_id, settings)
print("Set privacy settings result:", result)

# Get user privacy settings
result = engine.privacy_manager.get_user_settings(user_id)
print("User privacy settings:", result)

# Export user data
result = engine.privacy_manager.export_user_data(user_id)
print("Export user data result:", result)

# Delete user data
result = engine.privacy_manager.delete_user_data(user_id)
print("Delete user data result:", result)
```

### 5.7 Audit Logs

```python
# View audit logs
logs = engine.audit_manager.get_logs(user_id="user1", action="process_message")
print("Audit logs:", logs)

# Generate audit report
report = engine.audit_manager.generate_report(start_time="2026-01-01", end_time="2026-01-31")
print("Audit report:", report)
```

### 5.8 Performance Monitoring

```python
# Get performance metrics
metrics = engine.performance_monitor.get_metrics()
print("Performance metrics:", metrics)

# Reset performance metrics
engine.performance_monitor.reset_metrics()
print("Performance metrics reset")
```

## 6. Best Practices

### 6.1 Memory Management

- **Regular optimization**: Regularly call `optimize_system()` to optimize system performance, recommended daily or weekly
- **Memory compression**: Regularly call `compress_memories()` to compress memories and reduce storage space, recommended monthly
- **Setting importance**: For important memories, set a higher importance level to ensure they won't be forgotten
- **Batch operations**: For large memory operations, use batch APIs instead of individual operations for efficiency
- **Memory tags**: Add tags to memories for easier retrieval and management

### 6.2 Agent Usage

- **Choose the right agent**: Select the appropriate agent framework based on task type, e.g., ClaudeCode for code generation, WorkBuddy for collaborative tasks
- **Manage agent lifecycle**: After using an agent, unregister it promptly to release resources
- **Configure agent parameters**: Configure agent parameters based on specific needs for optimal results
- **Agent combination**: For complex tasks, combine the capabilities of multiple agents
- **Error handling**: Add appropriate error handling for agent operations to improve system stability

### 6.3 Knowledge Base Integration

- **Set up Obsidian vault**: Ensure the Obsidian vault path is correctly set so memories can be properly written back to the knowledge base
- **Regular synchronization**: Regularly call `sync_knowledge_base()` to synchronize the knowledge base and ensure data consistency
- **Organize knowledge properly**: Organize knowledge in Obsidian using folders and tags
- **Knowledge links**: Create links between knowledge in Obsidian to form a knowledge network
- **Version control**: Consider using version control systems like Git to manage the Obsidian vault

### 6.4 Performance Optimization

- **Adjust cache size**: Adjust cache size based on system resources to balance performance and memory usage
- **Disable unnecessary features**: If certain features (like LLM or Neo4j) are not needed, disable them in the configuration file to improve performance
- **Optimize storage**: Regularly clean up unnecessary memories to reduce storage pressure
- **Batch processing**: For large data operations, use batch processing to reduce database access times
- **Asynchronous operations**: For time-consuming operations, consider using asynchronous processing to improve system response speed
- **Hardware optimization**: Based on system load, appropriately increase memory or use SSD storage

### 6.5 Security Best Practices

- **API key management**: Use environment variables or key management services to store API keys, avoid hardcoding
- **Data encryption**: Enable sensitive data encryption to protect user privacy
- **Access control**: Set appropriate access permissions to limit memory access
- **Audit logs**: Enable audit logs to record system operations
- **Regular backups**: Regularly back up memory data to prevent data loss

### 6.6 Common Usage Scenarios

#### 6.6.1 Intelligent Customer Service

```python
# Initialize engine
engine = MemoryClassificationEngine()

# Handle customer query
def handle_customer_query(user_id, query):
    # Retrieve relevant memories
    memories = engine.retrieve_memories(query, user_id=user_id)
    
    # Build context
    context = {
        "user_id": user_id,
        "previous_memories": memories
    }
    
    # Process query
    result = engine.process_message(query, context=context)
    
    # Store new memories
    if result.get("matches"):
        for match in result["matches"]:
            # Can add additional metadata
            match["user_id"] = user_id
            engine.manage_memory("edit", match["id"], match)
    
    return result
```

#### 6.6.2 Personal Assistant

```python
# Initialize engine
engine = MemoryClassificationEngine()

# Manage user preferences
def update_user_preference(user_id, preference):
    result = engine.process_message(
        f"User preference: {preference}",
        context={"user_id": user_id, "memory_type": "user_preference"}
    )
    return result

# Retrieve user preferences
def get_user_preferences(user_id):
    memories = engine.retrieve_memories(
        "user_preference",
        memory_type="user_preference",
        user_id=user_id
    )
    return memories

# Intelligent recommendations
def recommend_content(user_id, current_topic):
    # Retrieve relevant memories
    memories = engine.retrieve_memories(
        current_topic,
        user_id=user_id,
        limit=5
    )
    
    # Generate recommendations based on memories
    recommendations = []
    for memory in memories:
        if "preference" in memory.get("content", "").lower():
            recommendations.append(memory["content"])
    
    return recommendations
```

#### 6.6.3 Enterprise Knowledge Management

```python
# Initialize engine
engine = MemoryClassificationEngine()

# Create enterprise tenant
def create_company_tenant(company_id, company_name):
    result = engine.tenant_manager.create_tenant(
        company_id,
        company_name,
        "enterprise"
    )
    return result

# Share memory to team
def share_memory_to_team(memory_id, team_id):
    result = engine.manage_memory(
        "edit",
        memory_id,
        {"visibility": "team", "team_id": team_id}
    )
    return result

# Batch import company knowledge
def import_company_knowledge(company_id, knowledge_items):
    for item in knowledge_items:
        result = engine.process_message(
            item["content"],
            context={
                "user_id": "system",
                "tenant_id": company_id,
                "memory_type": "fact_declaration"
            }
        )
    return len(knowledge_items)
```

## 7. Troubleshooting

### 7.1 Common Issues

#### 7.1.1 Inaccurate Memory Classification

**Problem**: Memory classification results do not match expectations.

**Solutions**:
- Check if rule configuration is correct
- Consider enabling LLM functionality to improve classification accuracy
- Provide feedback to help the system learn and improve

#### 7.1.2 Performance Issues

**Problem**: System response is slow or memory usage is too high.

**Solutions**:
- Adjust cache size and batch processing size
- Disable unnecessary features
- Regularly optimize the system and compress memories

#### 7.1.3 Knowledge Base Integration Issues

**Problem**: Unable to write memories back to the knowledge base or retrieve knowledge from the knowledge base.

**Solutions**:
- Ensure Obsidian is installed and the vault path is set correctly
- Check file permissions
- Ensure the Obsidian vault directory exists

#### 7.1.4 Agent Framework Issues

**Problem**: Unable to register or use agents.

**Solutions**:
- Check if the agent adapter is correctly installed
- Ensure API keys are valid (if needed)
- Check network connection

### 7.2 Logs and Debugging

- **View logs**: The system generates detailed logs to help you understand system status and error information
- **Enable debug mode**: Set `debug: true` in the configuration file to get more detailed debugging information
- **Use performance monitoring**: Regularly check performance metrics to identify potential issues

### 7.3 Contact Support

If you encounter issues that cannot be resolved, please create an issue in the GitHub repository with detailed error information and reproduction steps, and we will help you resolve the issue as soon as possible.

## 8. Summary

Memory Classification Engine is a powerful intelligent memory management system. By properly using its various features, you can:

- Automatically classify and store user memories
- Intelligently retrieve relevant memories
- Integrate with various agent frameworks to extend system capabilities
- Integrate with knowledge base tools like Obsidian to实现 bidirectional knowledge flow
- Protect user privacy and ensure data security
- Optimize system performance and improve response speed

We hope this guide helps you fully utilize the capabilities of the Memory Classification Engine to add intelligent memory management functionality to your applications or services.