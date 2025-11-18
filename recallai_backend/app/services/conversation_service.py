from sqlalchemy.orm import Session
from app.domain.repositories.conversation_repository import ConversationRepository

class ConversationService:
    def __init__(self, db: Session):
        self.repo = ConversationRepository(db)

    def list_for_user(self, user_id: int):
        conversations = self.repo.get_for_user(user_id)

        result = []
        for conv in conversations:
            result.append({
                "id": conv.id,
                "title": conv.title,
                "messages": [
                    {"role": m.role, "content": m.content}
                    for m in conv.messages
                ],
            })
        return result
