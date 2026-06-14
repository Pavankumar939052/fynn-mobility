# Fyn Mobility

Full-stack version of the Vehicle Service Management System assignment.

## Features

- Add service items with pricing
- Create vehicle service jobs
- Add service lines to a job
- Calculate final job amount
- Mark jobs as paid
- View daily, monthly, and yearly revenue charts

## Stack

- Backend: Django
- Frontend: React + Vite
- Database: SQLite
- Charts: Recharts

## Backend

```bash
python -m pip install -r requirements.txt
python backend/manage.py migrate
python backend/manage.py runserver
```

Backend URL: `http://127.0.0.1:8000/`

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://127.0.0.1:5174/`

## Tests

```bash
python backend/manage.py test garage
```
