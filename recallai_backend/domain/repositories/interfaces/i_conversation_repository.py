from typing import Protocol, List, Optional
from recallai_backend.domain.models.conversation import Conversation
from recallai_backend.domain.models.message import Message


class IConversationRepository(Protocol):
    def get_for_user(self, user_id: int) -> List[Conversation]:
        ...

    def create_conversation(self, user_id: int, title: str | None) -> Conversation:
        ...

    def get_by_id(self, conv_id: int) -> Optional[Conversation]:
        ...

    def rename(self, conv_id: int, title: str) -> Optional[Conversation]:
        ...

    def delete(self, conv_id: int) -> bool:
        ...

    def add_message(self, conv_id: int, role: str, content: str) -> Message:
        ...

    def delete_message(self, message_id: int) -> bool:
        ...

    def get_messages_paginated(
        self,
        conv_id: int,
        limit: int,
        before_id: int | None = None,
    ) -> List[Message]:
        ...

    def get_messages(self, conv_id: int) -> List[Message]:
        ...
