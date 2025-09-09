import asyncio
from typing import Dict, Any, Optional, List
from .conversation import Conversation
from ..ai.llm_client import LLMClient
from ..ai.memory_manager import MemoryManager
from ..ai.tool_manager import ToolManager


class ChatBot:
    """
    Main ChatBot class that orchestrates all AI functionality.
    Features GPT-5-like capabilities including reasoning, memory, and tool use.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conversation = Conversation()
        self.llm_client = LLMClient(config.get('llm', {}))
        self.memory_manager = MemoryManager(config.get('memory', {}))
        self.tool_manager = ToolManager(config.get('tools', {}))
        self.reasoning_enabled = config.get('reasoning', True)
        
    async def process_message(self, user_message: str, context: Optional[Dict] = None) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: The input from the user
            context: Additional context like user preferences, session info
            
        Returns:
            Generated response from the AI
        """
        # Add user message to conversation
        self.conversation.add('user', user_message)
        
        # Retrieve relevant memories
        relevant_memories = await self.memory_manager.retrieve_memories(user_message)
        
        # Determine if tools are needed
        tools_needed = await self.tool_manager.analyze_tool_need(user_message)
        
        # Generate response with all context
        response = await self._generate_response(
            user_message, 
            relevant_memories, 
            tools_needed,
            context
        )
        
        # Add response to conversation
        self.conversation.add('assistant', response)
        
        # Store interaction in memory
        await self.memory_manager.store_interaction(user_message, response)
        
        return response
    
    async def _generate_response(
        self, 
        user_message: str, 
        memories: List[Dict], 
        tools: List[str],
        context: Optional[Dict] = None
    ) -> str:
        """Generate response using LLM with all available context."""
        
        # Build system prompt with reasoning instructions
        system_prompt = self._build_system_prompt(memories, tools, context)
        
        # Prepare messages for LLM
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation.to_dict())
        
        # Generate response
        response = await self.llm_client.generate_response(messages, tools)
        
        return response
    
    def _build_system_prompt(self, memories: List[Dict], tools: List[str], context: Optional[Dict]) -> str:
        """Build comprehensive system prompt with all context."""
        prompt_parts = [
            "You are an advanced AI assistant with GPT-5-like capabilities.",
            "You have access to reasoning, memory, and tools.",
            "Think step-by-step and provide helpful, accurate responses."
        ]
        
        if memories:
            prompt_parts.append(f"Relevant context from past conversations: {memories}")
            
        if tools:
            prompt_parts.append(f"Available tools: {', '.join(tools)}")
            
        if context:
            prompt_parts.append(f"Additional context: {context}")
            
        return "\n\n".join(prompt_parts)
    
    def reset_conversation(self):
        """Reset the current conversation."""
        self.conversation = Conversation()
