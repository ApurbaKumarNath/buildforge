import json
import re
from django.core.management.base import BaseCommand
from catalog.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Component

# --- Data Cleaning Helper Functions (FINAL, ROBUST VERSION) ---

def clean_form_factor(value):
    """Translates common case form factors to motherboard form factors."""
    if not isinstance(value, str): return None
    value = value.strip().lower()
    if 'mid tower' in value or 'full tower' in value:
        return 'ATX'
    if 'mini tower' in value:
        return 'Micro-ATX'
    # Add more specific mappings if needed, e.g., Mini-ITX
    return None # Return None if no match, to not save invalid data

def clean_efficiency_rating(value):
    """Standardizes PSU efficiency ratings to match model choices."""
    if not isinstance(value, str) or 'N/A' in value:
        return None
    value = value.lower()
    if 'titanium' in value: return 'Titanium'
    if 'platinum' in value: return 'Platinum'
    if 'gold' in value: return 'Gold'
    if 'silver' in value: return 'Silver'
    if 'bronze' in value: return 'Bronze'
    if '80' in value: return '80+' # Catches '80 Plus' and '80+'
    return None

def clean_capacity_gb(value):
    """Converts strings like '1TB' or '512GB' to an integer in GB."""
    if isinstance(value, int): return value
    if not isinstance(value, str): return None
    
    value = value.upper().strip()
    # Find all numbers (including decimals) in the string
    numbers = re.findall(r"[\d\.]+", value)
    if not numbers: return None

    try:
        number = float(numbers[0])
        if 'TB' in value:
            return int(number * 1000)
        elif 'GB' in value:
            return int(number)
    except (ValueError, IndexError):
        return None
    return None

def clean_integer(value):
    """Converts a value to an integer, handling 'N/A' and other non-numerics."""
    if isinstance(value, int): return value
    if not isinstance(value, str): return None
    
    # Find all digits in the string
    numbers = re.findall(r"\d+", value)
    if not numbers: return None

    try:
        return int(numbers[0])
    except (ValueError, IndexError):
        return None
    return None

def clean_decimal(value):
    """Converts a value to a decimal, handling ranges and non-numerics."""
    if isinstance(value, (int, float)): return value
    if not isinstance(value, str): return None
        
    # Find all floating point or integer numbers
    numbers = re.findall(r"[\d\.]+", value)
    if not numbers: return None
    
    try:
        # Always take the first number found in a range like "3.70 GHz - 4.20 GHz"
        return float(numbers[0])
    except (ValueError, IndexError):
        return None
    return None

# --- Main Command ---

class Command(BaseCommand):
    help = 'Imports and cleans component data from JSON files.'

    def add_arguments(self, parser):
        parser.add_argument('component_type', type=str, help='The type of component (e.g., CPU, GPU).')
        parser.add_argument('json_file', type=str, help='The path to the JSON file.')

    def handle(self, *args, **kwargs):
        component_type = kwargs['component_type'].upper()
        json_file_path = kwargs['json_file']
        
        self.stdout.write(f"Importing and cleaning '{component_type}' data from '{json_file_path}'...")

        MODEL_MAP = {'CPU': CPU, 'GPU': GPU, 'MOTHERBOARD': Motherboard, 'RAM': RAM, 'STORAGE': Storage, 'PSU': PSU, 'CASE': Case}
        ModelClass = MODEL_MAP.get(component_type)
        if not ModelClass:
            self.stderr.write(self.style.ERROR(f"Invalid component type: '{component_type}'."))
            return

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {json_file_path}"))
            return
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f"JSON Decode Error in {json_file_path}: {e}"))
            return

        created_count = 0
        updated_count = 0

        for entry in data:
            name = entry.get('name')
            if not name:
                continue

            # --- The Quality Control (QC) Station ---
            cleaned_data = entry.copy() # Start with a copy of the original data

            # Apply cleaning functions based on component type
            if component_type == 'CASE':
                cleaned_data['form_factor'] = clean_form_factor(entry.get('form_factor'))
                cleaned_data['max_gpu_length'] = clean_integer(entry.get('max_gpu_length'))
            
            elif component_type == 'PSU':
                cleaned_data['wattage'] = clean_integer(entry.get('wattage'))
                cleaned_data['efficiency_rating'] = clean_efficiency_rating(entry.get('efficiency_rating'))

            elif component_type == 'STORAGE':
                cleaned_data['capacity_gb'] = clean_capacity_gb(entry.get('capacity_gb'))

            elif component_type == 'CPU':
                cleaned_data['clock_speed'] = clean_decimal(entry.get('clock_speed'))
                cleaned_data['core_count'] = clean_integer(entry.get('core_count'))

            elif component_type == 'GPU':
                cleaned_data['vram_gb'] = clean_capacity_gb(entry.get('vram_gb'))
                cleaned_data['gpu_clock_speed'] = clean_integer(entry.get('gpu_clock_speed'))

            elif component_type == 'RAM':
                cleaned_data['capacity_gb'] = clean_capacity_gb(entry.get('capacity_gb'))
                cleaned_data['speed_mhz'] = clean_integer(entry.get('speed_mhz'))

            # Remove keys from cleaned_data that are not actual model fields to prevent errors
            valid_fields = {f.name for f in ModelClass._meta.get_fields()}
            # This line also includes the fields from the parent 'Component' model
            valid_fields.update({f.name for f in Component._meta.get_fields()})
            
            data_to_save = {k: v for k, v in cleaned_data.items() if k in valid_fields}

            try:
                obj, created = ModelClass.objects.update_or_create(
                    name=name,
                    defaults=data_to_save
                )
                if created: created_count += 1
                else: updated_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Could not save '{name}': {e} | Data: {data_to_save}"))

        self.stdout.write(self.style.SUCCESS(f"Import for '{component_type}' complete! Created: {created_count}, Updated: {updated_count}"))