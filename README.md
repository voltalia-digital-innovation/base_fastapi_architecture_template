# Base Fastapi Architecture template

This project stands to support full base-fastapi work cycle according to audit rules

- Route for Swagger api docs: `<domain>/docs`
- Take a look at the "manage.py" file in the root directory to CLI facilities

### ORM POC explaination: `https://github.com/voltalia-digital-innovation/fastapi_orm_poc`

## Requirements:

- Python 3.12.x
- Windows 10+
- Docker

## How to Run:

- Virtual environment: `python -m venv env`
- Use Virtual environment: `.\env\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`
- Install `fastapi[standard]`: `pip install "fastapi[standard]"`
- Run migrations `python manage.py migrate`
- Start app:`fastapi dev main.py` or `uvicorn main:app --reload`, or use the CLI facilities `python manage.py runserver`

#### Tests:

- Run tests: `pytest`
- Run tests throught Coverage.py: `coverage run -m pytest`
- See tests coverage (after ran the tests throught coverage): `coverage html -d coverage_html`

Made by: Digital Innovation - Brazil
