import graphene
from graphql_jwt.decorators import permission_required

from ..core.fields import PrefetchingConnectionField
from ..descriptions import DESCRIPTIONS
from .mutations import (
    SaleCreate, SaleDelete, SaleUpdate, VoucherCreate, VoucherDelete,
    VoucherUpdate)
from .resolvers import resolve_sales, resolve_vouchers
from .types import Sale, Voucher


class DiscountQueries(graphene.ObjectType):
    sale = graphene.Field(
        Sale, id=graphene.Argument(graphene.ID, required=True),
        description='Lookup a sale by ID.')
    sales = PrefetchingConnectionField(
        Sale, query=graphene.String(description=DESCRIPTIONS['sale']),
        description="List of the shop\'s sales.")
    voucher = graphene.Field(
        Voucher, id=graphene.Argument(graphene.ID, required=True),
        description='Lookup a voucher by ID.')
    vouchers = PrefetchingConnectionField(
        Voucher, query=graphene.String(description=DESCRIPTIONS['product']),
        description="List of the shop\'s vouchers.")

    @permission_required('discount.manage_discounts')
    def resolve_sale(self, info, id):
        return graphene.Node.get_node_from_global_id(info, id, Sale)

    @permission_required('discount.manage_discounts')
    def resolve_sales(self, info, query=None, **kwargs):
        return resolve_sales(info, query)

    @permission_required('discount.manage_discounts')
    def resolve_voucher(self, info, id):
        return graphene.Node.get_node_from_global_id(info, id, Voucher)

    @permission_required('discount.manage_discounts')
    def resolve_vouchers(self, info, query=None, **kwargs):
        return resolve_vouchers(info, query)


class DiscountMutations(graphene.ObjectType):
    sale_create = SaleCreate.Field()
    sale_delete = SaleDelete.Field()
    sale_update = SaleUpdate.Field()

    voucher_create = VoucherCreate.Field()
    voucher_delete = VoucherDelete.Field()
    voucher_update = VoucherUpdate.Field()
