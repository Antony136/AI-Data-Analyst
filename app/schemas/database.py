from pydantic import BaseModel


class ColumnInfo(BaseModel):
    name: str
    data_type: str
    nullable: bool
    primary_key: bool = False


class ForeignKeyInfo(BaseModel):
    column: str
    referenced_table: str
    referenced_column: str


class TableInfo(BaseModel):
    name: str
    columns: list[ColumnInfo]
    foreign_keys: list[ForeignKeyInfo]