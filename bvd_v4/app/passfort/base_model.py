from schematics import Model


class BaseModel(Model):
    class Options:
        serialize_when_none = False
