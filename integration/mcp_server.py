"""Servidor MCP (Model Context Protocol) para ferramentas externas."""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone
import json

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class MCPTool(BaseModel):
    """Ferramenta MCP."""
    from pydantic import BaseModel
    
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]

from pydantic import BaseModel

class MCPTool(BaseModel):
    """Ferramenta MCP."""
    name: str
    description: str
    parameters: Dict[str, Any]
    
    class Config:
        arbitrary_types_allowed = True

class MCPServer:
    """Servidor MCP que expõe ferramentas para agentes."""
    
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.tools: Dict[str, MCPTool] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        self.tool_calls: List[Dict[str, Any]] = []
    
    def register_tool(self, name: str, description: str, 
                     parameters: Dict[str, Any], handler: Callable):
        """Regista uma ferramenta MCP."""
        tool = MCPTool(
            name=name,
            description=description,
            parameters=parameters
        )
        self.tools[name] = tool
        self.tool_handlers[name] = handler
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Lista todas as ferramentas disponíveis."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any],
                 entity_id: str) -> Dict[str, Any]:
        """
        Chama uma ferramenta MCP.
        
        Args:
            tool_name: Nome da ferramenta
            arguments: Argumentos para a ferramenta
            entity_id: ID da entidade que faz a chamada
        
        Returns:
            Resultado da ferramenta
        """
        if tool_name not in self.tools:
            raise ValueError(f"Ferramenta {tool_name} não encontrada")
        
        handler = self.tool_handlers[tool_name]
        
        try:
            result = handler(arguments)
            
            # Registar chamada
            self.tool_calls.append({
                "tool_name": tool_name,
                "arguments": arguments,
                "entity_id": entity_id,
                "result": result,
                "timestamp": utc_now()
            })
            
            return result
        except Exception as e:
            # Registar erro
            self.tool_calls.append({
                "tool_name": tool_name,
                "arguments": arguments,
                "entity_id": entity_id,
                "error": str(e),
                "timestamp": utc_now()
            })
            raise
    
    def get_tool_calls(self, entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna histórico de chamadas de ferramentas."""
        if entity_id:
            return [call for call in self.tool_calls if call["entity_id"] == entity_id]
        return self.tool_calls
