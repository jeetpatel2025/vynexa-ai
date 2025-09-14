import asyncio
import aiohttp
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
        
    def get_supported_providers(self) -> List[str]:
        """Get list of supported LLM providers."""
        return ['openai', 'openrouter', 'anthropic', 'local', 'ollama']
    
    def _init_clients(self):
        """Initialize LLM provider clients."""
        try:
            if self.provider == 'openai':
                api_key = self.config.get('openai_api_key')
                if api_key:
                    self.openai_client = openai.AsyncOpenAI(api_key=api_key)
                else:
                    self.openai_client = openai.AsyncOpenAI()  # Use environment variable

            elif self.provider == 'openrouter':
                api_key = self.config.get('openrouter_api_key')
                if api_key:
                    self.openai_client = openai.AsyncOpenAI(
                        api_key=api_key,
                        base_url="https://openrouter.ai/api/v1"
                    )
                else:
                    self.openai_client = openai.AsyncOpenAI(
                        base_url="https://openrouter.ai/api/v1"
                    )  # Use environment variable

            elif self.provider == 'anthropic':
                api_key = self.config.get('anthropic_api_key')
                if api_key:
                    self.anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
                else:
                    self.anthropic_client = anthropic.AsyncAnthropic()  # Use environment variable
                    
            elif self.provider == 'local':
                # HuggingFace transformers
                self.local_pipeline = None  # Initialize on first use
                
            elif self.provider == 'ollama':
                # Ollama local server
                self.ollama_base_url = self.config.get('ollama_base_url', 'http://localhost:11434')
                
        except Exception as e:
            print(f"Warning: Failed to initialize {self.provider} client: {e}")
    
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

    
            Generated response text
        """
        try:
            if self.provider == 'openai' or self.provider == 'openrouter':
                return await self._openai_generate(messages, tools)
            elif self.provider == 'anthropic':
                return await self._anthropic_generate(messages, tools)
            elif self.provider == 'local':
                return await self._local_generate(messages)
            elif self.provider == 'ollama':
                return await self._ollama_generate(messages)
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
        """Generate response using local HuggingFace model."""
        
        # Initialize pipeline on first use
        if self.local_pipeline is None:
            print(f"Loading local model: {self.model}...")
            loop = asyncio.get_event_loop()
            self.local_pipeline = await loop.run_in_executor(
                None,
                lambda: pipeline('text-generation', model=self.model, device_map='auto')
            )
        
        # Combine messages into a single prompt
        prompt = ""
        for msg in messages:
            prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        prompt += "Assistant:"
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: self.local_pipeline(
                prompt, 
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=self.local_pipeline.tokenizer.eos_token_id
            )[0]['generated_text']
        )
        
        # Extract only the assistant's response
        return result.split("Assistant:")[-1].strip()
    
    async def _ollama_generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Ollama local server."""
        
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.ollama_base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["message"]["content"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error {response.status}: {error_text}")
            except aiohttp.ClientError as e:
                raise Exception(f"Failed to connect to Ollama server at {self.ollama_base_url}: {e}")
    
    def supports_multimodal(self) -> bool:
        """Check if the current provider supports multimodal input."""
        return (self.provider in ['openai', 'openrouter']) and 'vision' in self.model.lower()
    
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
