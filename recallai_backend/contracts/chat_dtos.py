"""
Chat-related DTOs (contracts).

Thin wrapper around `recallai_backend.dtos.chat_dtos`.
"""

from recallai_backend.dtos.chat_dtos import *  # noqa: F401,F403

# Optionally, explicitly control the public surface:
# from recallai_backend.dtos.chat_dtos import (
#     ChatRequestDTO,
#     ChatAnswerSource,
#     ChatAttachmentDTO,
#     ChatResponseDTO,
#     DeleteMessageDTO,
# )
#
# __all__ = [
#     "ChatRequestDTO",
#     "ChatAnswerSource",
#     "ChatAttachmentDTO",
#     "ChatResponseDTO",
#     "DeleteMessageDTO",
# ]
