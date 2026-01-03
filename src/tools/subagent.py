"""
SubagentTool: Wrap an agent to be used as a tool by a parent agent.

This enables the "agent-as-tool" pattern where parent agents can delegate
tasks to specialized child agents, treating them like any other tool.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .base import BaseTool, ToolResult

if TYPE_CHECKING:
    from src.agent import BaseAgent


class SubagentTool(BaseTool):
    """
    Wraps a BaseAgent to be used as a callable tool by a parent agent.
    
    This is the core building block for hierarchical agent systems where
    a parent (orchestrator) agent can invoke specialized child agents
    to handle specific subtasks.
    
    Example:
        >>> researcher = BaseAgent(system_prompt="You are a research specialist...")
        >>> research_tool = SubagentTool(
        ...     agent=researcher,
        ...     name="research_agent",
        ...     description="Delegate research tasks to a specialized researcher"
        ... )
        >>> # Parent agent can now use research_tool like any other tool
        >>> orchestrator = BaseAgent(
        ...     system_prompt="You orchestrate tasks...",
        ...     tools=[research_tool]
        ... )
    """
    
    def __init__(
        self,
        agent: "BaseAgent",
        name: str,
        description: str,
        context_prefix: Optional[str] = None,
    ) -> None:
        """
        Initialize a SubagentTool.
        
        Args:
            agent: The child agent to wrap as a tool.
            name: Tool name (used by parent agent to invoke this subagent).
            description: Description of what this subagent does (helps parent
                        agent decide when to use it).
            context_prefix: Optional prefix to add before each task sent to
                           the subagent (e.g., background context).
        """
        self.agent = agent
        self.name = name
        self.description = description
        self.context_prefix = context_prefix
    
    def run(self, input_text: str) -> ToolResult:
        """
        Execute the subagent with the given input and return results.
        
        Args:
            input_text: The task/query to send to the subagent.
            
        Returns:
            ToolResult containing the subagent's response.
        """
        # Add context prefix if provided
        if self.context_prefix:
            full_prompt = f"{self.context_prefix}\n\nTask: {input_text}"
        else:
            full_prompt = input_text
        
        # Execute the subagent
        response = self.agent.complete(full_prompt)
        
        return ToolResult(
            content=response,
            data={
                "subagent_name": self.name,
                "input": input_text,
            }
        )
    
    def reset(self) -> None:
        """Reset the subagent's memory for a fresh start."""
        if hasattr(self.agent, 'memory') and self.agent.memory:
            self.agent.memory.clear()


class SubagentManager:
    """
    Manages a pool of subagents for dynamic spawning and lifecycle control.
    
    This class enables parent agents to:
    - Dynamically create specialized subagents at runtime
    - Track active subagents
    - Clean up subagents when done
    
    Example:
        >>> manager = SubagentManager(client=openai_client)
        >>> researcher = manager.spawn(
        ...     role="researcher",
        ...     task="Find information about AI agents",
        ...     model="gpt-4o-mini"
        ... )
        >>> result = researcher.complete("What are the latest trends?")
        >>> manager.terminate("researcher")  # Clean up
    """
    
    def __init__(
        self,
        client: Optional["OpenAI"] = None,  # type: ignore[name-defined]
        default_model: str = "gpt-4o-mini",
        default_temperature: float = 0.3,
    ) -> None:
        """
        Initialize the SubagentManager.
        
        Args:
            client: OpenAI client to share across subagents (saves resources).
            default_model: Default model for spawned subagents.
            default_temperature: Default temperature for spawned subagents.
        """
        self.client = client
        self.default_model = default_model
        self.default_temperature = default_temperature
        self._active_subagents: dict[str, "BaseAgent"] = {}
    
    def spawn(
        self,
        role: str,
        task: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        system_prompt_template: Optional[str] = None,
    ) -> "BaseAgent":
        """
        Dynamically spawn a new specialized subagent.
        
        Args:
            role: The role/specialization of the subagent (e.g., "researcher").
            task: The specific task this subagent will handle.
            model: Model to use (defaults to manager's default).
            temperature: Temperature setting (defaults to manager's default).
            system_prompt_template: Custom system prompt template. Use {role}
                                   and {task} as placeholders.
        
        Returns:
            A new BaseAgent configured for the specified role and task.
        """
        # Avoid circular import
        from src.agent import BaseAgent
        
        # Default system prompt template
        if system_prompt_template is None:
            system_prompt_template = """You are a specialized {role} agent.

Your specific task: {task}

Guidelines:
- Focus only on your assigned task
- Provide clear, actionable outputs
- Ask for clarification if the task is ambiguous
- Report any blockers or issues encountered"""
        
        system_prompt = system_prompt_template.format(role=role, task=task)
        
        subagent = BaseAgent(
            system_prompt=system_prompt,
            model=model or self.default_model,
            temperature=temperature or self.default_temperature,
            client=self.client,
            auto_load_env=self.client is None,  # Only load env if no client
        )
        
        self._active_subagents[role] = subagent
        return subagent
    
    def get(self, role: str) -> Optional["BaseAgent"]:
        """Get an active subagent by role name."""
        return self._active_subagents.get(role)
    
    def terminate(self, role: str) -> bool:
        """
        Terminate a subagent and clean up resources.
        
        Args:
            role: The role name of the subagent to terminate.
            
        Returns:
            True if subagent was found and terminated, False otherwise.
        """
        if role in self._active_subagents:
            subagent = self._active_subagents.pop(role)
            # Clear memory to free resources
            if hasattr(subagent, 'memory') and subagent.memory:
                subagent.memory.clear()
            return True
        return False
    
    def terminate_all(self) -> int:
        """
        Terminate all active subagents.
        
        Returns:
            Number of subagents terminated.
        """
        count = len(self._active_subagents)
        for role in list(self._active_subagents.keys()):
            self.terminate(role)
        return count
    
    def list_active(self) -> list[str]:
        """List all active subagent role names."""
        return list(self._active_subagents.keys())
    
    def as_tool(
        self,
        role: str,
        description: Optional[str] = None,
    ) -> Optional[SubagentTool]:
        """
        Wrap an active subagent as a SubagentTool.
        
        Args:
            role: The role name of the subagent.
            description: Tool description (auto-generated if not provided).
            
        Returns:
            SubagentTool wrapping the subagent, or None if not found.
        """
        subagent = self.get(role)
        if subagent is None:
            return None
        
        return SubagentTool(
            agent=subagent,
            name=f"{role}_agent",
            description=description or f"Delegate tasks to the {role} specialist",
        )
