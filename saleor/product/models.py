import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.text import slugify
from django.utils.translation import pgettext_lazy
from django_measurement.models import MeasurementField
from django_prices.models import MoneyField
from django_prices.templatetags import prices_i18n
from measurement.measures import Weight
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from prices import TaxedMoneyRange
from text_unidecode import unidecode
from versatileimagefield.fields import PPOIField, VersatileImageField

from ..core import TaxRateType
from ..core.exceptions import InsufficientStock
from ..core.models import SortableModel
from ..core.utils.taxes import DEFAULT_TAX_RATE_NAME, apply_tax_to_price
from ..core.utils.translations import TranslationProxy
from ..core.weight import WeightUnits, zero_weight
from ..discount.utils import calculate_discounted_price
from ..seo.models import SeoModel, SeoModelTranslation


class Category(MPTTModel, SeoModel):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children',
        on_delete=models.CASCADE)
    background_image = VersatileImageField(
        upload_to='category-backgrounds', blank=True, null=True)

    objects = models.Manager()
    tree = TreeManager()
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'product:category',
            kwargs={'slug': self.slug, 'category_id': self.id})


class CategoryTranslation(SeoModelTranslation):
    language_code = models.CharField(max_length=10)
    category = models.ForeignKey(
        Category, related_name='translations', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = (('language_code', 'category'),)

    def __str__(self):
        return self.name

    def __repr__(self):
        class_ = type(self)
        return '%s(pk=%r, name=%r, category_pk=%r)' % (
            class_.__name__, self.pk, self.name, self.category_id)


class ProductType(models.Model):
    name = models.CharField(max_length=128)
    has_variants = models.BooleanField(default=True)
    is_shipping_required = models.BooleanField(default=False)
    tax_rate = models.CharField(
        max_length=128, default=DEFAULT_TAX_RATE_NAME,
        choices=TaxRateType.CHOICES)
    weight = MeasurementField(
        measurement=Weight, unit_choices=WeightUnits.CHOICES,
        default=zero_weight)

    class Meta:
        app_label = 'product'

    def __str__(self):
        return self.name

    def __repr__(self):
        class_ = type(self)
        return '<%s.%s(pk=%r, name=%r)>' % (
            class_.__module__, class_.__name__, self.pk, self.name)


class ProductQuerySet(models.QuerySet):

    def available_products(self):
        today = datetime.date.today()
        return self.filter(
            Q(available_on__lte=today) | Q(available_on__isnull=True),
            Q(is_published=True))

    def visible_to_user(self, user):
        has_access_to_all = (
            user.is_active and user.has_perm('product.manage_products'))
        if has_access_to_all:
            return self.all()
        return self.available_products()


class Product(SeoModel):
    product_type = models.ForeignKey(
        ProductType, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField()
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.CASCADE)
    price = MoneyField(
        currency=settings.DEFAULT_CURRENCY,
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES)
    available_on = models.DateField(blank=True, null=True)
    is_published = models.BooleanField(default=True)
    attributes = HStoreField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    charge_taxes = models.BooleanField(default=True)
    tax_rate = models.CharField(
        max_length=128, default=DEFAULT_TAX_RATE_NAME, blank=True)
    weight = MeasurementField(
        measurement=Weight, unit_choices=WeightUnits.CHOICES,
        blank=True, null=True)

    objects = ProductQuerySet.as_manager()
    translated = TranslationProxy()

    class Meta:
        app_label = 'product'
        permissions = ((
            'manage_products', pgettext_lazy(
                'Permission description',
                'Manage products.')),)

    def __iter__(self):
        if not hasattr(self, '__variants'):
            setattr(self, '__variants', self.variants.all())
        return iter(getattr(self, '__variants'))

    def __repr__(self):
        class_ = type(self)
        return '<%s.%s(pk=%r, name=%r)>' % (
            class_.__module__, class_.__name__, self.pk, self.name)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'product:details',
            kwargs={'slug': self.get_slug(), 'product_id': self.id})

    def get_slug(self):
        return slugify(smart_text(unidecode(self.name)))

    def is_in_stock(self):
        return any(variant.is_in_stock() for variant in self)

    def is_available(self):
        today = datetime.date.today()
        return self.available_on is None or self.available_on <= today

    def get_first_image(self):
        images = list(self.images.all())
        return images[0].image if images else None

    def get_price_range(self, discounts=None, taxes=None):
        if self.variants.all():
            prices = [
                variant.get_price(discounts=discounts, taxes=taxes)
                for variant in self]
            return TaxedMoneyRange(min(prices), max(prices))
        price = calculate_discounted_price(self, self.price, discounts)
        if not self.charge_taxes:
            taxes = None
        tax_rate = self.tax_rate or self.product_type.tax_rate
        price = apply_tax_to_price(taxes, tax_rate, price)
        return TaxedMoneyRange(start=price, stop=price)


class ProductTranslation(SeoModelTranslation):
    language_code = models.CharField(max_length=10)
    product = models.ForeignKey(
        Product, related_name='translations', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField()

    class Meta:
        unique_together = (('language_code', 'product'),)

    def __str__(self):
        return self.name

    def __repr__(self):
        class_ = type(self)
        return '%s(pk=%r, name=%r, product_pk=%r)' % (
            class_.__name__, self.pk, self.name, self.product_id)


class ProductVariant(models.Model):
    sku = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255, blank=True)
    price_override = MoneyField(
        currency=settings.DEFAULT_CURRENCY,
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES, blank=True, null=True)
    product = models.ForeignKey(
        Product, related_name='variants', on_delete=models.CASCADE)
    attributes = HStoreField(default=dict, blank=True)
    images = models.ManyToManyField('ProductImage', through='VariantImage')
    track_inventory = models.BooleanField(default=True)
    quantity = models.IntegerField(
        validators=[MinValueValidator(0)], default=Decimal(1))
    quantity_allocated = models.IntegerField(
        validators=[MinValueValidator(0)], default=Decimal(0))
    cost_price = MoneyField(
        currency=settings.DEFAULT_CURRENCY,
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES, blank=True, null=True)
    weight = MeasurementField(
        measurement=Weight, unit_choices=WeightUnits.CHOICES,
        blank=True, null=True)
    translated = TranslationProxy()

    class Meta:
        app_label = 'product'

    def __str__(self):
        return self.name or self.sku

    @property
    def quantity_available(self):
        return max(self.quantity - self.quantity_allocated, 0)

    def check_quantity(self, quantity):
        """Check if there is at least the given quantity in stock
        if stock handling is enabled.
        """
        if self.track_inventory and quantity > self.quantity_available:
            raise InsufficientStock(self)

    @property
    def base_price(self):
        return self.price_override or self.product.price

    def get_price(self, discounts=None, taxes=None):
        price = calculate_discounted_price(
            self.product, self.base_price, discounts)
        if not self.product.charge_taxes:
            taxes = None
        tax_rate = (
            self.product.tax_rate or self.product.product_type.tax_rate)
        return apply_tax_to_price(taxes, tax_rate, price)

    def get_weight(self):
        return (
            self.weight or self.product.weight or
            self.product.product_type.weight)

    def get_absolute_url(self):
        slug = self.product.get_slug()
        product_id = self.product.id
        return reverse('product:details',
                       kwargs={'slug': slug, 'product_id': product_id})

    def is_shipping_required(self):
        return self.product.product_type.is_shipping_required

    def is_in_stock(self):
        return self.quantity_available > 0

    def display_product(self, translated=False):
        if translated:
            product = self.product.translated
            variant_display = str(self.translated)
        else:
            variant_display = str(self)
            product = self.product
        product_display = (
            '%s (%s)' % (product, variant_display)
            if variant_display else str(product))
        return smart_text(product_display)

    def get_first_image(self):
        images = list(self.images.all())
        if images:
            return images[0].image
        return self.product.get_first_image()

    def get_ajax_label(self, discounts=None):
        price = self.get_price(discounts).gross
        return '%s, %s, %s' % (
            self.sku, self.display_product(), prices_i18n.amount(price))


class ProductVariantTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    product_variant = models.ForeignKey(
        ProductVariant, related_name='translations', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)

    translated = TranslationProxy()

    class Meta:
        unique_together = (('language_code', 'product_variant'),)

    def __repr__(self):
        class_ = type(self)
        return '%s(pk=%r, name=%r, variant_pk=%r)' % (
            class_.__name__, self.pk, self.name, self.product_variant_id)

    def __str__(self):
        return self.name or str(self.product_variant)


class Attribute(models.Model):
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=50)
    product_type = models.ForeignKey(
        ProductType, related_name='product_attributes', blank=True,
        null=True, on_delete=models.CASCADE)
    product_variant_type = models.ForeignKey(
        ProductType, related_name='variant_attributes', blank=True,
        null=True, on_delete=models.CASCADE)

    translated = TranslationProxy()

    class Meta:
        ordering = ('slug', )

    def __str__(self):
        return self.name

    def get_formfield_name(self):
        return slugify('attribute-%s' % self.slug, allow_unicode=True)

    def has_values(self):
        return self.values.exists()


class AttributeTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    attribute = models.ForeignKey(
        Attribute, related_name='translations',
        on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = (('language_code', 'attribute'),)

    def __repr__(self):
        class_ = type(self)
        return '%s(pk=%r, name=%r, attribute_pk=%r)' % (
            class_.__name__, self.pk, self.name, self.attribute_id)

    def __str__(self):
        return self.name


class AttributeValue(SortableModel):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100, blank=True, default='')
    slug = models.SlugField(max_length=100)
    attribute = models.ForeignKey(
        Attribute, related_name='values', on_delete=models.CASCADE)

    translated = TranslationProxy()

    class Meta:
        ordering = ('sort_order',)
        unique_together = ('name', 'attribute')

    def __str__(self):
        return self.name

    def get_ordering_queryset(self):
        return self.attribute.values.all()


class AttributeValueTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    attribute_value = models.ForeignKey(
        AttributeValue, related_name='translations',
        on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = (('language_code', 'attribute_value'),)

    def __repr__(self):
        class_ = type(self)
        return '%s(pk=%r, name=%r, attribute_value_pk=%r)' % (
            class_.__name__, self.pk, self.name,
            self.attribute_value_id)

    def __str__(self):
        return self.name


class ProductImage(SortableModel):
    product = models.ForeignKey(
        Product, related_name='images', on_delete=models.CASCADE)
    image = VersatileImageField(
        upload_to='products', ppoi_field='ppoi', blank=False)
    ppoi = PPOIField()
    alt = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ('sort_order', )
        app_label = 'product'

    def get_ordering_queryset(self):
        return self.product.images.all()


class VariantImage(models.Model):
    variant = models.ForeignKey(
        'ProductVariant', related_name='variant_images',
        on_delete=models.CASCADE)
    image = models.ForeignKey(
        ProductImage, related_name='variant_images', on_delete=models.CASCADE)


class CollectionQuerySet(models.QuerySet):

    def public(self):
        return self.filter(is_published=True)

    def visible_to_user(self, user):
        has_access_to_all = (
            user.is_active and user.has_perm('product.manage_products'))
        if has_access_to_all:
            return self.all()
        return self.public()


class Collection(SeoModel):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128)
    products = models.ManyToManyField(
        Product, blank=True, related_name='collections')
    background_image = VersatileImageField(
        upload_to='collection-backgrounds', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    objects = CollectionQuerySet.as_manager()
    translated = TranslationProxy()

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'product:collection',
            kwargs={'pk': self.id, 'slug': self.slug})


class CollectionTranslation(SeoModelTranslation):
    language_code = models.CharField(max_length=10)
    collection = models.ForeignKey(
        Collection, related_name='translations',
        on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = (('language_code', 'collection'),)

    def __repr__(self):
        class_ = type(self)
        return '%s(pk=%r, name=%r, collection_pk=%r)' % (
            class_.__name__, self.pk, self.name, self.collection_id)

    def __str__(self):
        return self.name
