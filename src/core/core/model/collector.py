from marshmallow import fields, post_load
from sqlalchemy import or_, func
import uuid

from managers.db_manager import db
from model.parameter import NewParameterSchema
from shared.schema.collector import CollectorSchema


class NewCollectorSchema(CollectorSchema):
    parameters = fields.List(fields.Nested(NewParameterSchema))

    @post_load
    def make_collector(self, data, **kwargs):
        return Collector(**data)


class Collector(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String())
    type = db.Column(db.String(), nullable=False)
    parameters = db.relationship("Parameter", secondary="collector_parameter", cascade="all")
    sources = db.relationship("OSINTSource", backref="collector")

    def __init__(self, name, description, type, parameters):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.type = type
        self.parameters = parameters

    @classmethod
    def create_all(cls, collectors_data):
        new_collector_schema = NewCollectorSchema(many=True)
        return new_collector_schema.load(collectors_data)

    @classmethod
    def add(cls, collectors_data):
        if cls.find_by_type(collectors_data["type"]):
            return None
        schema = NewCollectorSchema()
        collector = schema.load(collectors_data)
        db.session.add(collector)
        db.session.commit()

    @classmethod
    def get_first(cls):
        return cls.query.first()

    @classmethod
    def get(cls, search):
        query = cls.query

        if search is not None:
            search_string = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Collector.name).like(search_string),
                    func.lower(Collector.description).like(search_string),
                )
            )

        return query.order_by(db.asc(Collector.name)).all(), query.count()

    @classmethod
    def find_by_type(cls, type):
        return cls.query.filter_by(type=type).first()

    @classmethod
    def get_all_json(cls, search):
        collectors, count = cls.get(search)
        node_schema = CollectorSchema(many=True)
        items = node_schema.dump(collectors)

        return {"total_count": count, "items": items}


class CollectorParameter(db.Model):
    collector_id = db.Column(db.String, db.ForeignKey("collector.id", ondelete="CASCADE"), primary_key=True)
    parameter_id = db.Column(db.Integer, db.ForeignKey("parameter.id", ondelete="CASCADE"), primary_key=True)
