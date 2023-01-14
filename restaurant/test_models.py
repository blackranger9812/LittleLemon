from django.test import TestCase


from restaurant.models import MenuItem, Booking


class MenuItemTest(TestCase):
    def test_get_item(self):
        item = MenuItem.objects.create(
            title='IceCream', price=80)
        itemstr = item.get_item()
        self.assertEqual(itemstr, "IceCream : 80")

