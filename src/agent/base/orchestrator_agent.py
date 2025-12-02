"""Base orchestrator agent for combining multiple sub-agents"""

from datetime import datetime
import pandas as pd
from src.agent.base.async_agent import AsyncAgent
from src.types.analysis_report import AnalysisReport
from agents import Agent, Runner, ModelSettings
import asyncio
from src.config import REPORT_LANGUAGE
from src.utils.cloudflare import write_csv_to_cloud, read_csv_from_cloud
        

class OrchestratorAgent(AsyncAgent):
    """
    Base class for agents that orchestrate multiple sub-agents.
    
    Provides a unified pattern for:
    - Setting up sub-agents
    - Running them in parallel
    - Synthesizing results
    """
    
    def __init__(self, agent_name: str, hooks: dict = None):
        """
        Initialize orchestrator agent.
        
        Args:
            agent_name: Name of the agent
            hooks: Dictionary of hook functions {hook_name: [func1, func2, ...]}
                   Available hooks:
                   - 'on_results_collected': Called after sub-agents complete
        """
        self.synthesis_agent: Agent = None
        self.sub_agents: list[AsyncAgent] = []
        self.sub_agent_results: list[AnalysisReport] = []
        self.output_type = AnalysisReport
        self.hooks = hooks or {}
        super().__init__(agent_name)
    
    def _setup(self):
        """Set up sub-agents and synthesis agent. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement _setup")
    
    def add_sub_agent(self, agent: AsyncAgent):
        """
        Add a sub-agent (automatically uses agent_name for labeling).
        
        Args:
            agent: Agent to add (already has agent_name attribute)
        
        Returns:
            self (supports method chaining)
        """
        self.sub_agents.append(agent)
        return self
    
    def _create_synthesis_agent(self, instructions: str) -> Agent:
        """Create synthesis agent for combining results."""
        return Agent(
            name=f"{self.agent_name}_synthesis",
            model="gpt-4.1-mini",
            instructions=instructions,
            model_settings=ModelSettings(temperature=0.1),
            output_type=AnalysisReport
        )
    
    async def run(self, prompt: str = None) -> AnalysisReport:
        """
        Run all sub-agents in parallel and synthesize results.
        
        Args:
            prompt: Optional prompt for sub-agents
            
        Returns:
            Synthesized analysis result as RunResult
        """
        if not self.sub_agents or self.synthesis_agent is None:
            self._setup()
        
        # Run all sub-agents in parallel
        task_prompt = prompt if prompt is not None else ""
        self.sub_agent_results = await asyncio.gather(*[agent.run(task_prompt) for agent in self.sub_agents])
        
        # Execute hooks after results are collected
        self._execute_hooks('on_results_collected', self.sub_agent_results)
        
        # Create synthesis prompt
        synthesis_prompt = self._create_synthesis_prompt()
        result = await Runner.run(self.synthesis_agent, input=synthesis_prompt)
        return result.final_output_as(self.output_type)
        
    
    def _create_synthesis_prompt(self) -> str:
        """
        Create synthesis prompt from sub-agent results.
        Automatically uses agent_name for labeling.
        Override in subclasses for custom synthesis logic.
        """
        prompt_parts = ["Please synthesize the following analyses:", ""]
        
        # Use each agent's agent_name for labeling
        for agent, result in zip(self.sub_agents, self.sub_agent_results):
            # Extract content from AnalysisReport
            result_text = result.content if hasattr(result, 'content') else str(result)
            
            prompt_parts.append(f"--- {agent.agent_name} ---")
            prompt_parts.append(result_text)
            prompt_parts.append("")
        
        prompt_parts.extend([
            "Provide a comprehensive synthesis that:",
            "1. Identifies key patterns and trends",
            "2. Highlights correlations between analyses",
            "3. Offers strategic insights",
            f"4. Responds in {REPORT_LANGUAGE}"
        ])
        
        return "\n".join(prompt_parts)
    
    def _execute_hooks(self, hook_name: str, *args, **kwargs):
        """
        Execute registered hook functions.
        
        Args:
            hook_name: Name of the hook to execute
            *args, **kwargs: Arguments to pass to hook functions
        """
        if hook_name in self.hooks:
            hook_funcs = self.hooks[hook_name]
            # Support both single function and list of functions
            if not isinstance(hook_funcs, list):
                hook_funcs = [hook_funcs]
            
            for hook_func in hook_funcs:
                try:
                    hook_func(*args, **kwargs)
                except Exception as e:
                    print(f"⚠️ Hook '{hook_name}' failed: {e}")
