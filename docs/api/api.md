# Memory Classification Engine API Documentation

## Overview

The Memory Classification Engine provides a comprehensive API for managing and classifying memories. This document describes the available endpoints, request/response formats, and usage examples.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:8000/api/v1
```

## Authentication

API requests require authentication using API keys. Include the API key in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### 1. Process Message

**POST /process**

Process a message and classify it into memories.

**Request Body:**

```json
{
  "message": "I need to buy groceries tomorrow at 5 PM",
  "context": {
    "user_id": "user123",
    "tenant_id": "default",
    "scenario": "personal"
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "I need to buy groceries tomorrow at 5 PM",
  "matches": [
    {
      "memory_type": "fact_declaration",
      "tier": 3,
      "content": "I need to buy groceries tomorrow at 5 PM",
      "confidence": 0.5,
      "source": "default:general",
      "description": "General fact declaration",
      "language": "en",
      "id": "mem_1234567890",
      "tenant_id": "default",
      "language_confidence": 0.97,
      "type": "fact_declaration",
      "entities": [
        {
          "text": "PM",
          "type": "organization",
          "confidence": 0.5
        }
      ],
      "sentiment": {
        "sentiment": "neutral",
        "confidence": 0.5,
        "positive_indicators": 0,
        "negative_indicators": 0
      },
      "created_by": "default",
      "sensitivity_level": "low",
      "visibility": "private",
      "created_at": "2026-04-08T10:21:57Z",
      "updated_at": "2026-04-08T10:21:57Z",
      "last_accessed": 1775643717.21584,
      "access_count": 1,
      "status": "active",
      "is_encrypted": false,
      "encryption_key_id": null,
      "privacy_level": 0,
      "weight": 0.7
    }
  ],
  "plugin_results": {
    "sentiment_analyzer": {
      "sentiment": "neutral",
      "confidence": 0.5,
      "positive_indicators": 0,
      "negative_indicators": 0
    },
    "entity_extractor": {
      "entities": [
        {
          "text": "PM",
          "type": "organization",
          "confidence": 0.5
        }
      ],
      "entity_count": 1
    }
  },
  "working_memory_size": 1,
  "processing_time": 0.015302181243896484,
  "tenant_id": "default",
  "language": "en",
  "language_confidence": 0.97
}
```

### 2. Retrieve Memories

**GET /memories**

Retrieve memories based on query parameters.

**Query Parameters:**

- `query`: Search query string
- `limit`: Maximum number of results (default: 5)
- `tenant_id`: Filter by tenant ID
- `memory_type`: Filter by memory type
- `tier`: Filter by storage tier

**Response:**

```json
{
  "success": true,
  "memories": [
    {
      "id": "mem_1234567890",
      "content": "I need to buy groceries tomorrow at 5 PM",
      "memory_type": "fact_declaration",
      "tier": 3,
      "confidence": 0.5,
      "created_at": "2026-04-08T10:21:57Z",
      "updated_at": "2026-04-08T10:21:57Z"
    }
  ],
  "total": 1
}
```

### 3. Get Memory

**GET /memories/{memory_id}**

Get a specific memory by ID.

**Response:**

```json
{
  "success": true,
  "memory": {
    "id": "mem_1234567890",
    "content": "I need to buy groceries tomorrow at 5 PM",
    "memory_type": "fact_declaration",
    "tier": 3,
    "confidence": 0.5,
    "source": "default:general",
    "description": "General fact declaration",
    "language": "en",
    "tenant_id": "default",
    "language_confidence": 0.97,
    "type": "fact_declaration",
    "entities": [
      {
        "text": "PM",
        "type": "organization",
        "confidence": 0.5
      }
    ],
    "sentiment": {
      "sentiment": "neutral",
      "confidence": 0.5,
      "positive_indicators": 0,
      "negative_indicators": 0
    },
    "created_by": "default",
    "sensitivity_level": "low",
    "visibility": "private",
    "created_at": "2026-04-08T10:21:57Z",
    "updated_at": "2026-04-08T10:21:57Z",
    "last_accessed": 1775643717.21584,
    "access_count": 1,
    "status": "active",
    "is_encrypted": false,
    "encryption_key_id": null,
    "privacy_level": 0,
    "weight": 0.7
  }
}
```

### 4. Update Memory

**PUT /memories/{memory_id}**

Update a memory.

**Request Body:**

```json
{
  "content": "I need to buy groceries tomorrow at 6 PM",
  "tags": ["shopping", "personal"]
}
```

**Response:**

```json
{
  "success": true,
  "memory": {
    "id": "mem_1234567890",
    "content": "I need to buy groceries tomorrow at 6 PM",
    "updated_at": "2026-04-08T10:30:00Z"
  }
}
```

### 5. Delete Memory

**DELETE /memories/{memory_id}**

Delete a memory.

**Response:**

```json
{
  "success": true,
  "message": "Memory deleted"
}
```

### 6. Export Memories

**GET /export**

Export memories in various formats.

**Query Parameters:**

- `format`: Export format (json, csv, jsonl)
- `tenant_id`: Filter by tenant ID
- `memory_types`: Comma-separated list of memory types

**Response:**

The response will be a file download in the requested format.

### 7. Get Stats

**GET /stats**

Get system statistics.

**Response:**

```json
{
  "success": true,
  "stats": {
    "working_memory_size": 10,
    "storage": {
      "tier2": {
        "total_memories": 100,
        "memory_types": {
          "user_preference": 40,
          "habit": 60
        }
      },
      "tier3": {
        "total_memories": 200,
        "memory_types": {
          "fact_declaration": 150,
          "event": 50
        }
      },
      "tier4": {
        "total_memories": 50,
        "memory_types": {
          "relationship": 30,
          "value": 20
        }
      }
    },
    "total_memories": 350
  }
}
```

### 8. Manage Memory

**POST /memories/manage**

Manage memory operations (view, edit, delete).

**Request Body:**

```json
{
  "action": "edit",
  "memory_id": "mem_1234567890",
  "data": {
    "content": "Updated memory content"
  },
  "user_id": "user123"
}
```

**Response:**

```json
{
  "success": true,
  "memory": {
    "id": "mem_1234567890",
    "content": "Updated memory content",
    "updated_at": "2026-04-08T10:30:00Z"
  }
}
```

### 9. Process with Agent

**POST /process/agent**

Process a message with a specific agent.

**Request Body:**

```json
{
  "agent_name": "claude_code",
  "message": "Write a Python function to calculate factorial",
  "context": {
    "user_id": "user123",
    "tenant_id": "default"
  }
}
```

**Response:**

```json
{
  "success": true,
  "agent_name": "claude_code",
  "response": "Here's a Python function to calculate factorial:
\n```python\ndef factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)\n```",
  "processing_time": 0.5
}
```

### 10. Tenant Management

**POST /tenants**

Create a new tenant.

**Request Body:**

```json
{
  "tenant_id": "company_a",
  "name": "Company A",
  "tenant_type": "enterprise",
  "user_id": "admin123"
}
```

**Response:**

```json
{
  "success": true,
  "tenant_id": "company_a",
  "message": "Tenant created successfully"
}
```

## Error Responses

All API endpoints return standardized error responses:

```json
{
  "success": false,
  "error": "Error message",
  "code": 400
}
```

### Common Error Codes

- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Invalid or missing API key
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server-side error

## SDK Usage

### Python SDK

```python
from memory_classification_engine.sdk import MemoryClassificationSDK

# Initialize SDK
sdk = MemoryClassificationSDK(api_key="YOUR_API_KEY", base_url="http://localhost:8000/api/v1")

# Process a message
result = sdk.process_message("I need to buy groceries tomorrow at 5 PM")
print(result)

# Retrieve memories
memories = sdk.retrieve_memories(query="groceries")
print(memories)

# Get a specific memory
memory = sdk.get_memory("mem_1234567890")
print(memory)

# Update a memory
updated_memory = sdk.update_memory("mem_1234567890", {"content": "I need to buy groceries tomorrow at 6 PM"})
print(updated_memory)

# Delete a memory
deleted = sdk.delete_memory("mem_1234567890")
print(deleted)

# Export memories
export_data = sdk.export_memories(format="json")
print(export_data)

# Get stats
stats = sdk.get_stats()
print(stats)

# Process with agent
agent_result = sdk.process_with_agent("claude_code", "Write a Python function")
print(agent_result)
```

## Rate Limits

API requests are subject to rate limits:

- Free tier: 100 requests per minute
- Standard tier: 1000 requests per minute
- Enterprise tier: 10,000 requests per minute

## Versioning

The API uses semantic versioning. The current version is v1. Subsequent versions will be available at `/api/v2`, `/api/v3`, etc.

## Support

For API support, contact support@memory-classification-engine.com or visit our documentation at https://docs.memory-classification-engine.com.