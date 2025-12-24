# catalog/models.py

#__________________________________________________________________________________________________________________________ (akn)

from django.db import models
from django.conf import settings

# ==============================================================================
# BASE COMPONENT MODEL
# This is the parent class containing all the common fields for every component.
# ==============================================================================
class Component(models.Model):
    name = models.CharField(max_length=500)
    manufacturer = models.CharField(max_length=255)
    image = models.URLField(max_length=1500, null=True, blank=True)
    tdp = models.PositiveIntegerField(null=True, blank=True, help_text="Thermal Design Power in Watts")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # === THIS IS THE MISSING PIECE ===
    TIER_CHOICES = [
        ('Entry', 'Entry-Level'),
        ('Mid', 'Mid-Range'),
        ('High', 'High-End'),
    ]
    performance_tier = models.CharField(
        max_length=10, 
        choices=TIER_CHOICES, 
        null=True, 
        blank=True,
        help_text="Performance tier for bottleneck calculations (primarily for CPU/GPU)"
    )
    # =================================

    def __str__(self):
        return f"{self.manufacturer} {self.name}"
    
    def get_type(self):
        """Returns the specific type of component (CPU, GPU, etc.)"""
        if hasattr(self, 'cpu'): return "CPU"
        if hasattr(self, 'gpu'): return "GPU"
        if hasattr(self, 'motherboard'): return "Motherboard"
        if hasattr(self, 'ram'): return "RAM"
        if hasattr(self, 'storage'): return "Storage"
        if hasattr(self, 'psu'): return "PSU"
        if hasattr(self, 'case'): return "Case"
        return "Component"


# ==============================================================================
# SPECIALIZED COMPONENT MODELS (CHILDREN)
# Each class below "inherits" from the Component class.
# This creates a new table for each component type (e.g., catalog_cpu)
# that is automatically linked one-to-one with the main catalog_component table.
# This is the Django implementation of our "is-a" specialization.
# ==============================================================================

class CPU(Component):
    core_count = models.PositiveIntegerField()
    clock_speed = models.CharField(max_length=30, help_text="Clock speed in GHz")
    socket = models.CharField(max_length=50)

class GPU(Component):
    vram_gb = models.CharField(max_length=7,help_text="VRAM in Gigabytes")
    gpu_clock_speed = models.CharField(max_length=20, help_text="Clock speed in MHz")

class Motherboard(Component):
    # Using 'choices' creates a dropdown menu in forms and the admin panel, ensuring data consistency.
    FORM_FACTOR_CHOICES = [
        ('ATX', 'ATX'),
        ('Micro-ATX', 'Micro-ATX'),
        ('Mini-ITX', 'Mini-ITX'),
    ]
    socket = models.CharField(max_length=50)
    form_factor = models.CharField(max_length=20, choices=FORM_FACTOR_CHOICES)
    ram_slots = models.PositiveIntegerField()

class RAM(Component):
    capacity_gb = models.CharField(max_length=20, help_text="Capacity per stick in Gigabytes")
    speed_mhz = models.CharField(max_length=20,help_text="Speed in MHz")

class Storage(Component):
    STORAGE_TYPE_CHOICES = [
        ('SSD', 'Solid State Drive'),
        ('NVMe', 'NVMe SSD'),
        ('HDD', 'Hard Disk Drive'),
    ]
    capacity_gb = models.CharField(max_length=10, help_text="Capacity in Gigabytes")
    storage_type = models.CharField(max_length=10, choices=STORAGE_TYPE_CHOICES)

class PSU(Component):
    EFFICIENCY_CHOICES = [
        ('80+', '80+'),
        ('Bronze', '80+ Bronze'),
        ('Silver', '80+ Silver'),
        ('Gold', '80+ Gold'),
        ('Platinum', '80+ Platinum'),
        ('Titanium', '80+ Titanium'),
    ]
    wattage = models.CharField(max_length=5, help_text="Wattage in Watts")
    efficiency_rating = models.CharField(max_length=20, choices=EFFICIENCY_CHOICES)

class Case(Component):
    # We can reuse the choices from the Motherboard model.
    form_factor = models.CharField(max_length=20, choices=Motherboard.FORM_FACTOR_CHOICES)
    max_gpu_length = models.CharField(max_length=5,help_text="Maximum GPU length in mm", null=True, blank=True)

# ==============================================================================
# REVIEW MODEL
# ==============================================================================
class Review(models.Model):
    # LOGIC: If User is deleted, keep the review but set user to NULL.
    # This requires null=True on the database field.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    # LOGIC: If Component is deleted, delete the review (Cascade).
    # related_name='reviews' allows us to easily get all reviews for a component 
    # (e.g., my_gpu.reviews.all())
    component = models.ForeignKey(
        Component, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )

    # Rating logic: We can enforce 1-5 stars using choices or validation.
    # Let's use choices for simplicity in the UI.
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    
    review_text = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        # LOGIC: "One review of one component can be written by only one user."
        # This constraint prevents a user from reviewing the same item twice.
        unique_together = ('user', 'component')

    def __str__(self):
        # Handle the case where user is None (deleted account)
        username = self.user.username if self.user else "Deleted User"
        return f"{self.rating} Stars for {self.component.name} by {username}"

# builds/models.py


    
#__________________________________________________________________________________________________________________________