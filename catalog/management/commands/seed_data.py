# catalog/management/commands/seed_data.py

#__________________________________________________________________________________________________________________________ (akn)

from django.core.management.base import BaseCommand
from catalog.models import Component, CPU, GPU, Motherboard, RAM, Storage, PSU, Case

class Command(BaseCommand):
    help = 'Populates the database with test data for demonstration using a robust, manual method.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database using robust manual assignment...")

        # Clear existing data to ensure a clean slate
        Component.objects.all().delete()
        self.stdout.write("Deleted old data.")

        # ==========================================
        # 1. CPUs
        # ==========================================
        cpus = [
            {'name': 'Core i3-12100F', 'manufacturer': 'Intel', 'price': 100.00, 'performance_tier': 'Entry', 'core_count': 4, 'clock_speed': 3.3, 'socket': 'LGA1700'},
            {'name': 'Ryzen 5 5600X', 'manufacturer': 'AMD', 'price': 150.00, 'performance_tier': 'Mid', 'core_count': 6, 'clock_speed': 3.7, 'socket': 'AM4'},
            {'name': 'Core i5-13600K', 'manufacturer': 'Intel', 'price': 300.00, 'performance_tier': 'Mid', 'core_count': 14, 'clock_speed': 3.5, 'socket': 'LGA1700'},
            {'name': 'Ryzen 9 7950X', 'manufacturer': 'AMD', 'price': 550.00, 'performance_tier': 'High', 'core_count': 16, 'clock_speed': 4.5, 'socket': 'AM5'},
            {'name': 'Core i9-13900K', 'manufacturer': 'Intel', 'price': 580.00, 'performance_tier': 'High', 'core_count': 24, 'clock_speed': 3.0, 'socket': 'LGA1700'},
        ]

        for data in cpus:
            obj = CPU()
            # Parent fields
            obj.name = data['name']
            obj.manufacturer = data['manufacturer']
            obj.price = data['price']
            obj.performance_tier = data['performance_tier']
            # Child fields
            obj.core_count = data['core_count']
            obj.clock_speed = data['clock_speed']
            obj.socket = data['socket']
            obj.save()
            self.stdout.write(f"Created CPU: {obj.name}")

        # ==========================================
        # 2. GPUs
        # ==========================================
        gpus = [
            {'name': 'Radeon RX 6500 XT', 'manufacturer': 'AMD', 'price': 160.00, 'performance_tier': 'Entry', 'vram_gb': 4, 'gpu_clock_speed': 2610},
            {'name': 'GeForce RTX 3060', 'manufacturer': 'NVIDIA', 'price': 350.00, 'performance_tier': 'Mid', 'vram_gb': 12, 'gpu_clock_speed': 1320},
            {'name': 'GeForce RTX 4070', 'manufacturer': 'NVIDIA', 'price': 600.00, 'performance_tier': 'Mid', 'vram_gb': 12, 'gpu_clock_speed': 1920},
            {'name': 'Radeon RX 7900 XTX', 'manufacturer': 'AMD', 'price': 999.00, 'performance_tier': 'High', 'vram_gb': 24, 'gpu_clock_speed': 2300},
            {'name': 'GeForce RTX 4090', 'manufacturer': 'NVIDIA', 'price': 1599.00, 'performance_tier': 'High', 'vram_gb': 24, 'gpu_clock_speed': 2230},
        ]

        for data in gpus:
            obj = GPU()
            # Parent fields
            obj.name = data['name']
            obj.manufacturer = data['manufacturer']
            obj.price = data['price']
            obj.performance_tier = data['performance_tier']
            # Child fields
            obj.vram_gb = data['vram_gb']
            obj.gpu_clock_speed = data['gpu_clock_speed']
            obj.save()
            self.stdout.write(f"Created GPU: {obj.name}")

        # ==========================================
        # 3. Motherboards
        # ==========================================
        mobos = [
            {'name': 'B660M DS3H', 'manufacturer': 'Gigabyte', 'price': 110.00, 'socket': 'LGA1700', 'form_factor': 'Micro-ATX', 'ram_slots': 4},
            {'name': 'B550 Tomahawk', 'manufacturer': 'MSI', 'price': 170.00, 'socket': 'AM4', 'form_factor': 'ATX', 'ram_slots': 4},
            {'name': 'X670E Hero', 'manufacturer': 'ASUS', 'price': 699.00, 'socket': 'AM5', 'form_factor': 'ATX', 'ram_slots': 4},
        ]
        for data in mobos:
            obj = Motherboard()
            # Parent fields
            obj.name = data['name']
            obj.manufacturer = data['manufacturer']
            obj.price = data['price']
            # Child fields
            obj.socket = data['socket']
            obj.form_factor = data['form_factor']
            obj.ram_slots = data['ram_slots']
            obj.save()
            self.stdout.write(f"Created Mobo: {obj.name}")

        # ==========================================
        # 4. RAM
        # ==========================================
        rams = [
            {'name': 'Vengeance LPX 16GB', 'manufacturer': 'Corsair', 'price': 50.00, 'capacity_gb': 16, 'speed_mhz': 3200},
            {'name': 'Trident Z5 32GB', 'manufacturer': 'G.Skill', 'price': 120.00, 'capacity_gb': 32, 'speed_mhz': 6000},
        ]
        for data in rams:
            obj = RAM()
            # Parent fields
            obj.name = data['name']
            obj.manufacturer = data['manufacturer']
            obj.price = data['price']
            # Child fields
            obj.capacity_gb = data['capacity_gb']
            obj.speed_mhz = data['speed_mhz']
            obj.save()
            self.stdout.write(f"Created RAM: {obj.name}")

        # ==========================================
        # 5. Storage
        # ==========================================
        storage_items = [
            {'name': '970 Evo Plus 1TB', 'manufacturer': 'Samsung', 'price': 60.00, 'capacity_gb': 1000, 'storage_type': 'NVMe'},
            {'name': 'Barracuda 2TB', 'manufacturer': 'Seagate', 'price': 50.00, 'capacity_gb': 2000, 'storage_type': 'HDD'},
        ]
        for data in storage_items:
            obj = Storage()
            # Parent fields
            obj.name = data['name']
            obj.manufacturer = data['manufacturer']
            obj.price = data['price']
            # Child fields
            obj.capacity_gb = data['capacity_gb']
            obj.storage_type = data['storage_type']
            obj.save()
            self.stdout.write(f"Created Storage: {obj.name}")

        # ==========================================
        # 6. PSUs
        # ==========================================
        psus = [
            {'name': 'CV650', 'manufacturer': 'Corsair', 'price': 60.00, 'wattage': 650, 'efficiency_rating': 'Bronze'},
            {'name': 'RM850x', 'manufacturer': 'Corsair', 'price': 130.00, 'wattage': 850, 'efficiency_rating': 'Gold'},
            {'name': 'Dark Power 13 1000W', 'manufacturer': 'be quiet!', 'price': 250.00, 'wattage': 1000, 'efficiency_rating': 'Titanium'},
        ]
        for data in psus:
            obj = PSU()
            # Parent fields
            obj.name = data['name']
            obj.manufacturer = data['manufacturer']
            obj.price = data['price']
            # Child fields
            obj.wattage = data['wattage']
            obj.efficiency_rating = data['efficiency_rating']
            obj.save()
            self.stdout.write(f"Created PSU: {obj.name}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with test components!'))

#__________________________________________________________________________________________________________________________