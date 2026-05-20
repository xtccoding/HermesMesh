"""
Supervision Module - Anti-hallucination defense and quality assurance
"""

from .supervisor_hermes import SupervisorHermes
from .cross_debate import CrossDebateEngine
from .alignment_tools import AlignmentTools
from .consensus_voting import ConsensusVoting


class SupervisorNetwork:
    """Supervision network for quality assurance."""

    def __init__(self, config_path=None):
        self.config_path = config_path
        self.supervisor = SupervisorHermes(config_path)
        self.debate_engine = CrossDebateEngine()
        self.alignment_tools = AlignmentTools()
        self.consensus = ConsensusVoting()

    async def start(self, instances=3):
        """Start supervisor network."""
        await self.supervisor.start(instances=instances)

    async def validate(self, worker_output, source_data):
        """Validate worker output against source data."""
        # Run alignment checks
        alignment_result = await self.alignment_tools.verify(
            worker_output, source_data
        )
        
        # Run cross-debate if disagreements found
        if alignment_result.has_disagreements:
            debate_result = await self.debate_engine.debate(
                worker_output, alignment_result.disagreements
            )
            return await self.consensus.vote(debate_result)
        
        return alignment_result

    async def shutdown(self):
        """Shutdown supervisor network."""
        await self.supervisor.shutdown()
