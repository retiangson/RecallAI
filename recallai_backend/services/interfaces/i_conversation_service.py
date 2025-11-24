from typing import Protocol, Any


class IConversationService(Protocol):
    def list_for_user(self, user_id: int) -> list[dict[str, Any]]:
        ...

    def create(self, user_id: int, title: str | None = None) -> dict[str, Any]:
        ...

    def add_message(self, conv_id: int, role: str, content: str) -> dict[str, Any]:
        ...

    def get_by_id(self, conv_id: int) -> dict[str, Any] | None:
        ...

    def rename(self, conv_id: int, title: str) -> dict[str, Any] | None:
        ...

    def delete(self, conv_id: int) -> bool:
        ...

    def delete_message(self, message_id: int) -> bool:
        ...

    def get_messages_paginated(
        self,
        conv_id: int,
        limit: int = 10,
        before_id: int | None = None,
    ) -> list[dict[str, Any]]:
        ...

    def add_message_to_note(
        self,
        user_id: int,
        content: str,
        title: str | None = None,
    ) -> dict[str, Any]:
        ...
