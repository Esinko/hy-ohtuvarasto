"""Warehouse model extending Varasto with name and item management."""
from varasto import Varasto


class Warehouse(Varasto):
    """A named warehouse that can store items with quantities."""

    def __init__(self, name, tilavuus, alku_saldo=0):
        super().__init__(tilavuus, alku_saldo)
        self.name = name
        self.items = {}  # item_name -> quantity

    def add_item(self, item_name, quantity):
        """Add an item to the warehouse.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        if quantity <= 0:
            return False, "Quantity must be positive"
        if quantity > self.paljonko_mahtuu():
            return False, "Not enough space in warehouse"

        self.lisaa_varastoon(quantity)
        if item_name in self.items:
            self.items[item_name] += quantity
        else:
            self.items[item_name] = quantity
        return True, None

    def remove_item(self, item_name, quantity=None):
        """Remove an item or reduce its quantity.

        Args:
            item_name: Name of the item to remove
            quantity: Amount to remove (None = remove all)

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        if item_name not in self.items:
            return False, "Item not found"

        if quantity is None:
            quantity = self.items[item_name]

        if quantity <= 0:
            return False, "Quantity must be positive"
        if quantity > self.items[item_name]:
            return False, "Not enough items to remove"

        self.ota_varastosta(quantity)
        self.items[item_name] -= quantity
        if self.items[item_name] == 0:
            del self.items[item_name]
        return True, None

    def get_item_count(self):
        """Get total number of unique items."""
        return len(self.items)

    def get_space_left_percent(self):
        """Get percentage of space left."""
        if self.tilavuus == 0:
            return 0
        return (self.paljonko_mahtuu() / self.tilavuus) * 100
