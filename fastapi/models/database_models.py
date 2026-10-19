from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
  id: int | None = Field(default=None, unique=True, primary_key=True)
  username: str
  password: str


class Prediction(SQLModel, table=True):
  id: int | None = Field(default=None, primary_key=True)
  text: str
  intent: str
  owner_id: int = Field(foreign_key="user.id")