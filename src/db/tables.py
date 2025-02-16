from piccolo.columns import UUID, Bytea, DoublePrecision, Varchar
from piccolo.table import Table


class Visitors(Table):
    id = UUID(primary_key=True)
    full_name = Varchar(default=None)
    frontal_pic = Bytea(default=None)
    left_pic = Bytea(null=True, default=None)
    right_pic = Bytea(null=True, default=None)


class UnknownVisitors(Table):
    id = UUID(primary_key=True)
    pic = Bytea(default=None)
    nearest_distance = DoublePrecision()
