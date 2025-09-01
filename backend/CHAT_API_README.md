# Grace Papers Backend - Chat API

This document describes the chat functionality added to the Grace Papers backend.

## Phase 1 Complete: Basic Chat Session Management ✅

### New Features Added:
- **Session Management**: In-memory chat sessions with unique IDs
- **Message Storage**: Store and retrieve chat messages with different types
- **Chat History**: Get complete conversation history for any session
- **Error Handling**: Proper error responses for invalid sessions

### New API Endpoints:

#### 1. Start Chat Session
```
POST /api/chat/start
```
**Request:**
```json
{
  "user_id": "optional-user-id"
}
```
**Response:**
```json
{
  "success": true,
  "session_id": "uuid-here",
  "message": "Chat session started successfully!"
}
```

#### 2. Send Message
```
POST /api/chat/message
```
**Request:**
```json
{
  "session_id": "uuid-here",
  "message": "I want to learn Python programming",
  "message_type": "user"
}
```
**Response:**
```json
{
  "success": true,
  "message": {
    "id": "message-uuid",
    "session_id": "session-uuid",
    "message_type": "user",
    "content": "I want to learn Python programming",
    "timestamp": "2025-01-01T12:00:00",
    "metadata": {}
  },
  "session_id": "session-uuid",
  "has_more_messages": false
}
```

#### 3. Get Chat History
```
GET /api/chat/history/{session_id}
```
**Response:**
```json
{
  "success": true,
  "session_id": "session-uuid",
  "messages": [
    {
      "id": "msg-1",
      "session_id": "session-uuid",
      "message_type": "agent_response",
      "content": "Hello! I'm your course research assistant...",
      "timestamp": "2025-01-01T12:00:00",
      "metadata": {"is_welcome": true}
    },
    {
      "id": "msg-2",
      "session_id": "session-uuid",
      "message_type": "user",
      "content": "I want to learn Python programming",
      "timestamp": "2025-01-01T12:01:00",
      "metadata": {}
    }
  ],
  "total_messages": 2
}
```

### Message Types:
- `user` - Message from the user
- `agent_thinking` - Agent is processing/thinking
- `agent_searching` - Agent is searching for courses
- `agent_response` - Agent's text response
- `agent_courses` - Agent returning course results
- `error` - Error messages

### Data Models:

#### ChatSession
```python
{
  "id": str,
  "user_id": Optional[str],
  "created_at": datetime,
  "last_activity": datetime,
  "messages": List[ChatMessage],
  "context": Dict[str, Any]
}
```

#### ChatMessage
```python
{
  "id": str,
  "session_id": str,
  "message_type": str,
  "content": str,
  "timestamp": datetime,
  "metadata": Optional[Dict[str, Any]]
}
```

## Testing

Run the test script to verify Phase 1 functionality:

```bash
cd backend
python test_chat_api.py
```

Make sure the server is running first:
```bash
python main_with_agent.py
```

## What's Next - Phase 2: Agent Integration 🚧

The next phase will integrate the research agent with the chat system:

1. **Agent Processing**: When users send messages, trigger the research agent
2. **Step-by-Step Messages**: Return agent's thinking process as separate messages
3. **Course Integration**: Seamlessly integrate course search results into chat
4. **Context Awareness**: Maintain conversation context for better responses

### Planned Flow:
```
User: "Find me Python courses"
Agent: "I'll help you find Python courses. Let me search our database..."
Agent: "Found 12 courses in our internal database. Checking external sources..."
Agent: "Perfect! Here are the best Python courses I found for you:"
Agent: [Returns formatted course results]
```

## Architecture Notes

- **Session Storage**: Currently in-memory (will upgrade to Redis for production)
- **Message Persistence**: Messages stored in session objects
- **Error Handling**: Comprehensive error responses with proper HTTP status codes
- **CORS**: Configured for frontend integration (localhost:3000, localhost:3001)

## Backward Compatibility

All existing endpoints remain unchanged:
- ✅ `/api/search-courses` - Original course search
- ✅ `/api/save-study-plan` - Save study plans  
- ✅ `/api/user-profile/{user_id}` - User profiles
- ✅ All debug and health endpoints

The chat system is additive and doesn't affect existing functionality.
