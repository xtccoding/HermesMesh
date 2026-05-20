"""
Synthesis Module - Report generation and signal production
"""

from .synthesizer_hermes import SynthesizerHermes
from .report_builder import ReportBuilder
from .signal_generator import SignalGenerator


class ReportingEngine:
    """Main reporting engine."""

    def __init__(self, config_path=None):
        self.config_path = config_path
        self.synthesizer = SynthesizerHermes(config_path)
        self.report_builder = ReportBuilder()
        self.signal_generator = SignalGenerator()

    async def start(self):
        """Start the reporting engine."""
        await self.synthesizer.start()

    async def generate_report(self, validated_data):
        """Generate a quantitative report."""
        # Build report structure
        report = await self.report_builder.build(validated_data)
        
        # Generate trading signals
        signals = await self.signal_generator.generate(validated_data)
        
        # Synthesize final report
        final_report = await self.synthesizer.synthesize(report, signals)
        
        return final_report

    async def shutdown(self):
        """Shutdown the reporting engine."""
        await self.synthesizer.shutdown()
