from sqlalchemy.types import UserDefinedType

class VectorType(UserDefinedType):
    def __init__(self, dimensions):
        self.dimensions = dimensions

    def get_col_spec(self):
        return f"vector({self.dimensions})"

    # Optional: makes SQLAlchemy treat this as an immutable type
    def python_type(self):
        return list
