from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from zenml.client import Client
from zenml.exceptions import EntityExistsError


class Settings(BaseSettings):
    """Settings class for managing application configuration.

    This class handles all configuration settings including API keys, database connections,
    and model parameters. It supports loading from environment variables and .env files.

    Attributes
    ----------
    model_config : SettingsConfigDict
        Configuration for the settings model, specifying .env file usage
    OPENAI_MODEL_ID : str
        Identifier for the OpenAI model to use
    OPENAI_API_KEY : str | None
        API key for OpenAI services
    ... (other attributes follow same pattern)
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # ---> Required settings even when working locally. <---
    # OpenAI API Config
    OPENAI_MODEL_ID: str = "gpt-4o-mini"
    OPENAI_API_KEY: str | None = None

    # Huggingface API Config
    HUGGINGFACE_ACCESS_TOKEN: str | None = None

    # Comet ML (Experiment Tracking)
    COMET_API_KEY: str | None = None

    # ---> Required settings when deploying the code. <---
    # ---> Otherwise, default values values work fine. <---

    # MongoDB database
    DATABASE_HOST: str = "mongodb://llm_engineering:llm_engineering@localhost:27017"
    DATABASE_NAME: str = "twin"

    # Qdrant vector database
    USE_QDRANT_CLOUD: bool = False
    QDRANT_DATABASE_URL: str = "localhost"
    QDRANT_DATABASE_PORT: int = 6333
    QDRANT_CLOUD_URL: str = "str"
    QDRANT_APIKEY: str | None = None

    # AWS Authentication
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "eu-west-1"
    AWS_ARN_ROLE: str | None = None

    # --- Optional settings used to tweak the code. ---

    # AWS SageMaker
    HF_MODEL_ID: str = "mlabonne/TwinLlama-3.1-8B-DPO"
    GPU_INSTANCE_TYPE: str = "ml.g5.2xlarge"
    SM_NUM_GPUS: int = 1
    MAX_INPUT_LENGTH: int = 2_048
    MAX_TOTAL_TOKENS: int = 4_096
    MAX_BATCH_TOTAL_TOKENS: int = 4_096
    COPIES: int = 1  # Number of replicas
    GPUS: int = 1  # Number of GPUs
    CPUS: int = 2  # Number of CPU cores

    SAGEMAKER_ENDPOINT_CONFIG_INFERENCE: str = "twin"
    SAGEMAKER_ENDPOINT_INFERENCE: str = "twin"
    TEMPERATURE_INFERENCE: float = 0.01
    TOP_P_INFERENCE: float = 0.9
    MAX_NEW_TOKENS_INFERENCE: int = 150

    # RAG
    TEXT_EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    RERANKING_CROSS_ENCODER_MODEL_ID: str = "cross-encoder/ms-marco-MiniLM-L-4-v2"
    RAG_MODEL_DEVICE: str = "cpu"

    # LinkedIn Credentials
    LINKEDIN_USERNAME: str | None = None
    LINKEDIN_PASSWORD: str | None = None

    @property
    def OPENAI_MAX_TOKEN_WINDOW(self) -> int:
        """Calculate the maximum token window size for OpenAI API.

        Returns
        -------
        int
            The maximum number of tokens allowed for the current OpenAI model,
            with a 10% safety margin applied.
        """
        official_max_token_window: int = {
            "gpt-3.5-turbo": 16_385,
            "gpt-4-turbo": 128_000,
            "gpt-4o": 128_000,
            "gpt-4o-mini": 128_000,
        }.get(self.OPENAI_MODEL_ID, 128_000)
        max_token_window: int = int(official_max_token_window * 0.9)

        return max_token_window

    @classmethod
    def load_settings(cls) -> "Settings":
        """Load settings from ZenML secret store or environment variables.

        Returns
        -------
        Settings
            An instance of the Settings class with loaded configuration values.
        """
        try:
            logger.info("Loading settings from the ZenML secret store.")
            settings_secret = Client().get_secret("settings")
            settings = cls(**settings_secret.secret_values)
        except (RuntimeError, KeyError):
            logger.warning(
                "Failed to load settings from the ZenML secret store. "
                "Defaulting to loading the settings from the .env file."
            )
            settings = cls()

        return settings

    def export(self) -> None:
        """Export current settings to ZenML secret store.

        This method converts all settings to strings and stores them in the ZenML
        secret store for later retrieval.

        Returns
        -------
        None
        """
        env_vars: dict[str, str] = settings.model_dump()
        for key, value in env_vars.items():
            env_vars[key] = str(value)

        client: Client = Client()

        try:
            client.create_secret(name="settings", secret_values=env_vars)
        except EntityExistsError:
            logger.warning(
                "Secret 'scope' already exists. Delete it manually by running "
                "'zenml secret delete settings' before running this script."
            )


settings = Settings.load_settings()
