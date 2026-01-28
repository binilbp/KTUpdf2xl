# Database Scripts (PostgreSQL)

This folder contains all PostgreSQL-related scripts used in this project.

## Contents

- Schema definitions and table creation
- Migrations and seed data
- Utility SQL queries
- Scripts related to JWT-based authentication (e.g., user tables, tokens)

## Notes

- Ensure PostgreSQL is installed and running.
- JWT authentication relies on a `users` table with appropriate fields (e.g., `email`, `hashed_password`, `is_active`).
- Modify connection strings or environment variables as needed for your local or production setup.

## Usage

You can run scripts using the `psql` CLI or any SQL GUI like pgAdmin or DBeaver.

```bash
psql -U your_username -d your_database -f script.sql
