from typing import Annotated, Any
from llm_engineering.domain.exceptions import ImproperlyConfiguredException


def split_user_full_name(
    user: Any | None,
) -> tuple[Annotated[str, "first_name"], Annotated[str, "last_name"]]:
    """Split a full name into first name and last name components.

    Parameters
    ----------
    user : Any | None
        The full name of the user as a single string. Can be None.

    Returns
    -------
    tuple[str, str]
        A tuple containing (first_name, last_name).
        If the name has multiple parts, first_name will contain all parts except the last,
        and last_name will contain the last part.
        If the name has only one part, both first_name and last_name will be the same.

    Raises
    ------
    ImproperlyConfiguredException
        If the user name is None or empty after splitting.
    """
    if user is None:  # type: ignore
        raise ImproperlyConfiguredException("User full name is empty.")

    name_tokens: list[str] = user.split(" ")  # type: ignore
    if len(name_tokens) == 0:
        raise ImproperlyConfiguredException("User full name is empty.")
    elif len(name_tokens) == 1:
        first_name: str = name_tokens[0]
        last_name: str = name_tokens[0]
    else:
        first_name: str = " ".join(name_tokens[:-1])  # type: ignore
        last_name: str = name_tokens[-1]  # type: ignore

    return first_name, last_name
