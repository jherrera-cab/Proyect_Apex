from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator, field_validator


class ParseConfig(BaseModel):
    format: str = Field(..., min_length=1, description="Formato de strftime, ej: %d/%m/%Y")

class TargetConfig(BaseModel):
    name: str =Field(..., min_length=1)
    name_table: str = Field(..., min_length=1)
    dtype: Literal['str', 'int', 'float', 'date']

    @field_validator("name_table")
    @classmethod
    def normalize_table_name(cls, value: str)->str:
        return value.strip().lower()

class ColumnMapping(BaseModel):
    source: str = Field(..., min_length=1)
    target: TargetConfig
    parse: Optional[ParseConfig] = None

    @model_validator(mode="after")
    def chek_date_has_parse(self)->"ColumnMapping":
        if self.target.dtype == "date" and self.parse is None:
            raise ValueError(
                f"La columna '{self.source}' es de tipo 'date' pero no tiene bloque 'parse'"
            )
        return self

class SheetConfig(BaseModel):
    name: str= Field(..., min_length=1)
    role: Literal["master", "detail"]
    key_join: list[str] = Field(..., min_length=1)
    columns: list[ColumnMapping] = Field(..., min_length=1)

    @model_validator(mode="after")
    def check_unique_target(self) -> "SheetConfig":
        seen_target: set[tuple[str, str]] = set()
        duplicates: list[str] = []

        for col in self.columns:
            key = (col.target.name_table, col.target.name)
            if key in seen_target:
                duplicates.append(
                    f"tabla '{col.target.name_table}' -> columna '{col.target.name}'(origen: {col.source})"

                )

            if duplicates:
                raise ValueError(\
                    "Se encontraron destinos duplicados en la configuracion:\n - "
                    + "\n -".join(duplicates)
                    )
        return self

class PipelineConfig(BaseModel):
    excel_dir: Path
    allowed_tables: list[str] = Field(..., min_length=1)
    sheet_name: SheetConfig = Field(...)

    @field_validator("allowed_tables")
    @classmethod
    def normalize_allowed_tables(cls, tables: list[str]) -> list[str]:
        return [t.strip().lower() for t in tables if t.strip()]

    @model_validator(mode="after")
    def check_tables_are_allowed(self) -> "PipelineConfig":
        if self.sheet_name is None:
            return self

        valid_tables = set(self.allowed_tables)
        invalid_entries: list[str] = []

        for col in self.sheet_name.columns:
            if col.target.name_table not in valid_tables:
                invalid_entries.append(
                    f"columna '{col.source}' apunta a tabla '{col.target.name_table}' (no declarada en allowed_tables)"
                )

        if invalid_entries:
            raise ValueError(
                f"Tablas destino no permitidas (válidas: {sorted(valid_tables)}):\n  - "
                + "\n  - ".join(invalid_entries)
            )
        return self