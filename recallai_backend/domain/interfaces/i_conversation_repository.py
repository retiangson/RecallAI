from typing import Protocol, List, Optional
from recallai_backend.domain.models.conversation import Conversation
from recallai_backend.domain.models.message import Message


class IConversationRepository(Protocol):
    """
    Abstraction for conversations and message storage.
    """

    # CREATE
    def create_conversation(
        self,
        user_id: int,
        title: str | None = None,
    ) -> Conversation:
        ...

    def add_message(
        self,
        conv_id: int,
        role: str,
        content: str,
    ) -> Message:
        ...

    # READ
    def get_for_user(self, user_id: int) -> List[Conversation]:
        ...

    def get_by_id(self, conv_id: int) -> Optional[Conversation]:
        ...

    def get_messages(self, conv_id: int) -> List[Message]:
        ...

    def get_messages_paginated(
        self,
        conv_id: int,
        limit: int,
        before_id: int | None,
    ) -> List[Message]:
        ...

    # UPDATE
    def rename(self, conv_id: int, title: str) -> Optional[Conversation]:
        ...

    # DELETE
    def delete(self, conv_id: int) -> bool:
        ...

    def delete_message(self, message_id: int) -> bool:
        ...
