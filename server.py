import json
import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, EXCLUDE, ValidationError, validates, post_load
from werkzeug.exceptions import NotFound

load_dotenv()

app = Flask(__name__)

db_url = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url

db = SQLAlchemy(app)


class Nekretnina(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    link_nekretnine = db.Column(db.String(300), nullable=True, unique=True)
    stan = db.Column(db.Boolean, nullable=True)
    izdavanje = db.Column(db.Boolean, nullable=True)
    lokacija = db.Column(db.String(80), nullable=True)
    # lokacija_grad = db.Column(db.String(30), nullable=True)
    # lokacija_deo_grada = db.Column(db.String(50), nullable=True)
    kvadratura = db.Column(db.Float, nullable=True)
    godina_izgradnje = db.Column(db.Integer, nullable=True)
    povrsina_zemljista = db.Column(db.Float, nullable=True)
    sprat = db.Column(db.Integer, nullable=True)
    ukupno_spratova = db.Column(db.Integer, nullable=True)
    uknjizeno = db.Column(db.Boolean, nullable=True)
    tip_grejanja = db.Column(db.String(50), nullable=True)
    broj_soba = db.Column(db.Float, nullable=True)
    broj_kupatila = db.Column(db.Float, nullable=True)
    ima_parking = db.Column(db.Boolean, nullable=True)
    dodatna_opremljenost = db.Column(db.String(1000), nullable=True)

    def serialized_data(self):
        return {
            "id": self.id,
            "link_nekretnine": self.link_nekretnine,
            "stan": self.stan,
            "izdavanje": self.izdavanje,
            "lokacija": self.lokacija,
            # "lokacija_grad": self.lokacija_grad,
            # "lokacija_deo_grada": self.lokacija_deo_grada,
            "kvadratura": self.kvadratura,
            "godina_izgradnje": self.godina_izgradnje,
            "povrsina_zemljista": self.povrsina_zemljista,
            "sprat": self.sprat,
            "ukupno_spratova": self.ukupno_spratova,
            "uknjizeno": self.uknjizeno,
            "tip_grejanja": self.tip_grejanja,
            "broj_soba": self.broj_soba,
            "broj_kupatila": self.broj_kupatila,
            "ima_parking": self.ima_parking,
            "dodatna_opremljenost": json.loads(self.dodatna_opremljenost)
        }


class NekretninaSchema(Schema):
    id = fields.Integer(required=False, allow_none=True)
    link_nekretnine = fields.URL(required=False, allow_none=True)
    stan = fields.Boolean(required=False, allow_none=True)
    izdavanje = fields.Boolean(required=False, allow_none=True)
    lokacija = fields.String(required=False, allow_none=True)
    kvadratura = fields.Float(required=False, allow_none=True)
    godina_izgradnje = fields.Integer(required=False, allow_none=True)
    povrsina_zemljista = fields.Float(required=False, allow_none=True)
    sprat = fields.Float(required=False, allow_none=True)
    ukupno_spratova = fields.Float(required=False, allow_none=True)
    uknjizeno = fields.Boolean(required=False, allow_none=True)
    tip_grejanja = fields.String(required=False, allow_none=True)
    broj_soba = fields.Float(required=False, allow_none=True)
    broj_kupatila = fields.Float(required=False, allow_none=True)
    ima_parking = fields.Boolean(required=False, allow_none=True)
    dodatna_opremljenost = fields.String(required=False, allow_none=True)

    @validates("kvadratura")
    def validate_kvadratura(self, value):
        if value and value < 0:
            raise ValidationError("Kvadratura ne moze biti  negativna")

    @validates("broj_soba")
    def validate_broj_soba(self, value):
        if value and value < 0:
            raise ValidationError("Broj soba ne moze biti negativan")

    @validates("broj_kupatila")
    def validate_broj_kupatila(self, value):
        if value and value < 0:
            raise ValidationError("Broj kupatila ne moze biti negativan")

    @validates("godina_izgradnje")
    def validate_godina_izgradnje(self, value):
        if value and value < 0:
            raise ValidationError("Godina izgradnje ne moze biti negativna")

    @post_load
    def set_none_stan_kuca_sprat(self, data, **kwargs):
        try:
            if data["stan"]:
                data["povrsina_zemljista"] = None
            else:
                data["sprat"] = None
                data["ukupno_spratova"] = None
        except:
            pass
        return data


schema = NekretninaSchema()


@app.get("/api/nekretnina/<int:id>")
def pretraga_id(id):
    nekretnina = db.session.execute(db.select(Nekretnina).filter_by(id=id)).scalar()
    if nekretnina:
        return jsonify(nekretnina.serialized_data())
    raise NotFound(description='Nekretnina sa tim ID ne postoji')


@app.get("/api/nekretnina/")
def full_pretraga():
    nekretnine = db.session.query(Nekretnina)
    tip = request.args.get("tip")
    if tip:
        tip = tip == "stan"
        nekretnine = nekretnine.filter_by(stan=tip)

    min_kv = request.args.get("min_kv")
    max_kv = request.args.get("max_kv")

    # Ukoliko se filtrira po kvadraturi oba polja ce biti obavezna (primer od 0 do 100)
    if min_kv and max_kv:
        nekretnine = nekretnine.filter(Nekretnina.kvadratura.between(min_kv, max_kv))

    parking = request.args.get("parking")
    if parking:
        parking = parking == "True"
        nekretnine = nekretnine.filter_by(ima_parking=parking)

    stranica = int(request.args.get("page"))
    stranica_podaci = db.paginate(nekretnine.order_by("id"), page=stranica, per_page=2)

    return jsonify({
        "trenutna_stranica": stranica_podaci.page,
        "ukupno_stranica": stranica_podaci.pages,
        "rezultata_po_stranici": stranica_podaci.per_page,
        "total_rezultata": stranica_podaci.total,
        "nekretnine": [nekretnina.serialized_data() for nekretnina in stranica_podaci.items]
    })


@app.post("/api/nekretnina/")
def dodaj_nekretninu():
    data = request.json
    if "dodatna_opremljenost" in data.keys():
        data["dodatna_opremljenost"] = json.dumps(data["dodatna_opremljenost"])
    try:
        serialized_data = schema.load(data, unknown=EXCLUDE, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    nova_nekretnina = Nekretnina(**serialized_data)

    db.session.add(nova_nekretnina)
    db.session.commit()
    return jsonify(nova_nekretnina.serialized_data()), 201


@app.patch("/api/nekretnina/<int:id>")
def update_nekretnine(id):
    data = request.json

    if "id" in data.keys():
        return jsonify({"error": "ID se ne moze menjati"})

    nekretnina = db.session.execute(db.select(Nekretnina).filter_by(id=id)).scalar()

    if not nekretnina:
        raise NotFound(description='Nekretnina sa tim ID ne postoji')

    if "dodatna_opremljenost" in data.keys():
        data["dodatna_opremljenost"] = json.dumps(data["dodatna_opremljenost"])

    nekretnina_data = nekretnina.serialized_data()
    nekretnina_data.update(data)

    try:
        serialized_data = schema.load(nekretnina_data, unknown=EXCLUDE)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    for k, v in serialized_data.items():
        setattr(nekretnina, k, v)

    db.session.merge(nekretnina)
    db.session.commit()

    return jsonify(nekretnina.serialized_data())
