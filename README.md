# RBT test
Pre samog rada napraviti virutal env i instalirati potrebne pakete
## Server
Pre pokretanja servera bitno je napraviti .env fajl koji ce u sebi imati DATABASE_URL (kao u .env_template) i napraviti tabelu u bazi (db.create_all())

Endpoints:
1. Select za id: GET -> /api/nekretnina/[id]
2. Pretraga: GET -> /api/nekretnina/?tip=&min_kv=&max_kv=&parking=&page=2
    
    Samo page je obavezan filter, a ukoliko se radi i pretraga po kvadraturi onda su i min i max potrebni
3. Kreiranje nove nekretnine POST -> /api/nekretnina/
4. Update postojece: PATCH -> /api/nekretnina/[id]

## Crawler
Crawler se pokrece samo sa python crawler.py

Koristi BeautifulSoup da pokupi podatke sa stranica i requests da salje podatke na server.