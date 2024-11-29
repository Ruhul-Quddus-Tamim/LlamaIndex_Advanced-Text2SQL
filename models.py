from pydantic import BaseModel, Field


class TableInfo(BaseModel):
    """Information regarding a structured table."""

    table_name: str = Field(
        ..., description="Table name (must be unique, use underscores, and NO spaces)"
    )
    table_summary: str = Field(
        ..., description="Short, concise summary/caption of the table"
    )

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True