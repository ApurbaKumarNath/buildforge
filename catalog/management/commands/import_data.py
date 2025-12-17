# catalog/management/commands/import_data.py

import json
from django.core.management.base import BaseCommand
from catalog.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case

class Command(BaseCommand):
    help = 'Imports component data from a specified JSON file for a specific component type.'

    def add_arguments(self, parser):
        # Argument 1: The type of component (e.g., "CPU", "GPU")
        parser.add_argument('component_type', type=str, help='The type of component to import (e.g., CPU, GPU).')
        
        # Argument 2: The path to the JSON file
        parser.add_argument('json_file', type=str, help='The path to the JSON file to import.')

    def handle(self, *args, **kwargs):
        component_type = kwargs['component_type'].upper() # Use .upper() to make it case-insensitive (cpu -> CPU)
        json_file_path = kwargs['json_file']
        
        self.stdout.write(f"Attempting to import '{component_type}' data from '{json_file_path}'...")

        # A dictionary to map the 'type' string from the command line to the actual Django Model class
        MODEL_MAP = {
            'CPU': CPU,
            'GPU': GPU,
            'MOTHERBOARD': Motherboard,
            'RAM': RAM,
            'STORAGE': Storage,
            'PSU': PSU,
            'CASE': Case,
        }

        ModelClass = MODEL_MAP.get(component_type)
        if not ModelClass:
            self.stderr.write(self.style.ERROR(f"Invalid component type: '{component_type}'. Please use one of {list(MODEL_MAP.keys())}"))
            return

        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {json_file_path}"))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f"Error decoding JSON from the file: {json_file_path}"))
            return

        created_count = 0
        updated_count = 0

        for entry in data:
            # All fields are now at the top level in the JSON, so we can pass the whole entry.
            # We use the 'name' field as the unique identifier to check for existence.
            name = entry.get('name')
            if not name:
                self.stdout.write(self.style.WARNING(f"Skipping entry with no name: {entry}"))
                continue

            try:
                # update_or_create finds an object by 'name'.
                # If found, it updates it with the values in 'defaults'.
                # If not found, it creates a new object with all values.
                obj, created = ModelClass.objects.update_or_create(
                    name=name,
                    defaults=entry
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing entry '{name}': {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Import for '{component_type}' complete! "
            f"Created: {created_count}, Updated: {updated_count}"
        ))