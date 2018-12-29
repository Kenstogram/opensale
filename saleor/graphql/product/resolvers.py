import graphene
import graphene_django_optimizer as gql_optimizer
from django.db.models import Q, Sum

from ...order import OrderStatus
from ...product import models
from ..utils import (
    filter_by_period, filter_by_query_param, get_database_id, get_nodes)
from .filters import (
    filter_products_by_attributes, filter_products_by_categories,
    filter_products_by_collections, filter_products_by_price, sort_qs)
from .types import Category, Collection, ProductVariant, StockAvailability

PRODUCT_SEARCH_FIELDS = ('name', 'description', 'category__name')
CATEGORY_SEARCH_FIELDS = ('name', 'slug', 'description', 'parent__name')
COLLECTION_SEARCH_FIELDS = ('name', 'slug')
ATTRIBUTES_SEARCH_FIELDS = ('name', 'slug')


def resolve_attributes(info, category_id, query):
    qs = models.Attribute.objects.all()
    qs = filter_by_query_param(qs, query, ATTRIBUTES_SEARCH_FIELDS)
    if category_id:
        # Get attributes that are used with product types
        # within the given category.
        category = graphene.Node.get_node_from_global_id(
            info, category_id, Category)
        if category is None:
            return qs.none()
        tree = category.get_descendants(include_self=True)
        product_types = {
            obj[0]
            for obj in models.Product.objects.filter(
                category__in=tree).values_list('product_type_id')}
        qs = qs.filter(
            Q(product_type__in=product_types)
            | Q(product_variant_type__in=product_types))
    qs = qs.order_by('name')
    qs = qs.distinct()
    return gql_optimizer.query(qs, info)


def resolve_categories(info, query, level=None):
    qs = models.Category.objects.prefetch_related('children')
    if level is not None:
        qs = qs.filter(level=level)
    qs = filter_by_query_param(qs, query, CATEGORY_SEARCH_FIELDS)
    qs = qs.order_by('name')
    qs = qs.distinct()
    return gql_optimizer.query(qs, info)


def resolve_collections(info, query):
    user = info.context.user
    qs = models.Collection.objects.visible_to_user(user)
    qs = filter_by_query_param(qs, query, COLLECTION_SEARCH_FIELDS)
    qs = qs.order_by('name')
    return gql_optimizer.query(qs, info)


def resolve_products(
        info, attributes=None, categories=None, collections=None,
        price_lte=None, price_gte=None, sort_by=None, stock_availability=None,
        query=None, **kwargs):

    user = info.context.user
    qs = models.Product.objects.visible_to_user(user)
    qs = filter_by_query_param(qs, query, PRODUCT_SEARCH_FIELDS)

    if attributes:
        qs = filter_products_by_attributes(qs, attributes)

    if categories:
        categories = get_nodes(categories, Category)
        qs = filter_products_by_categories(qs, categories)

    if collections:
        collections = get_nodes(collections, Collection)
        qs = filter_products_by_collections(qs, collections)

    if stock_availability:
        qs = qs.annotate(total_quantity=Sum('variants__quantity'))
        if stock_availability == StockAvailability.IN_STOCK:
            qs = qs.filter(total_quantity__gt=0)
        elif stock_availability == StockAvailability.OUT_OF_STOCK:
            qs = qs.filter(total_quantity__lte=0)

    qs = filter_products_by_price(qs, price_lte, price_gte)
    qs = sort_qs(qs, sort_by)
    qs = qs.distinct()
    return gql_optimizer.query(qs, info)


def resolve_product_types(info):
    qs = models.ProductType.objects.all()
    qs = qs.order_by('name')
    return gql_optimizer.query(qs, info)


def resolve_product_variants(info, ids=None):
    qs = models.ProductVariant.objects.all()
    if ids:
        db_ids = [
            get_database_id(info, node_id, only_type=ProductVariant)
            for node_id in ids]
        qs = qs.filter(pk__in=db_ids)
    return gql_optimizer.query(qs, info)


def resolve_report_product_sales(info, period):
    qs = models.ProductVariant.objects.prefetch_related(
        'product', 'product__images', 'order_lines__order').all()

    # exclude draft and canceled orders
    exclude_status = [OrderStatus.DRAFT, OrderStatus.CANCELED]
    qs = qs.exclude(order_lines__order__status__in=exclude_status)

    # filter by period
    qs = filter_by_period(qs, period, 'order_lines__order__created')

    qs = qs.annotate(quantity_ordered=Sum('order_lines__quantity'))
    qs = qs.filter(quantity_ordered__isnull=False)
    return qs.order_by('-quantity_ordered')
