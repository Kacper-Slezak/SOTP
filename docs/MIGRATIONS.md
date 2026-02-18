# Database Migration Guide

This guide explains how to work with database migrations in the SOTP project. We use Alembic for database schema management with support for multiple databases (PostgreSQL and TimescaleDB).

## Prerequisites

- Docker and Docker Compose installed
- Backend container running
- Basic understanding of database migrations

## Project Database Structure

The project uses two separate databases:

- **PostgreSQL** (`postgres` branch) - For application data (users, devices, configurations)
- **TimescaleDB** (`timescale` branch) - For time-series metrics (ping results, performance data)

Each database has its own migration branch in Alembic.

## Working with Migrations

### 1. Access the Backend Container

All migration commands should be run inside the backend container:

```bash
make dev
make shell-backend
```

To find your container name:

```bash
docker ps | grep backend
```

### 2. Check Current Migration Status

Before making changes, check which migrations are applied:

**For TimescaleDB:**

```bash
alembic -c alembic.ini -x db=timescale current
alembic -c alembic.ini -x db=timescale history
```

**For PostgreSQL:**

```bash
alembic -c alembic.ini -x db=postgres current
alembic -c alembic.ini -x db=postgres history
```

### 3. Apply Existing Migrations

To upgrade your database to the latest version:

**For TimescaleDB:**

```bash
alembic -c alembic.ini -x db=timescale upgrade timescale@head
```

**For PostgreSQL:**

```bash
alembic -c alembic.ini -x db=postgres upgrade postgres@head
```

**Important:** Always specify the branch name (`timescale@head` or `postgres@head`) to avoid "Multiple head revisions" errors.

### 4. Create New Migrations

When you modify SQLAlchemy models, create a new migration:

**For TimescaleDB:**

```bash
alembic -c alembic.ini -x db=timescale revision --autogenerate -m "description of changes" --branch-label timescale
```

**For PostgreSQL:**

```bash
alembic -c alembic.ini -x db=postgres revision --autogenerate -m "description of changes" --branch-label postgres
```

**Tips for migration descriptions:**

- Use clear, descriptive messages: `"add ping_results table"`, `"add user email column"`
- Keep it concise but informative
- Use present tense: "add", "modify", "remove"

### 5. Review Generated Migration

After creating a migration, **always review the generated file** in `alembic/versions/`:

```bash
ls -la alembic/versions/
cat alembic/versions/<generated_revision_id>_*.py
```

Check that:

- The `upgrade()` function contains the correct changes
- The `downgrade()` function properly reverses those changes
- No sensitive data or unexpected changes are included

### 6. Apply Your New Migration

After reviewing:

```bash
# For TimescaleDB
alembic -c alembic.ini -x db=timescale upgrade timescale@head

# For PostgreSQL
alembic -c alembic.ini -x db=postgres upgrade postgres@head
```

### 7. Verify the Changes

Connect to the database to verify your changes were applied:

**For TimescaleDB:**

```bash
psql postgresql://sotp_timescale_user:dev_password_456@timescale:5432/sotp_metrics_db -c "\d table_name"
```

**For PostgreSQL:**

```bash
psql postgresql://sotp_user:dev_password_123@postgres:5432/sotp_db -c "\d table_name"
```

Replace `table_name` with the actual table you want to inspect.

## Common Commands Reference

### Check Migration Status

```bash
# Current revision
alembic -c alembic.ini -x db=<timescale|postgres> current

# Show all migrations
alembic -c alembic.ini -x db=<timescale|postgres> history

# Show available heads
alembic -c alembic.ini -x db=<timescale|postgres> heads
```

### Upgrade/Downgrade

```bash
# Upgrade to latest
alembic -c alembic.ini -x db=<timescale|postgres> upgrade <branch>@head

# Upgrade to specific revision
alembic -c alembic.ini -x db=<timescale|postgres> upgrade <revision_id>

# Downgrade one revision
alembic -c alembic.ini -x db=<timescale|postgres> downgrade -1

# Downgrade to specific revision
alembic -c alembic.ini -x db=<timescale|postgres> downgrade <revision_id>
```

### Create Migrations

```bash
# Auto-generate migration
alembic -c alembic.ini -x db=<timescale|postgres> revision --autogenerate -m "message" --branch-label <branch>

# Create empty migration (for manual changes)
alembic -c alembic.ini -x db=<timescale|postgres> revision -m "message" --branch-label <branch>
```

## Troubleshooting

### Error: "Target database is not up to date"

This means there are pending migrations. Apply them first:

```bash
alembic -c alembic.ini -x db=timescale upgrade timescale@head
```

### Error: "Multiple head revisions are present"

You need to specify which branch to work with:

```bash
# Instead of:
alembic upgrade head

# Use:
alembic -c alembic.ini -x db=timescale upgrade timescale@head
```

### Migration Applied but Not Recorded

If a migration was applied manually but Alembic doesn't know about it, stamp the database:

```bash
alembic -c alembic.ini -x db=timescale stamp <revision_id>
```

### Can't Connect to Database from Host

Database hostnames like `timescale` and `postgres` only work inside Docker's network. Always run Alembic commands from inside the backend container, not from your host machine.

### Need to Undo Last Migration

```bash
# Downgrade one step
alembic -c alembic.ini -x db=timescale downgrade -1

# Check current status
alembic -c alembic.ini -x db=timescale current
```

## Best Practices

1. **Always review auto-generated migrations** - Alembic might not detect all changes correctly
2. **Test migrations in development first** - Before applying to production
3. **Keep migrations small and focused** - One logical change per migration
4. **Write reversible migrations** - Always implement proper `downgrade()` functions
5. **Commit migration files to version control** - They're part of your codebase
6. **Don't modify existing migrations** - Create new ones to fix issues
7. **Back up data before major migrations** - Especially in production

## Database Credentials

### Development Environment

**TimescaleDB:**

- Host: `timescale` (inside Docker) / `localhost:5432` (from host)
- Database: `sotp_metrics_db`
- User: `sotp_timescale_user`
- Password: `dev_password_456`

**PostgreSQL:**

- Host: `postgres` (inside Docker) / `localhost:5433` (from host)
- Database: `sotp_db`
- User: `sotp_user`
- Password: `dev_password_123`

**Note:** Production credentials should be stored in environment variables and never committed to version control.

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [TimescaleDB Documentation](https://docs.timescale.com/)

## Need Help?

If you encounter issues not covered here:

1. Check the Alembic documentation
2. Review the `alembic/env.py` file for custom configuration
3. Ask the team in the project chat
4. Check Docker logs: `docker logs <container-name>`
