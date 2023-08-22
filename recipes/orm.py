"""Database schema and considerations.

## Tables

### `recipe`

| `id` | `name |
|------|-------|
| e3t6 | soup  |
| pvdl | chips |

**Considerations**

A recipe represents the aggregate in this context but no real problem with
multiple edits at the same time so no "lock" on the table.

Elsewhere there might be a version column and a postgres database engine
initialised with a repeatable read option.

No problem with multiple edits because:

* Seems unlikely - in practice a recipe will be curated by a low number of users.
* Not business-critical - no-one, say, loses money if this happens.


### `requirement`

| `recipe_id` | `ingredient` | `measurement` | `quantity` |
|-------------|--------------|---------------|-----------:|
| pvdl        | potato       | units         |          2 |
| e3t6        | tomato       | grams         |        500 |

**Considerations**

There will be a lot of "1 pinch of salt" rows that may point to a `requirement`
table such as:

| `requirement_id` | `ingredient` | `measurement` | `quantity` |
|------------------|--------------|---------------|-----------:|
| h92e             | potato       | units         |          2 |
| dng3             | tomato       | grams         |        500 |

Combined with an association table between recipe and requirement.

`recipe_requirement`

| `recipe_id` | `requirement_id` |
|-------------|------------------|
| pvdl        | h92e             |
| e3t6        | dng3             |

Where multiple recipes can point to the same requirement.

But constrast with, say, "500 grams of flour".

There may be many many different requirements in the end.
Especially considering the different measurements used around the world.
Which would require converting all the measurements to some cardinal measurement.

So save a join and take the hit on some duplicated data.

"""

from __future__ import annotations

from sqlalchemy import Float, Column, String, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship

from recipes import domain


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Recipe(Base):
    __tablename__ = "recipe"

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    # version = Column(Integer, nullable=False, server_default="0")

    requirements = relationship("Requirement", back_populates="recipe")

    @classmethod
    def from_domain(cls, recipe: domain.RecipeInDB) -> Recipe:
        return cls(
            **(
                recipe.model_dump()
                | {
                    "requirements": [
                        Requirement(**requirement.model_dump())
                        for requirement in recipe.requirements
                    ]
                }
            )
        )


class Requirement(Base):
    __tablename__ = "requirement"

    recipe_id = Column(String(255), ForeignKey("recipe.id"), primary_key=True)
    ingredient = Column(String(255), primary_key=True)
    measurement = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=False)

    recipe = relationship("Recipe", back_populates="requirements")
