import asyncio
from typing import Dict, Any, List, Optional
import openai
import anthropic
from transformers import pipeline


class LLMClient:
    """
    Unified client for multiple LLM providers (OpenAI, Anthropic, local models).
    Provides GPT-5-like reasoning and response generation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get('provider', 'openai')
        self.model = config.get('model', 'gpt-4')
        self.max_tokens = config.get('max_tokens', 4000)
        self.temperature = config.get('temperature', 0.7)
        
        # Initialize clients
        self._init_clients()
    
    def _init_clients(self):
        """Initialize LLM provider clients."""
        if self.provider == 'openai':
            self.openai_client = openai.AsyncOpenAI()
        elif self.provider == 'anthropic':
            self.anthropic_client = anthropic.AsyncAnthropic()
        elif self.provider == 'local':
            self.local_pipeline = pipeline('text-generation', model=self.model)
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[str]] = None
    ) -> str:
        """
        Generate response using the configured LLM provider.
        
        Args:
            messages: List of conversation messages
            tools: Available tools for function calling
            
        Returns:
            Generated response text
        """
        try:
            if self.provider == 'openai':
                return await self._openai_generate(messages, tools)
            elif self.provider == 'anthropic':
                return await self._anthropic_generate(messages, tools)
            elif self.provider == 'local':
                return await self._local_generate(messages)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def _openai_generate(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[str]] = None
    ) -> str:
        """Generate response using OpenAI API."""
        
        # Add reasoning capabilities to system prompt
        if messages and messages[0]['role'] == 'system':
            messages[0]['content'] += "\n\nUse step-by-step reasoning for complex queries. Think through the problem before responding."
        
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        return response.choices[0].message.content
    
    async def _anthropic_generate(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[str]] = None
    ) -> str:
        """Generate response using Anthropic API."""
        
        # Convert messages format for Anthropic
        system_prompt = ""
        conversation_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_prompt += msg['content'] + "\n"
            else:
                conversation_messages.append(msg)
        
        response = await self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=conversation_messages
        )
        
        return response.content[0].text
    
    async def _local_generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using local model."""
        
        # Combine messages into a single prompt
        prompt = ""
        for msg in messages:
            prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        prompt += "Assistant:"
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: self.local_pipeline(prompt, max_length=self.max_tokens)[0]['generated_text']
        )
        
        # Extract only the assistant's response
        return result.split("Assistant:")[-1].strip()
    
    def supports_multimodal(self) -> bool:
        """Check if the current provider supports multimodal input."""
        return self.provider == 'openai' and 'vision' in self.model.lower()
    
    async def analyze_image(self, image_path: str, prompt: str) -> str:
        """Analyze an image with a text prompt (if supported)."""
        if not self.supports_multimodal():
            return "Image analysis not supported with current model configuration."
        
        try:
            import base64
            with open(image_path, 'rb') as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ]
            
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
