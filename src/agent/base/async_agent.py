from agents import Agent, Runner


class AsyncAgent:
    """
    Base class for async agent creation using Template Method pattern.
    
    Subclasses should override:
    - _setup(): Initialize attributes needed by _create_agent()
    - _create_agent(): Create and return the Agent instance
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self._setup()  # Hook: subclass initializes attributes here
        self.agent = self._create_agent()
    
    def _setup(self):
        """
        Hook method for subclass setup before agent creation.
        
        Override this to initialize instance attributes needed by _create_agent().
        """
        pass
    
    def _create_agent(self) -> Agent:
        """
        Create the LLM agent with instructions and tools.
        
        Subclasses must override this to create their specific agent.
        
        Returns:
            Agent instance configured for the specific use case
        """
        return Agent(
            name=self.agent_name,
            instructions="",
            model="gpt-4o-mini",
        )
    
    async def run(self, message: str):
        """
        Execute the agent with a user message.
        
        Args:
            message: User's analysis request
            
        Returns:
            Agent's response with analysis results
        """
        result = await Runner.run(self.agent, input=message)
        return result
