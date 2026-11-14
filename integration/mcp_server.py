"""Servidor MCP: expoe ferramentas a agentes, com historico por tenant."""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class MCPTool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class MCPServer:
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.tools: Dict[str, MCPTool] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        self.tool_calls: List[Dict[str, Any]] = []

    def register_tool(self, name: str, description: str,
                      parameters: Dict[str, Any], handler: Callable):
        self.tools[name] = MCPTool(name=name, description=description, parameters=parameters)
        self.tool_handlers[name] = handler

    def list_tools(self) -> List[Dict[str, Any]]:
        return [t.model_dump() for t in self.tools.values()]

    def call_tool(self, tool_name: str, arguments: Dict[str, Any],
                  entity_id: str) -> Dict[str, Any]:
        if tool_name not in self.tools:
            raise ValueError(f"Ferramenta {tool_name} nao encontrada")
        record = {"tool_name": tool_name, "arguments": arguments,
                  "entity_id": entity_id, "timestamp": utc_now()}
        try:
            result = self.tool_handlers[tool_name](arguments)
            record["result"] = result
            self.tool_calls.append(record)
            return result
        except Exception as e:
            record["error"] = str(e)
            self.tool_calls.append(record)
            raise

    def get_tool_calls(self, entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if entity_id is not None:
            return [c for c in self.tool_calls if c["entity_id"] == entity_id]
        return list(self.tool_calls)
