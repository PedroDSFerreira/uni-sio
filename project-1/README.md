<div align="center">
    <h1>Vulnerable webserver exploitation</h1>
    <i>
    Cherrypy server that hosts an e-health website.
    There are two versions of this website, one secure and the other vulnerable.
    </i>
</div>

<br>


## Software

- HTML/CSS/JS (frontend)
- Cherrypy (webserver)
- SQLite (database)

## Get Started
### Requirements
- Docker
- Docker-compose

### Installation
- `cd` into project directory
- To run docker containers, do:

    ```bash
    docker compose up --build
    ```
    - Insecure application will be available at http://localhost:7000
    - Secure application will be available at https://localhost:8000

<br>

## Vulnerabilities
- [CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')](https://cwe.mitre.org/data/definitions/79.html)
- [CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')](https://cwe.mitre.org/data/definitions/89.html)
- [CWE-312: Cleartext Storage of Sensitive Information](https://cwe.mitre.org/data/definitions/312.html)
- [CWE-319: Cleartext Transmission of Sensitive Information](https://cwe.mitre.org/data/definitions/319.html)

<br>

---

## Authors

- [André Silva](https://github.com/andrecastrosilva)
- [Francisco Cardita](https://github.com/FranciscoCardita)
- [Pedro Ferreira](https://github.com/PedroDSFerreira)
- [Renato Ourives](https://github.com/RenaGold)
