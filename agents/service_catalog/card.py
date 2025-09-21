from a2a.types import AgentCard, AgentSkill, AgentCapabilities

AGENT_SKILL = AgentSkill(
    id = "service_catalog_skill",
    name = "Service Catalog Greeting Skill",
    description = "A skill that provides a greeting message for the Service Catalog agent.",
    tags=["greeting", "service_catalog"],
    examples= ["Hello service catalog!", "What services do you offer?"],
)

AGENT_CARD = AgentCard(
    name="Service Catalog Agent",
    description="An agent that provides information about the service catalog.",
    url = "http://localhost:8001",
    skills=[AGENT_SKILL],
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text"],
    default_output_modes=["text"],
    version="1.0.0",
)