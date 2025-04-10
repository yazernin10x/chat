from pathlib import Path
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Supprime tous les fichiers de migration dans les applications du dossier apps"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force la suppression sans demander de confirmation",
        )

    def handle(self, *args, **options):
        apps_dir = Path("apps")

        if not options["force"]:
            confirm = input(
                "⚠️  Cette action va supprimer tous les fichiers de migration. Êtes-vous sûr ? [y/N] "
            )
            if confirm.lower() != "y":
                self.stdout.write(self.style.WARNING("Operation annulée"))
                return

        migration_files_count = 0

        for app_dir in apps_dir.iterdir():
            if app_dir.is_dir():
                migrations_path = app_dir / "migrations"

                if migrations_path.exists():
                    for migration_file in migrations_path.iterdir():
                        if migration_file.name != "__init__.py":
                            try:
                                if migration_file.is_file():
                                    migration_file.unlink()
                                    migration_files_count += 1
                                    self.stdout.write(
                                        self.style.SUCCESS(
                                            f"Supprimé : {migration_file}"
                                        )
                                    )
                            except Exception as e:
                                raise CommandError(
                                    f"Erreur lors de la suppression de {migration_file}: {e}"
                                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Suppression terminée. {migration_files_count} fichiers de migration supprimés."
            )
        )

        self.stdout.write(
            self.style.WARNING(
                "\nPensez à :\n"
                "1. Supprimer votre base de données si nécessaire\n"
                "2. Recréer une nouvelle base de données\n"
                "3. Exécuter python manage.py makemigrations\n"
                "4. Exécuter python manage.py migrate"
            )
        )
