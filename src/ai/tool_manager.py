import asyncio
import json
import re
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import requests
import os


class ToolManager:
    """
    Tool management system for GPT-5-like function calling and external integrations.
    Supports web search, code execution, file operations, and custom tools.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tools = {}
        self.enabled_tools = config.get('enabled_tools', ['web_search', 'calculator', 'file_operations'])
        
        # Register built-in tools
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register all built-in tools."""
        self.register_tool('web_search', self._web_search, 
                          "Search the web for current information")
        self.register_tool('calculator', self._calculator, 
                          "Perform mathematical calculations")
        self.register_tool('file_operations', self._file_operations, 
                          "Read, write, and manage files")
        self.register_tool('code_executor', self._code_executor, 
                          "Execute Python code in a safe environment")
        self.register_tool('weather', self._get_weather, 
                          "Get current weather information")
        self.register_tool('datetime', self._get_datetime, 
                          "Get current date and time information")
    
    def register_tool(self, name: str, func: Callable, description: str):
        """Register a new tool function."""
        self.tools[name] = {
            'function': func,
            'description': description,
            'enabled': name in self.enabled_tools
        }
    
    async def analyze_tool_need(self, user_message: str) -> List[str]:
        """
        Analyze if tools are needed based on user message.
        
        Args:
            user_message: User's input message
            
        Returns:
            List of tool names that might be useful
        """
        message_lower = user_message.lower()
        needed_tools = []
        
        # Pattern matching for different tool needs
        tool_patterns = {
            'web_search': [
                r'search', r'look up', r'find information', r'current', r'latest', 
                r'news', r'what is', r'who is', r'when did', r'recent'
            ],
            'calculator': [
                r'calculate', r'compute', r'math', r'sum', r'multiply', r'divide',
                r'percentage', r'equation', r'\+', r'-', r'\*', r'/'
            ],
            'file_operations': [
                r'read file', r'save', r'write file', r'create file', r'file content'
            ],
            'code_executor': [
                r'run code', r'execute', r'python', r'script', r'program'
            ],
            'weather': [
                r'weather', r'temperature', r'forecast', r'rain', r'sunny', r'climate'
            ]
        }
        
        for tool, patterns in tool_patterns.items():
            if tool in self.enabled_tools:
                for pattern in patterns:
                    if re.search(pattern, message_lower):
                        needed_tools.append(tool)
                        break
        
        return needed_tools
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a specific tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}
        
        if not self.tools[tool_name]['enabled']:
            return {"error": f"Tool '{tool_name}' is disabled"}
        
        try:
            tool_func = self.tools[tool_name]['function']
            result = await tool_func(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def _web_search(self, query: str, num_results: int = 5) -> str:
        """Perform web search (mock implementation - replace with real search API)."""
        # In a real implementation, integrate with Google Search API, Bing API, etc.
        return f"Web search results for '{query}':\n1. Mock result 1\n2. Mock result 2\n3. Mock result 3"
    
    async def _calculator(self, expression: str) -> str:
        """Safe calculator for mathematical expressions."""
        try:
            # Remove any non-mathematical characters for safety
            safe_expr = re.sub(r'[^0-9+\-*/.() ]', '', expression)
            result = eval(safe_expr)
            return f"Calculation: {expression} = {result}"
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    async def _file_operations(self, operation: str, filepath: str, content: str = "") -> str:
        """Handle file operations safely."""
        try:
            if operation == "read":
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                return f"File content:\n{content[:1000]}{'...' if len(content) > 1000 else ''}"
            
            elif operation == "write":
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"Successfully wrote to {filepath}"
            
            elif operation == "append":
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(content)
                return f"Successfully appended to {filepath}"
            
            else:
                return f"Unsupported file operation: {operation}"
                
        except Exception as e:
            return f"File operation error: {str(e)}"
    
    async def _code_executor(self, code: str, language: str = "python") -> str:
        """Execute code in a safe environment (mock implementation)."""
        if language.lower() != "python":
            return "Only Python code execution is currently supported."
        
        # In production, use a proper sandboxed environment
        # This is a simplified mock implementation
        try:
            # Basic safety checks
            unsafe_patterns = ['import os', 'import sys', 'exec', 'eval', '__import__']
            for pattern in unsafe_patterns:
                if pattern in code:
                    return f"Unsafe code detected: {pattern} not allowed"
            
            # Mock execution result
            return f"Code executed successfully:\n{code}\n\nOutput: [Mock execution result]"
            
        except Exception as e:
            return f"Code execution error: {str(e)}"
    
    async def _get_weather(self, location: str) -> str:
        """Get weather information (mock implementation)."""
        # In production, integrate with OpenWeatherMap, AccuWeather, etc.
        return f"Weather in {location}: 22°C, partly cloudy, 60% humidity"
    
    async def _get_datetime(self, timezone: str = "UTC") -> str:
        """Get current date and time information."""
        current_time = datetime.now()
        return f"Current date and time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} {timezone}"
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available and enabled tools."""
        available_tools = []
        for name, tool in self.tools.items():
            if tool['enabled']:
                available_tools.append({
                    'name': name,
                    'description': tool['description']
                })
        return available_tools
    
    def enable_tool(self, tool_name: str):
        """Enable a specific tool."""
        if tool_name in self.tools:
            self.tools[tool_name]['enabled'] = True
            if tool_name not in self.enabled_tools:
                self.enabled_tools.append(tool_name)
    
    def disable_tool(self, tool_name: str):
        """Disable a specific tool."""
        if tool_name in self.tools:
            self.tools[tool_name]['enabled'] = False
            if tool_name in self.enabled_tools:
                self.enabled_tools.remove(tool_name)
    
    async def process_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple tool calls from LLM response.
        
        Args:
            tool_calls: List of tool call specifications
            
        Returns:
            List of tool execution results
        """
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.get('name')
            arguments = tool_call.get('arguments', {})
            
            result = await self.execute_tool(tool_name, **arguments)
            results.append({
                'tool_name': tool_name,
                'result': result
            })
        
        return results
