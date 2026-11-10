from app.agent.simulated import SimulatedProvider


def make_provider(settings):
    if settings.ai_mode == "simulated":
        return SimulatedProvider()
    if settings.ai_mode == "groq":
        from app.agent.groq_provider import GroqProvider

        return GroqProvider(settings.groq_api_key, settings.groq_model)
    from app.agent.openai_provider import OpenAIProvider

    return OpenAIProvider(settings.openai_api_key, settings.openai_model)
