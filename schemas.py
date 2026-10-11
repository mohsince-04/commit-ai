from typing import Optional
from pydantic import BaseModel, Field


class CommitMessageResponse(BaseModel):
    commit_type: str = Field(
        description="Semantic commit type: feat, fix, refactor, docs, style, test, chore, perf"
    )
    scope: Optional[str] = Field(
        description="Optional module or component scope (e.g., auth, db, ui, api)"
    )
    subject: str = Field(
        description="Short, imperative summary of the change in present tense (max 50 chars)"
    )
    body: Optional[str] = Field(
        description="Detailed explanation of what and why changes were made"
    )
    breaking_change: bool = Field(
        description="True if this introduces a breaking API or behavioral change"
    )
    full_commit_message: str = Field(
        description="The fully assembled, properly formatted conventional commit message string"
    )
