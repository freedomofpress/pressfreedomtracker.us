from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0117_categorypage_google_sheets_name"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "CREATE EXTENSION IF NOT EXISTS unaccent;",
                """
                CREATE TEXT SEARCH CONFIGURATION unaccented_english (COPY = english);
                ALTER TEXT SEARCH CONFIGURATION unaccented_english
                    ALTER MAPPING FOR hword, hword_part, word
                    WITH unaccent, english_stem;
                """,
            ],
            reverse_sql=[
                "DROP TEXT SEARCH CONFIGURATION IF EXISTS unaccented_english;",
                "DROP EXTENSION IF EXISTS unaccent;",
            ],
        ),
    ]
