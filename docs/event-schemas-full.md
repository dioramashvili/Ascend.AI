# Event Schemas Documentation
Project: CareerSim Platform  
Team: AscendAI
Last Updated: 2025-11-30  

---

# 1. User Input Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "UserInputEvent",
  "description": "Event triggered when user submits a query or selects an option",
  "required": ["event_type", "timestamp", "request_id", "user_query", "session_id"],
  "properties": {
    "event_type": {"type": "string", "const": "user_input"},
    "timestamp": {"type": "string", "format": "date-time"},
    "request_id": {"type": "string"},
    "user_query": {"type": "string", "minLength": 1, "maxLength": 500},
    "user_id": {"type": "string"},
    "session_id": {"type": "string"},
    "metadata": {
      "type": "object",
      "properties": {
        "user_agent": {"type": "string"},
        "ip_address": {"type": "string"}
      }
    }
  }
}
```

---

# 2. LLM Request Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "LLMRequestEvent",
  "required": ["event_type", "timestamp", "request_id", "model", "messages"],
  "properties": {
    "event_type": {"type": "string", "const": "llm_request"},
    "timestamp": {"type": "string", "format": "date-time"},
    "request_id": {"type": "string"},
    "model": {"type": "string"},
    "messages": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["role", "content"],
        "properties": {
          "role": {"type": "string", "enum": ["system", "user", "assistant"]},
          "content": {"type": "string"}
        }
      }
    }
  }
}
```

---

# 3. LLM Response Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "LLMResponseEvent",
  "required": ["event_type", "timestamp", "request_id", "response_text", "tokens_used", "latency_ms"],
  "properties": {
    "event_type": {"type": "string", "const": "llm_response"},
    "timestamp": {"type": "string", "format": "date-time"},
    "request_id": {"type": "string"},
    "response_text": {"type": "string"},
    "tokens_used": {
      "type": "object",
      "properties": {
        "input_tokens": {"type": "integer"},
        "output_tokens": {"type": "integer"},
        "total_tokens": {"type": "integer"}
      }
    },
    "latency_ms": {"type": "integer"},
    "model": {"type": "string"}
  }
}
```

---

# 4. Tool Call Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "ToolCallEvent",
  "required": ["event_type", "timestamp", "request_id", "tool_name", "tool_arguments"],
  "properties": {
    "event_type": {"type": "string", "const": "tool_call"},
    "timestamp": {"type": "string", "format": "date-time"},
    "request_id": {"type": "string"},
    "tool_call_id": {"type": "string"},
    "tool_name": {"type": "string"},
    "tool_arguments": {"type": "object"}
  }
}
```

---

# 5. Tool Result Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "ToolResultEvent",
  "required": ["event_type", "timestamp", "request_id", "tool_call_id", "success"],
  "properties": {
    "event_type": {"type": "string", "const": "tool_result"},
    "timestamp": {"type": "string", "format": "date-time"},
    "request_id": {"type": "string"},
    "tool_call_id": {"type": "string"},
    "success": {"type": "boolean"},
    "result": {"type": ["object", "string", "number", "boolean", "array"]},
    "error": {"type": "string"},
    "latency_ms": {"type": "integer"}
  }
}
```

---

# 6. Database Write Event Schema (save_evaluation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "DatabaseWriteEvent",
  "required": ["event_type", "timestamp", "request_id", "table", "operation", "success"],
  "properties": {
    "event_type": {"type": "string", "const": "database_write"},
    "timestamp": {"type": "string", "format": "date-time"},
    "request_id": {"type": "string"},
    "table": {"type": "string", "const": "evaluations"},
    "operation": {"type": "string", "const": "insert"},
    "success": {"type": "boolean"},
    "data": {"type": "object"},
    "latency_ms": {"type": "integer"},
    "error": {"type": "string"}
  }
}
```

---

# 7. Error Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "ErrorEvent",
  "required": ["event_type", "timestamp", "error_type", "error_message"],
  "properties": {
    "event_type": {"type": "string", "const": "error"},
    "timestamp": {"type": "string", "format": "date-time"},
    "error_type": {"type": "string"},
    "error_message": {"type": "string"},
    "error_code": {"type": "string"},
    "request_id": {"type": "string"},
    "component": {"type": "string"},
    "retry_possible": {"type": "boolean"}
  }
}
```

---

