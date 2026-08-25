
"""First-class private Elara X NRLMSIS 2.0 compatibility implementation."""

from .api import (
    ModelNotInitializedError,
    ResourceError,
    ResourceNotConfiguredError,
    ResourceNotFoundError,
    ResourceIdentityError,
    ResourceInitializationError,
    VerifiedParameterResource,
    initialize,
    is_initialized,
    calculate,
    gtd8d,
)

__all__ = [
    "ModelNotInitializedError",
    "ResourceError",
    "ResourceNotConfiguredError",
    "ResourceNotFoundError",
    "ResourceIdentityError",
    "ResourceInitializationError",
    "VerifiedParameterResource",
    "initialize",
    "is_initialized",
    "calculate",
    "gtd8d",
]

MODEL_ID = "nrlmsis20"
DISPLAY_NAME = "NRLMSIS 2.0"
IMPLEMENTATION_KIND = (
    "FIRST_CLASS_NATIVE_COMPATIBILITY_FROM_ACCEPTED_NRLMSIS21_TRANSLATION"
)
PUBLIC_DENSITY_OUTPUTS = 9
NO_OUTPUT_EXPOSED = False

SCIENTIFIC_IDENTITY_SHA256 = "c720f852e4966c1fd3519618c46858d6494a0a40f702ff0eb8271abcb567d14e"
