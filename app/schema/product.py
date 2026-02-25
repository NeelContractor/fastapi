from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from typing import Annotated


class Product(BaseModel):

    id: Annotated[int, Field(ge=1, le=1000)]

    name: Annotated[str, Field(min_length=2, max_length=50)]

    category: str

    price: Annotated[float, Field(ge=0)]

    rating: Annotated[float, Field(ge=0, le=5)]

    stock: int

    brand: str


    # FIELD VALIDATOR

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):

        if value.strip() == "":
            raise ValueError("Name cannot be empty")

        return value


    # MODEL VALIDATOR

    @model_validator(mode="after")
    @classmethod
    def validate_rules(cls, model):

        if model.rating < 1 and model.stock < 100:
            raise ValueError(
                "Low rating products need higher stock"
            )

        return model


    # COMPUTED FIELDS

    @computed_field
    def in_stock(self) -> bool:
        return self.stock > 0


    @computed_field
    def price_with_tax(self) -> float:
        return round(self.price * 1.18, 2)