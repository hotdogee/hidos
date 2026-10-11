"""
Regenerate the example results of the analysis apps (#44):

    python manage.py generate_examples [--app cellc2 ...]

Runs every app on <app>/static/<app>/images/Example.<ext> and writes
Example_r.jpg and Example.json next to it, so the examples always show what
the current algorithm version produces.
"""
import json
import os
import shutil
import sys
import tempfile
import time

from django.core.management.base import BaseCommand, CommandError

from cell.examples import analysis_apps, example_dir, example_input
from cell.tasks import json_safe


class _File:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)


class ExampleRecord:
    """The attributes of a Task that the analysis functions use."""

    def __init__(self, uploaded, workdir):
        ext = os.path.splitext(uploaded)[1].lower()
        self.name = os.path.basename(uploaded)
        self.uploaded_image = _File(uploaded)
        self.result_image = _File(os.path.join(workdir, 'result' + ext))
        self.result_display = _File(os.path.join(workdir, 'result_display.jpg'))


class Command(BaseCommand):
    help = 'Run the analysis apps on their example images and save the results next to them.'

    def add_arguments(self, parser):
        parser.add_argument('--app', action='append', dest='apps', help='Only this app (repeatable).')

    def handle(self, *args, **options):
        configs = analysis_apps()
        if options['apps']:
            unknown = set(options['apps']) - {c.label for c in configs}
            if unknown:
                raise CommandError('Unknown analysis app(s): %s' % ', '.join(sorted(unknown)))
            configs = [c for c in configs if c.label in options['apps']]
        for config in configs:
            uploaded = example_input(config)
            if uploaded is None:
                self.stdout.write(self.style.WARNING('%s: no Example image, skipped' % config.label))
                continue
            workdir = tempfile.mkdtemp(prefix='hidos-example-')
            try:
                record = ExampleRecord(uploaded, workdir)
                started = time.time()
                result = json_safe(sys.modules[config.name].run(record))
                shutil.copyfile(record.result_display.path, os.path.join(example_dir(config), 'Example_r.jpg'))
                with open(os.path.join(example_dir(config), 'Example.json'), 'w', encoding='utf-8', newline='\n') as fh:
                    json.dump(result, fh, indent=2, sort_keys=True)
                    fh.write('\n')
            finally:
                shutil.rmtree(workdir, ignore_errors=True)
            self.stdout.write(self.style.SUCCESS('%s: %s (%.1fs)' % (config.label, json.dumps(result, sort_keys=True), time.time() - started)))
