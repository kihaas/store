from alembic import context
from website import create_app
from website.models import db


app = create_app()
app.app_context().push()
target_metadata = db.metadata

def run_migrations_online():
    connectable = db.engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True  # Для работы с SQLite
        )
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
