import requests
from bs4 import BeautifulSoup

server_endpoint = "http://localhost:5000/api/nekretnina/"

base_url = "https://www.nekretnine.rs"
stranice_url = "https://www.nekretnine.rs/stambeni-objekti/lista/po-stranici/10/stranica/"
trenutna_stranica = 1
odradjene_nekretnine = []


def obradi_nekretninu(link_nekretnine):

    req = requests.get(link_nekretnine)
    html_deo = req.text
    soup = BeautifulSoup(html_deo, "lxml")

    nova_nekretnina = {
        "link_nekretnine": link_nekretnine, #
        "stan":  None, #
        "izdavanje":  None, #
        "lokacija_grad":  None, #
        "lokacija_deo_grada":  None, #
        "kvadratura":  None, #
        "godina_izgradnje":  None, #
        "povrsina_zemljista":  None, # 
        "sprat":  None, #
        "ukupno_spratova":  None, #
        "uknjizeno":  None, #
        "tip_grejanja":  None,
        "broj_soba":  None,  #
        "broj_kupatila":  None,  #
        "ima_parking":  None, #
        "dodatna_opremljenost": []
    }

    # cena = int(soup.find_all("h4", {"class": "stickyBox__price"})[0].text.split("EUR")[0].strip().replace(" ", ""))
    stan = "stan" in soup.find("h2", {"class": "detail-seo-subtitle"}).text
    lokacija =  soup.find("h3", {"class": "stickyBox__Location"}).text.split(", ")
    nova_nekretnina["stan"] = stan
    try:
        nova_nekretnina["lokacija_grad"] = lokacija[0].strip()
        nova_nekretnina["lokacija_deo_grada"] = lokacija[1].strip()
    except IndexError:
        print("Nema potpunih podataka za lokaciju")


    glavni_detalji = soup.find("div", {"class": "property__main-details"})
    
    if glavni_detalji:

        for g in glavni_detalji.findChildren("li"):
            glavni_text = g.text.strip().split(":")
            znacenje = glavni_text[0].strip()
            vrednost = glavni_text[1].strip()
            if znacenje == "Grejanje":
                nova_nekretnina["tip_grejanja"] = vrednost
            if znacenje == "Parking":
                if vrednost == "Da":
                    nova_nekretnina["ima_parking"] = True
                else:
                    nova_nekretnina["ima_parking"] = False



    extra_detalji_divs = soup.find_all("div", {"class": "property__amenities"})
    for e in extra_detalji_divs:
        liste = e.findChildren("li")
        for x in liste:
            podaci_o_nekretnini = x.findChildren("strong")
            if podaci_o_nekretnini:
                znacenje = x.text.split(":")[0].strip()
                vrednost = podaci_o_nekretnini[0].text.strip()
                if znacenje == "Transakcija":
                    if vrednost == "Izdavanje":
                        nova_nekretnina["izdavanje"] = True
                    else:
                        nova_nekretnina["izdavanje"] = False
                elif znacenje == "Kvadratura":
                    nova_nekretnina["kvadratura"] = float(vrednost.split(" ")[0])
                elif znacenje == "Godina izgradnje":
                    nova_nekretnina["godina_izgradnje"] = vrednost
                elif znacenje == "Površina zemljišta":
                    nova_nekretnina["povrsina_zemljista"] = float(vrednost.split(" ")[0])
                elif znacenje == "Spratnost":
                    if vrednost == "Prizemlje":
                        vrednost = 0
                    elif vrednost == "Visoko prizemlje":
                        vrednost = 0.5
                    elif vrednost == "Suteren":
                        vrednost = -1
                    nova_nekretnina["sprat"] = float(vrednost)
                elif znacenje == "Ukupan broj spratova":
                    nova_nekretnina["ukupno_spratova"] = float(vrednost)
                elif znacenje == "Uknjiženo" and vrednost == "Da":
                    nova_nekretnina["uknjizeno"] = True
                elif znacenje == "Ukupan broj soba":
                    nova_nekretnina["broj_soba"] = float(vrednost)
                elif znacenje == "Broj kupatila":
                    nova_nekretnina["broj_kupatila"] = float(vrednost)
            else:
                vrednost = x.text.strip()
                if ":" in vrednost:
                    vrednost = vrednost.split(":")
                    nova_nekretnina["dodatna_opremljenost"].append(f"{vrednost[0].strip()}: {vrednost[1].strip()}")
                else:
                    nova_nekretnina["dodatna_opremljenost"].append(vrednost)

    return nova_nekretnina


while trenutna_stranica < 50:
    # print("STRANICA:", trenutna_stranica)
    stranica_pretrage = stranice_url + str(trenutna_stranica)
    req = requests.get(stranica_pretrage)
    soup = BeautifulSoup(req.text, "lxml")
    ponude = soup.find_all("h2", {"class": "offer-title"})
    for ponuda in ponude:
        link_nekretnine = base_url + ponuda.findChildren("a")[0]["href"]
        if link_nekretnine not in odradjene_nekretnine:
            odradjene_nekretnine.append(link_nekretnine)
            nekretnina_info = obradi_nekretninu(link_nekretnine)
            requests.post(server_endpoint, json=nekretnina_info)
    trenutna_stranica += 1

