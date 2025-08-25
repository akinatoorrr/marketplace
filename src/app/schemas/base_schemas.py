from pydantic import (
    BaseModel,
    ConfigDict,
)


class BlogSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
