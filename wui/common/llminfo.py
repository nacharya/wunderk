class LLMInfo:
    def __init__(self):
        """
        Initialize the LLMInfo class with a dictionary of available models
        for different LLM providers.
        """
        self.modellist = {
            "OpenAI": ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o", "gpt-4.1"],
            "Google": ["gemini-2.0-flash", "gemini-2.5-flash-preview-05-20"],
            "Anthropic": [
                "claude-opus-4-20250514",
                "claude-3-7-sonnet-latest",
                "claude-3-5-sonnet-latest",
                "claude-3-5-haiku-latest",
            ],
            "Ollama": ["mistral", "llama3.2:3b", "deepseek-r1:8b"],
        }
        self.default_model = {
            "OpenAI": "gpt-4.1-mini",
            "Google": "gemini-2.0-flash",
            "Anthropic": "claude-3-5-sonnet-latest",
            "Ollama": "mistral",
        }

    def get_model_list(self, provider):
        """
        Get the list of models for a specific LLM provider.

        :param provider: The name of the LLM provider (e.g., "OpenAI", "Google").
        :return: A list of model names for the specified provider.
        """
        return self.modellist.get(provider, [])

    def get_providers(self):
        """
        Get the list of available LLM providers.
        :return: A list of LLM provider names.
        """
        return list(self.modellist.keys())

    def get_default_model(self, provider):
        """
        Get the default model for a specific LLM provider.
        :param provider: The name of the LLM provider (e.g., "OpenAI", "Google").
        :return: The default model name for the specified provider.
        """
        return self.default_model.get(provider, None)
