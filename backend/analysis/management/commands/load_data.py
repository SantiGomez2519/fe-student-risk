from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from analysis.loader import load_from_path

DEFAULT_FILE = "Resultados — Riesgo Estudiantil.xlsx"


class Command(BaseCommand):
    help = "Carga los datos del formulario desde un archivo Excel y calcula el riesgo."

    def add_arguments(self, parser):
        parser.add_argument(
            "path", nargs="?", default=None,
            help="Ruta al .xlsx. Por defecto usa el archivo del repositorio.",
        )
        parser.add_argument("--sheet", default=None, help="Nombre de la hoja a leer.")

    def handle(self, *args, **options):
        path = options["path"]
        if not path:
            path = str(Path(settings.REPO_ROOT) / DEFAULT_FILE)
        if not Path(path).exists():
            raise CommandError(f"No existe el archivo: {path}")

        self.stdout.write(f"Cargando: {path}")
        stats = load_from_path(path, options["sheet"])
        self.stdout.write(self.style.SUCCESS(
            f"Listo. Filas={stats['rows']} creados={stats['created']} "
            f"actualizados={stats['updated']}"
        ))
