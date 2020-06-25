from django.test import TestCase

from django.contrib.auth import get_user_model

from stock import models as stock_models


class StockModelsTests(TestCase):
    '''
    Test all models for stock application
    '''
    def setUp(self):
        '''
        Initiate all tests
        '''
        self.user = get_user_model().objects.create_user(
                                                username='xecus',
                                                first_name='Mohamed',
                                                last_name='Aboel-fotouh',
                                                password='Testpass123',)

    def test_create_category(self):
        '''
        Test creating a new category with minimum values
        '''
        stock_models.Category.objects.create(name='New category')

        self.assertEqual(stock_models.Category.objects.all().count(), 1)

    def test_create_item(self):
        '''
        Test creating a new item with minimum values
        '''
        category = stock_models.Category.objects.create(name='New category')

        location = stock_models.Location.objects.create(name='New location')

        sub_location = stock_models.SubLocation.objects.create(
                                        location=location,
                                        name='new sublocation' )

        stock_models.Item.objects.create(
                                        code='code',
                                        category=category,
                                        location=sub_location,
                                        price=50)

        self.assertEqual(stock_models.Item.objects.all().count(), 1)

    def test_create_assembly_item(self):
        '''
        Test creating a new item with minimum values
        '''
        category = stock_models.Category.objects.create(name='New category')

        location = stock_models.Location.objects.create(name='New location')

        sub_location = stock_models.SubLocation.objects.create(
                                        location=location,
                                        name='new sublocation' )

        item = stock_models.Item.objects.create(
                                        code='code',
                                        category=category,
                                        location=sub_location,
                                        price=50)

        assemblied_item = stock_models.Item.objects.create(
                                        code='assembly code',
                                        category=category,
                                        location=sub_location,
                                        price=50,
                                        is_assembly=True)

        stock_models.AssemblyItem.objects.create(
                                        item=assemblied_item,
                                        sub_item=item,
                                        quantity=5)

        self.assertEqual(stock_models.AssemblyItem.objects.all().count(), 1)

    def test_create_location(self):
        '''
        Test creating a new location with minimum values
        '''
        stock_models.Location.objects.create(name='New location')

        self.assertEqual(stock_models.Location.objects.all().count(), 1)

    def test_create_sublocation(self):
        '''
        Test creating a new sublocation with minimum values
        '''
        location = stock_models.Location.objects.create(name='New location')

        stock_models.SubLocation.objects.create(
                                        location=location,
                                        name='new sublocation' )

        self.assertEqual(stock_models.SubLocation.objects.all().count(), 1)

    def test_create_item_move(self):
        '''
        Test creating a new item move with minimum values
        '''
        category = stock_models.Category.objects.create(name='New category')

        location = stock_models.Location.objects.create(name='New location')

        sub_location = stock_models.SubLocation.objects.create(
                                        location=location,
                                        name='new sublocation' )

        item = stock_models.Item.objects.create(
                                        code='code',
                                        category=category,
                                        location=sub_location,
                                        price=50)

        stock_models.ItemMove.objects.create(
                                        item=item,
                                        location=sub_location,
                                        type=stock_models.ItemMove.ADD,
                                        related_to=stock_models.ItemMove.SELL,
                                        quantity=5 )

        self.assertEqual(stock_models.ItemMove.objects.all().count(), 1)

    def test_create_assembly_move(self):
        '''
        Test creating a new assembly move with minimum values
        '''
        category = stock_models.Category.objects.create(name='New category')

        location = stock_models.Location.objects.create(name='New location')

        sub_location = stock_models.SubLocation.objects.create(
                                    location=location,
                                    name='new sublocation' )

        sub_item = stock_models.Item.objects.create(
                                    code='code',
                                    category=category,
                                    location=sub_location,
                                    price=50)

        item = stock_models.Item.objects.create(
                                    code='Acode',
                                    category=category,
                                    location=sub_location,
                                    price=50,
                                    is_assembly=True)

        stock_models.AssemblyItem.objects.create(
                                    item=item,
                                    sub_item=sub_item,
                                    quantity=2)

        stock_models.ItemMove.objects.create(
                                    item=sub_item,
                                    location=sub_location,
                                    type=stock_models.ItemMove.ADD,
                                    related_to=stock_models.ItemMove.PURCHASE,
                                    quantity=50)

        stock_models.ItemMove.objects.create(
                                    item=item,
                                    location=sub_location,
                                    type=stock_models.ItemMove.REMOVE,
                                    related_to=stock_models.ItemMove.SELL,
                                    quantity=5)

        self.assertEqual(stock_models.AssemblyMove.objects.all().count(), 1)

    def test_create_item_transfer(self):
        '''
        Test creating item transfer with minimum values
        '''
        category = stock_models.Category.objects.create(name='New category')

        location = stock_models.Location.objects.create(name='New location')

        old_location = stock_models.SubLocation.objects.create(
                                    location=location,
                                    name='old sublocation' )

        item = stock_models.Item.objects.create(
                                    code='code',
                                    category=category,
                                    location=old_location,
                                    price=50)

        new_location = stock_models.SubLocation.objects.create(
                                    location=location,
                                    name='new sublocation' )

        item_move = stock_models.ItemMove.objects.create(
                                    item=item,
                                    location=old_location,
                                    type=stock_models.ItemMove.ADD,
                                    related_to=stock_models.ItemMove.PURCHASE,
                                    quantity=5 )

        remove_move = stock_models.ItemMove.objects.create(
                                    item=item,
                                    location=old_location,
                                    type=stock_models.ItemMove.REMOVE,
                                    related_to=stock_models.ItemMove.TRANSFER,
                                    quantity=5 )

        add_move = stock_models.ItemMove.objects.create(
                                    item=item,
                                    location=new_location,
                                    type=stock_models.ItemMove.ADD,
                                    related_to=stock_models.ItemMove.TRANSFER,
                                    quantity=5 )

        stock_models.ItemTransfer.objects.create(
                                    item=item,
                                    old_location=old_location,
                                    new_location=new_location,
                                    add_move = add_move,
                                    remove_move = remove_move)

        self.assertEqual(stock_models.ItemTransfer.objects.all().count(), 1)


class StockMethodsTests(TestCase):
    '''
    Test all models' methods
    '''
    def setUp(self):
        '''
        initiate all tests
        '''
        self.user = get_user_model().objects.create_user(
                                username='xecus',
                                first_name='Mohamed',
                                last_name='Aboel-fotouh',
                                password='Testpass123')

        self.category = stock_models.Category.objects.create(
                                name='New category')

        self.location = stock_models.Location.objects.create(
                                name='New location')

        self.sub_location = stock_models.SubLocation.objects.create(
                                location=self.location,
                                name='new sublocation')

        self.item = stock_models.Item.objects.create(
                                code='code',
                                category=self.category,
                                location=self.sub_location,
                                price=50)

        self.assembled_item = stock_models.Item.objects.create(
                                code='assembly code',
                                category=self.category,
                                location=self.sub_location,
                                price=50,
                                is_assembly=True)

        self.assembly_item = stock_models.AssemblyItem.objects.create(
                                item=self.assembled_item,
                                sub_item=self.item,
                                quantity=5)

        self.item_move = stock_models.ItemMove.objects.create(
                                item=self.item,
                                location=self.sub_location,
                                type=stock_models.ItemMove.ADD,
                                related_to=stock_models.ItemMove.PURCHASE,
                                quantity=20)

        self.assembled_item_move = stock_models.ItemMove.objects.create(
                                item=self.assembled_item,
                                location=self.sub_location,
                                type=stock_models.ItemMove.REMOVE,
                                related_to=stock_models.ItemMove.SELL,
                                quantity=1)

        self.sub_item_move = stock_models.ItemMove.objects.create(
                                item=self.assembly_item.sub_item,
                                location=self.sub_location,
                                type=stock_models.ItemMove.REMOVE,
                                related_to=stock_models.ItemMove.ASSEMBLY,
                                quantity=self.assembled_item_move.quantity \
                                        * self.assembly_item.quantity)

    def test_category_edit(self):
        '''
        Test edited method in category model
        '''
        self.category.edited(self.user)

        self.assertEqual(self.category.edited_by, self.user)

    def test_item_quantity(self):
        '''
        Test quantity property in Item model
        '''
        self.assertEqual(
                        self.assembled_item.quantity,
                        self.item.quantity / self.assembly_item.quantity)

    def test_item_edit(self):
        '''
        Test edited method in item model
        '''
        self.item.edited(self.user)

        self.assertEqual(self.item.edited_by, self.user)

    def test_assembly_item_sub_quantity(self):
        '''
        Test sub_item_quantity property in AssemblyItem model
        '''
        self.assertEqual(
                        self.assembly_item.sub_item_quantity,
                        self.item.quantity)

    def test_location_get_sub(self):
        '''
        Test get_sub_locations method in Location model
        '''
        self.assertEqual(
                        self.location.get_sub_locations()[0],
                        self.sub_location)

    def test_location_edit(self):
        '''
        Test edited method in location model
        '''
        self.location.edited(self.user)

        self.assertEqual(self.location.edited_by, self.user)

    def test_sub_location_get_items(self):
        '''
        Test get_items method in SubLocation model
        '''
        self.assertEqual(self.sub_location.get_items()[0], self.item)

    def test_sub_location_edit(self):
        '''
        Test edited method in SubLocation model
        '''
        self.sub_location.edited(self.user)

        self.assertEqual(self.sub_location.edited_by, self.user)

    def test_item_move_edit(self):
        '''
        Test edited method in ItemMove model
        '''
        self.item_move.edited(self.user)

        self.assertEqual(self.item_move.edited_by, self.user)
