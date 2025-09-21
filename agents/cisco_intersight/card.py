from a2a.types import AgentCard, AgentSkill, AgentCapabilities

AGENT_SKILL = AgentSkill(
    id = "cisco_intersight_skill",
    name = "Cisco Intersight Greeting Skill",
    description = "A skill that provides a greeting message for the Cisco Intersight agent.",
    tags=["greeting", "cisco_intersight"],
    examples= ["Hello Cisco Intersight!", "What can you do for me?"],
)

AGENT_CARD = AgentCard(
    name="Cisco Intersight Agent",
    description="An agent that provides information about the Cisco Intersight.",
    url = "http://localhost:8002",
    skills=[AGENT_SKILL],
    capabilities=AgentCapabilities(streaming=True ),
    default_input_modes=["text"],
    default_output_modes=["text"],
    version="1.0.0",
)