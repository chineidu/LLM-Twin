from loguru import logger
from typing import Annotated, Any

from zenml import get_step_context, step
from zenml.config.retry_config import StepRetryConfig

from llm_engineering.application import utils
from llm_engineering.domain.documents import UserDocument


retry_config = StepRetryConfig(max_retries=3, delay=5, backoff=2)


@step(retry=retry_config)
def get_or_create_user(user_full_name: str) -> Annotated[UserDocument, "user"]:
    logger.info(f"Getting or creating user: {user_full_name}")

    first_name, last_name = utils.split_user_full_name(user_full_name)
    user = UserDocument.get_or_create(first_name=first_name, last_name=last_name)

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="user", metadata=_get_metadata(user_full_name, user)
    )

    return user


def _get_metadata(user_full_name: str, user: UserDocument) -> dict[str, dict[str, Any]]:
    return {
        "query": {"user_full_name": user_full_name},
        "retrieved": {
            "user_id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    }
