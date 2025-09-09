import os
import asyncio
import uuid
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

from src.core.chatbot import ChatBot


# Load environment variables
load_dotenv()

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active chatbot instances per session
active_bots = {}


def create_chatbot():
    """Create a new chatbot instance with configuration."""
    config = {
        'llm': {
            'provider': os.getenv('LLM_PROVIDER', 'openai'),
            'model': os.getenv('LLM_MODEL', 'gpt-4o'),
            'max_tokens': int(os.getenv('MAX_TOKENS', '4000')),
            'temperature': float(os.getenv('TEMPERATURE', '0.7')),
        },
        'memory': {
            'db_path': os.getenv('MEMORY_DB_PATH', 'data/memory.db'),
            'vector_db_path': os.getenv('VECTOR_DB_PATH', 'data/chroma_db')
        },
        'tools': {
            'enabled_tools': os.getenv('ENABLED_TOOLS', 'web_search,calculator,file_operations').split(',')
        },
        'reasoning': os.getenv('REASONING_ENABLED', 'true').lower() == 'true'
    }
    return ChatBot(config)


@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('chat.html')


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """REST API endpoint for chat messages."""
    try:
        data = request.json
        message = data.get('message')
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create chatbot for session
        if session_id not in active_bots:
            active_bots[session_id] = create_chatbot()
        
        bot = active_bots[session_id]
        
        # Process message
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            bot.process_message(message, context={'session_id': session_id})
        )
        loop.close()
        
        return jsonify({
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    session_id = str(uuid.uuid4())
    active_bots[session_id] = create_chatbot()
    emit('connected', {'session_id': session_id})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    pass


@socketio.on('message')
def handle_message(data):
    """Handle incoming WebSocket messages."""
    try:
        message = data.get('message')
        session_id = data.get('session_id', 'default')
        
        if session_id not in active_bots:
            active_bots[session_id] = create_chatbot()
        
        bot = active_bots[session_id]
        
        # Process message asynchronously
        async def process_and_emit():
            response = await bot.process_message(
                message, 
                context={'session_id': session_id}
            )
            socketio.emit('response', {
                'response': response,
                'session_id': session_id
            })
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_and_emit())
        loop.close()
        
    except Exception as e:
        emit('error', {'error': str(e)})


@socketio.on('reset_conversation')
def handle_reset(data):
    """Reset conversation for a session."""
    session_id = data.get('session_id', 'default')
    if session_id in active_bots:
        active_bots[session_id].reset_conversation()
    emit('conversation_reset', {'session_id': session_id})


@app.route('/api/tools')
def api_tools():
    """Get available tools."""
    bot = create_chatbot()
    tools = bot.tool_manager.get_available_tools()
    return jsonify({'tools': tools})


if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Run the application
    socketio.run(
        app, 
        host=os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'false').lower() == 'true'
    )
