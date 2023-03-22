from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

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
    lokacija_grad = db.Column(db.String(30), nullable=True)
    lokacija_deo_grada = db.Column(db.String(50), nullable=True)
    kvadratura = db.Column(db.Integer, nullable=True)
    godina_izgradnje = db.Column(db.Integer, nullable=True)
    povrsina_zemljista = db.Column(db.Float, nullable=True)
    sprat = db.Column(db.Integer, nullable=True)
    ukupno_spratova = db.Column(db.Integer, nullable=True)
    uknjizeno = db.Column(db.Boolean, nullable=True)
    tip_grejanja = db.Column(db.String(50), nullable=True)
    broj_soba = db.Column(db.Integer, nullable=True)
    broj_kupatila = db.Column(db.Integer, nullable=True)
    ima_parking = db.Column(db.Boolean, nullable=True)
    dodatna_opremljenost = db.Column(db.String(1000), nullable=True)

    def serialized_data(self):
        return {
            "id": self.id,
            "link_nekretnine": self.link_nekretnine,
            "stan": self.stan,
            "izdavanje": self.izdavanje,
            "lokacija_grad": self.lokacija_grad,
            "lokacija_deo_grada": self.lokacija_deo_grada,
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
            "dodatna_opremljenost": self.dodatna_opremljenost 
        }


@app.get("/api/nekretnina/<id>")
def pretraga_id(id):
    nekretnina = Nekretnina.query.filter_by(id=id).first()

    if nekretnina:
        return jsonify(nekretnina.serialized_data())

    return jsonify({"info": "Nekretnina sa tim ID ne postoji"})


@app.get("/api/nekretnina/")
def full_pretraga():
    nekretnine = Nekretnina.query.filter().order_by("id")
    tip = request.args.get("tip")
    if tip:
        if tip == "stan":
            tip=True
        else:
            tip=False
        
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

    print(nekretnine.all())
    stranica = int(request.args.get("page"))
    nekretnine = nekretnine.all()[(stranica-1)*2:stranica*2]
    return jsonify({"nekretnine": [nekretnina.serialized_data() for nekretnina in nekretnine]})

@app.post("/api/nekretnina/")
def dodaj_nekretninu():
    data = request.json
    nova_nekretnina = Nekretnina(**data)
    db.session.add(nova_nekretnina)
    db.session.commit()
    return data

@app.patch("/api/nekretnina/<id>")
def update_nekretnine(id):
    nekretnina = Nekretnina.query.filter_by(id=id)
    print(nekretnina)
    data = request.json
    if "id" in data.keys():
        return jsonify({"error": "ID se ne moze menjati"})
    if nekretnina.all():
        nekretnina = nekretnina.update(data)
        db.session.commit()
        return jsonify(Nekretnina.query.filter_by(id=id).first().serialized_data())

    return jsonify({"info": "Nekretnina sa tim ID ne postoji"})