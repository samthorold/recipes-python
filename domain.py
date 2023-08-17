from __future__ import annotations
import uuid

from pydantic import BaseModel, ConfigDict, NonNegativeFloat


class Requirement(BaseModel):
    ingredient: str
    measurement: str
    quantity: NonNegativeFloat


class RequirementInDB(Requirement):
    recipe_id: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class Recipe(BaseModel):
    name: str
    requirements: list[Requirement]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Rustica",
                    "requirements": [
                        {
                            "ingredient": "Spinach",
                            "measurement": "grams",
                            "quantity": 500,
                        }
                    ],
                }
            ]
        },
    )


class RecipeInDB(Recipe):
    id: str
    requirements: list[RequirementInDB]

    model_config = ConfigDict(
        from_attributes=True,
    )

    @classmethod
    def from_recipe(cls, recipe: Recipe) -> RecipeInDB:
        recipe_id = str(uuid.uuid4().hex)
        return RecipeInDB.model_validate(
            recipe.model_dump()
            | {
                "id": recipe_id,
                "requirements": [
                    RequirementInDB.model_validate(
                        requirement.model_dump()
                        | {"id": str(uuid.uuid4().hex), "recipe_id": recipe_id}
                    )
                    for requirement in recipe.requirements
                ],
            }
        )
