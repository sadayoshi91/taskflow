# TaskFlow

TaskFlow to webowa aplikacja do zarządzania **projektami, zadaniami, pracownikami i komentarzami**.
Projekt powstał w Django i pokazuje pracę z bazą danych, REST API, uwierzytelnianiem JWT,
cache w Redis oraz zadaniami w tle (Celery). Frontend renderowany jest przez Django Templates.

## Funkcje

- Rejestracja i logowanie użytkowników (`django.contrib.auth`), role: administrator, kierownik, pracownik
- Zarządzanie projektami i zadaniami z poziomu strony WWW (tworzenie, edycja, usuwanie)
- Komentarze do zadań i szybka zmiana statusu zadania
- Profil użytkownika z możliwością wgrania avatara (obsługa mediów `ImageField`)
- REST API (Django REST Framework) z dokumentacją Swagger / ReDoc
- Uwierzytelnianie tokenami JWT (SimpleJWT)
- Cache listy projektów i aktywnych zadań (Redis)
- Zadanie Celery generujące przypomnienia o zadaniach z bliskim terminem
- Rozbudowany panel administracyjny Django (filtry, wyszukiwanie, inlines)
- Generowanie danych testowych komendą `seed_db` (biblioteka Faker)

## Stack technologiczny

- Python 3.14, Django 5.2 LTS
- Django REST Framework, SimpleJWT, drf-spectacular
- PostgreSQL, Redis, Celery
- Pillow (obrazy), Faker (dane testowe)

## Wymagania

- Python 3.14
- PostgreSQL i Redis (do pełnej konfiguracji)

## Uruchomienie (PostgreSQL + Redis)

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# zmienne środowiskowe – wzór w env.example.ps1
. .\env.example.ps1

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Worker i harmonogram Celery (w osobnych terminalach):

```powershell
celery -A config worker -l info --pool=solo
celery -A config beat -l info
```

## Szybkie uruchomienie bez PostgreSQL i Redis (SQLite + cache w pamięci)

```powershell
python manage.py migrate --settings=config.test_settings
python manage.py loaddata taskflow_demo_data --settings=config.test_settings
python manage.py runserver --settings=config.test_settings
```

## Dane testowe

```powershell
python manage.py seed_db --managers 3 --employees 12 --projects 6
```

Konta z fixture `taskflow_demo_data` (hasło: `TaskFlow123!`):

| Login | Rola |
| --- | --- |
| `admin_demo` | administrator |
| `manager_demo` | kierownik |
| `employee_demo` | pracownik |

## Ważne adresy

- Strona WWW: `http://127.0.0.1:8000/`
- Panel admina: `http://127.0.0.1:8000/admin/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`

## Testy

```powershell
python manage.py test --settings=config.test_settings
```

## Struktura projektu

```
apps/
  users/      # użytkownicy, role, profil, JWT, komenda seed_db
  projects/   # projekty
  tasks/      # zadania, powiadomienia, zadanie Celery
  comments/   # komentarze
  web/        # widoki HTML (frontend)
config/       # ustawienia, urls, Celery
templates/    # szablony HTML
static/       # CSS i JS
fixtures/     # dane demonstracyjne
```
