from p2.datashackle.core import Model, model_config


@model_config(tablename='person')
class Person(Model):
    """Our person model, which is maintained through admin UI. Point browser to http://localhost:8080/datashackle"""
