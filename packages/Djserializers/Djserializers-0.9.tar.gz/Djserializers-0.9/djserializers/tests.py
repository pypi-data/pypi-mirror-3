from datetime import date
from decimal import Decimal

from django.db import models
from django.test import TestCase

from .annotated import serialize_model_annotated
from .base import serialize_model,  serialize_queryset
from .json_renderer import render_json, render_json_object_string, render_json_string
from .util import get_serialization_fields


# Foreign Key Relationship
class Catalog(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=150)

class Category(models.Model):
    catalog = models.ForeignKey("Catalog", related_name="categories")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=150)

class Product(models.Model):
    category = models.ForeignKey("Category", related_name="products")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    product_code = models.CharField(max_length=60)
    unit_price = models.DecimalField(max_digits=5, decimal_places=2, default="0.00")

    class Meta:
        ordering = ["product_code"]


# Many to Many Relationship
class Topping(models.Model):
    name = models.CharField(max_length=100)

class Pizza(models.Model):
    toppings = models.ManyToManyField(Topping)


# One to One Relationship
class Place(models.Model):
    name = models.CharField(max_length=100)

class Restaurant(models.Model):
    place = models.OneToOneField(Place)
    serves_pizza = models.BooleanField()

class Town(models.Model):
    place = models.OneToOneField(Place, primary_key=True)
    has_pizza = models.BooleanField()


# Natural Key
class PersonManager(models.Manager):

    def get_by_natural_key(self, first_name, last_name):
        return self.get(first_name=first_name, last_name=last_name)

class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField()

    objects = PersonManager()

    def natural_key(self):
        return (self.first_name, self.last_name)

    class Meta:
        unique_together = (('first_name', 'last_name'),)

class Book(models.Model):
    author = models.ForeignKey(Person)
    name = models.CharField(max_length=100)


# Many To Many Through

class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(Person, through='Membership')

class Membership(models.Model):
    person = models.ForeignKey(Person)
    group = models.ForeignKey(Group)


class SerializationFieldsTest(TestCase):

    def test_serialization_fields(self):
        # List all fields
        self.assertEqual(
            [f.name for f in get_serialization_fields(Product)],
            ['category', 'name', 'slug', 'product_code', 'unit_price'],
        )

        # List specific fields
        self.assertEqual(
            [f.name for f in get_serialization_fields(Product,
                fields=["category", "unit_price"])],
            ['category', 'unit_price'],
        )

        # List all fields except excluded
        self.assertEqual(
            [f.name for f in get_serialization_fields(Product,
                exclude=["category", "unit_price"])],
            ['name', 'slug', 'product_code'],
        )

        # Specify both fields and exclude.
        self.assertEqual(
            [f.name for f in get_serialization_fields(Product,
                fields=["category", "unit_price"],
                exclude=["category", "unit_price"])],
            [],
        )


class SerializerTest(TestCase):

    def test_serialize_model(self):
        catalog = Catalog.objects.create(
            name="Catalog",
            slug="catalog",
        )
        category = Category.objects.create(
            catalog=catalog,
            name="Category",
            slug="category",
        )
        product = Product.objects.create(
            category=category,
            name="Product",
            slug="product",
            product_code="1234",
            unit_price="1.00",
        )

        # Serialize a model
        self.assertEqual(serialize_model(product),
            {
                'category': category.pk,
                'product_code': '1234',
                'name': u'Product',
                'slug': u'product',
                'unit_price': '1.00',
            }
        )

        # Specify specific fields
        self.assertEqual(
            serialize_model(product, fields=["name", "slug"]),
            {
                'name': u'Product',
                'slug': u'product',
            },
        )

        # Specify fields with serialize set to False
        self.assertEqual(
            serialize_model(product, fields=["id"]),
            {
                'id': product.pk,
            },
        )

        # Exclude specific fields
        self.assertEqual(
            serialize_model(product, exclude=["name", "slug"]),
            {
                'category': category.pk,
                'product_code': '1234',
                'unit_price': '1.00',
            },
        )

        # Specify invalid field names
        self.assertEqual(
            serialize_model(product, fields=["invalid", ]),
            {},
        )

        # Specify relation
        self.assertEqual(
            serialize_model(product, related=["category"]),
            {
                'category': {
                    'catalog': catalog.pk,
                    'name': 'Category',
                    'slug': 'category',
                },
                'product_code': '1234',
                'name': u'Product',
                'slug': u'product',
                'unit_price': '1.00',
            }
        )

        # Specify relation fields
        self.assertEqual(
            serialize_model(
                product,
                related=["category"],
                related_fields={"category": ["name"]},
            ),
            {
                'category': {
                    'name': 'Category',
                },
                'product_code': '1234',
                'name': u'Product',
                'slug': u'product',
                'unit_price': '1.00',
            }
        )

        # Specify multi-level relation
        self.assertEqual(
            serialize_model(
                product,
                related=["category", "category__catalog"],
                related_fields={
                    "category": ["name", "catalog"],
                    "category__catalog": ["name"],
                },
            ),
            {
                'category': {
                    'name': 'Category',
                    'catalog': {
                        'name': u'Catalog',
                    },
                },
                'product_code': '1234',
                'name': u'Product',
                'slug': u'product',
                'unit_price': '1.00',
            }
        )

    def test_serialize_many_to_many(self):
        pizza = Pizza.objects.create()
        pizza.toppings.create(name="Bacon")
        pizza.toppings.create(name="Pineapple")

        self.assertEqual(
            serialize_model(pizza),
            {'toppings': [1, 2]}
        )

        self.assertEqual(
            serialize_model(pizza, related=["toppings"]),
            {'toppings': [{'name': u'Bacon'}, {'name': u'Pineapple'}]},
        )

    def test_serialize_many_to_many_through(self):
        person = Person.objects.create(
            first_name="Reginald",
            last_name="User",
            birthdate="1982-11-01",
        )

        group = Group.objects.create(
            name="The Bam Group",
        )

        membership = Membership.objects.create(
            person=person,
            group=group,
        )

        # Don't serialize manually created m2m fields by default
        self.assertEqual(
            serialize_model(Group.objects.get()),
            {
                'name': u'The Bam Group',
            }
        )

        # Do serialize if specified
        self.assertEqual(
            serialize_model(Group.objects.get(), fields=["name", "members"]),
            {
                'name': u'The Bam Group',
                'members': [membership.pk],
            }
        )

    def test_serialize_one_to_one(self):
        place = Place.objects.create(name="Dodgers")
        restaurant = Restaurant.objects.create(
            place=place,
            serves_pizza=True,
        )

        self.assertEqual(
            serialize_model(restaurant),
            {
                'serves_pizza': True,
                'place': place.pk,
            }
        )

        self.assertEqual(
            serialize_model(restaurant, related=["place"]),
            {
                'serves_pizza': True,
                'place': {
                    'name': u'Dodgers',
                 },
            }
        )

        # Check model with primary_key = True
        town = Town.objects.create(
            place=place,
            has_pizza=True,
        )

        self.assertEqual(
            serialize_model(town),
            {
                'has_pizza': True,
            }
        )

    def test_serialize_natural_key(self):
        Person.objects.create(
            first_name="Jacobim",
            last_name="User",
            birthdate="1980-11-01",
        )
        book = Book.objects.create(
            author=Person.objects.get(),
            name="Another Day, Another Pizza",
        )

        # Test natural key
        self.assertEqual(
            serialize_model(book, use_natural_keys=True),
            {
                'name': u'Another Day, Another Pizza',
                'author': (u'Jacobim', u'User'),
            },
        )

        # Test with relation specified
        self.assertEqual(
            serialize_model(book, related=["author"], use_natural_keys=True),
            {
                'name': u'Another Day, Another Pizza',
                'author': {
                    'first_name': u'Jacobim',
                    'last_name': u'User',
                    'birthdate': date(1980, 11, 1),
                },
            }
        )

    def test_serialize_queryset(self):
        catalog = Catalog.objects.create(
            name="Catalog",
            slug="catalog",
        )
        category = Category.objects.create(
            catalog=catalog,
            name="Category",
            slug="category",
        )
        Product.objects.create(
            category=category,
            name="Product",
            slug="product",
            product_code="1234",
            unit_price="1.00",
        )
        Product.objects.create(
            category=category,
            name="Product2",
            slug="product2",
            product_code="2",
            unit_price="2.00",
        )

        self.assertEqual(
            list(serialize_queryset(Product.objects.all())),
            [
                {
                    'category': category.pk,
                    'product_code': u'1234',
                    'name': u'Product',
                    'unit_price': Decimal('1.00'),
                    'slug': u'product',
                },
                {
                    'category': category.pk,
                    'product_code': u'2',
                    'name': u'Product2',
                    'unit_price': Decimal('2.00'),
                    'slug': u'product2',
                },
            ],
        )


class SerializeAnnotatedTest(TestCase):

    def test_serialize_model_annotated(self):
        catalog = Catalog.objects.create(
            name="Catalog",
            slug="catalog",
        )
        category = Category.objects.create(
            catalog=catalog,
            name="Category",
            slug="category",
        )
        product = Product.objects.create(
            category=category,
            name="Product",
            slug="product",
            product_code="1234",
            unit_price="1.00",
        )

        # Serialize a model
        self.assertEqual(serialize_model_annotated(product),
            {
                'pk': product.pk,
                'model': u'djserializers.product',
                'fields': {
                    'category': category.pk,
                    'product_code': u'1234',
                    'name': u'Product',
                    'slug': u'product',
                    'unit_price': '1.00',
                },
            }
        )

        self.assertEqual(
            serialize_model_annotated(product, related=["category"]),
            {
                'pk': product.pk,
                'model': u'djserializers.product',
                'fields': {
                    'category': {
                        'pk': category.pk,
                        'model': 'djserializers.category',
                        'fields': {
                            'catalog': catalog.pk,
                            'name': u'Category',
                            'slug': u'category',
                        },
                    },
                    'product_code': u'1234',
                    'name': u'Product',
                    'unit_price': u'1.00',
                    'slug': u'product',
                },
            }
        )


class JsonTest(TestCase):

    def test_render_json(self):
        catalog = Catalog.objects.create(
            name="Catalog",
            slug="catalog",
        )
        category = Category.objects.create(
            catalog=catalog,
            name="Category",
            slug="category",
        )
        Product.objects.create(
            category=category,
            name="Product",
            slug="product",
            product_code="1234",
            unit_price="1.00",
        )
        Product.objects.create(
            category=category,
            name="Product2",
            slug="product2",
            product_code="4321",
            unit_price="1.50",
        )

        # Render a model
        self.assertEqual(
            render_json(serialize_model(Product.objects.get(slug="product")), sort_keys=True),
            '{"category": 1, "name": "Product", "product_code": "1234", "slug": "product", "unit_price": "1"}'
        )

        # Render a queryset to string
        output = render_json_string(
            iterable=serialize_queryset(Product.objects.all()),
            sort_keys=True,
        )

        self.assertEqual(
            output,
            '[{"category": 1, "name": "Product", "product_code": "1234", "slug": "product", "unit_price": "1"}, {"category": 1, "name": "Product2", "product_code": "4321", "slug": "product2", "unit_price": "1.5"}]\n',
        )

        # Render a queryset as an object string
        output = render_json_object_string(
            iterable=serialize_queryset(Product.objects.all()),
            sort_keys=True,
        )

        self.assertEqual(
            output,
            '{"category": 1, "name": "Product", "product_code": "1234", "slug": "product", "unit_price": "1"}\n{"category": 1, "name": "Product2", "product_code": "4321", "slug": "product2", "unit_price": "1.5"}\n',
        )
