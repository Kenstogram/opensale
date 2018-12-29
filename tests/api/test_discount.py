import pytest

import graphene
from saleor.discount import DiscountValueType, VoucherType
from saleor.graphql.discount.types import (
    DiscountValueTypeEnum, VoucherTypeEnum)
from tests.api.utils import get_graphql_content


def test_voucher_query(staff_api_client, voucher, permission_manage_discounts):
    query = """
    query vouchers {
        vouchers(first: 1) {
            edges {
                node {
                    type
                    name
                    code
                    usageLimit
                    used
                    startDate
                    discountValueType
                    discountValue
                }
            }
        }
    }
    """
    response = staff_api_client.post_graphql(
        query, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['vouchers']['edges'][0]['node']
    assert data['type'] == voucher.type.upper()
    assert data['name'] == voucher.name
    assert data['code'] == voucher.code
    assert data['usageLimit'] == voucher.usage_limit
    assert data['used'] == voucher.used
    assert data['startDate'] == voucher.start_date.isoformat()
    assert data['discountValueType'] == voucher.discount_value_type.upper()
    assert data['discountValue'] == voucher.discount_value


def test_sale_query(staff_api_client, sale, permission_manage_discounts):
    query = """
        query sales {
            sales(first: 1) {
                edges {
                    node {
                        type
                        name
                        value
                        startDate
                    }
                }
            }
        }
        """
    response = staff_api_client.post_graphql(
        query, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['sales']['edges'][0]['node']
    assert data['type'] == sale.type.upper()
    assert data['name'] == sale.name
    assert data['value'] == sale.value
    assert data['startDate'] == sale.start_date.isoformat()


def test_create_voucher(staff_api_client, permission_manage_discounts):
    query = """
    mutation  voucherCreate(
        $type: VoucherTypeEnum, $name: String, $code: String,
        $discountValueType: DiscountValueTypeEnum,
        $discountValue: Decimal, $minAmountSpent: Decimal) {
            voucherCreate(input: {
            name: $name, type: $type, code: $code,
            discountValueType: $discountValueType, discountValue: $discountValue,
            minAmountSpent: $minAmountSpent}) {
                errors {
                    field
                    message
                }
                voucher {
                    type
                    minAmountSpent {
                        amount
                    }
                    name
                    code
                    discountValueType
                }
            }
        }
    """
    variables = {
        'name': 'test voucher',
        'type': VoucherTypeEnum.VALUE.name,
        'code': 'testcode123',
        'discountValueType': DiscountValueTypeEnum.FIXED.name,
        'discountValue': 10.12,
        'minAmountSpent': 1.12}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['voucherCreate']['voucher']
    assert data['type'] == VoucherType.VALUE.upper()
    assert data['minAmountSpent']['amount'] == 1.12
    assert data['name'] == 'test voucher'
    assert data['code'] == 'testcode123'
    assert data['discountValueType'] == DiscountValueType.FIXED.upper()


def test_update_voucher(
        staff_api_client, voucher, permission_manage_discounts):
    query = """
    mutation  voucherUpdate($code: String,
        $discountValueType: DiscountValueTypeEnum, $id: ID!) {
            voucherUpdate(id: $id, input: {
                code: $code, discountValueType: $discountValueType}) {
                errors {
                    field
                    message
                }
                voucher {
                    code
                    discountValueType
                }
            }
        }
    """
    # Set discount value type to 'fixed' and change it in mutation
    voucher.discount_value_type = DiscountValueType.FIXED
    voucher.save()
    assert voucher.code != 'testcode123'
    variables = {
        'id': graphene.Node.to_global_id('Voucher', voucher.id),
        'code': 'testcode123',
        'discountValueType': DiscountValueTypeEnum.PERCENTAGE.name}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['voucherUpdate']['voucher']
    assert data['code'] == 'testcode123'
    assert data['discountValueType'] == DiscountValueType.PERCENTAGE.upper()


def test_voucher_delete_mutation(
        staff_api_client, voucher, permission_manage_discounts):
    query = """
        mutation DeleteVoucher($id: ID!) {
            voucherDelete(id: $id) {
                voucher {
                    name
                    id
                }
                errors {
                    field
                    message
                }
              }
            }
    """
    variables = {'id': graphene.Node.to_global_id('Voucher', voucher.id)}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['voucherDelete']
    assert data['voucher']['name'] == voucher.name
    with pytest.raises(voucher._meta.model.DoesNotExist):
        voucher.refresh_from_db()


def test_create_sale(staff_api_client, permission_manage_discounts):
    query = """
    mutation  saleCreate(
        $type: DiscountValueTypeEnum, $name: String, $value: Decimal) {
            saleCreate(input: {name: $name, type: $type, value: $value}) {
                errors {
                    field
                    message
                }
                sale {
                    type
                    name
                    value
                }
            }
        }
    """
    variables = {
        'name': 'test sale',
        'type': DiscountValueTypeEnum.FIXED.name,
        'value': '10.12'}
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['saleCreate']['sale']
    assert data['type'] == DiscountValueType.FIXED.upper()
    assert data['name'] == 'test sale'
    assert data['value'] == 10.12


def test_update_sale(staff_api_client, sale, permission_manage_discounts):
    query = """
    mutation  saleUpdate($type: DiscountValueTypeEnum, $id: ID!) {
            saleUpdate(id: $id, input: {type: $type}) {
                errors {
                    field
                    message
                }
                sale {
                    type
                }
            }
        }
    """
    # Set discount value type to 'fixed' and change it in mutation
    sale.type = DiscountValueType.FIXED
    sale.save()
    variables = {
        'id': graphene.Node.to_global_id('Sale', sale.id),
        'type': DiscountValueTypeEnum.PERCENTAGE.name}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['saleUpdate']['sale']
    assert data['type'] == DiscountValueType.PERCENTAGE.upper()


def test_sale_delete_mutation(
        staff_api_client, sale, permission_manage_discounts):
    query = """
        mutation DeleteSale($id: ID!) {
            saleDelete(id: $id) {
                sale {
                    name
                    id
                }
                errors {
                    field
                    message
                }
              }
            }
    """
    variables = {'id': graphene.Node.to_global_id('Sale', sale.id)}

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_discounts])
    content = get_graphql_content(response)
    data = content['data']['saleDelete']
    assert data['sale']['name'] == sale.name
    with pytest.raises(sale._meta.model.DoesNotExist):
        sale.refresh_from_db()


def test_validate_voucher(
        voucher, staff_api_client, permission_manage_discounts):
    query = """
    mutation  voucherUpdate(
        $id: ID!, $type: VoucherTypeEnum) {
            voucherUpdate(
            id: $id, input: {type: $type}) {
                errors {
                    field
                    message
                }
            }
        }
    """
    # apparently can't do so via pytest parametrize
    # as it parses VoucherTypeEnum into str format
    fields = (
        (VoucherTypeEnum.CATEGORY, 'categories'),
        (VoucherTypeEnum.PRODUCT, 'products'),
        (VoucherTypeEnum.COLLECTION, 'collections'))
    staff_api_client.user.user_permissions.add(permission_manage_discounts)
    for voucher_type, field_name in fields:
        variables = {
            'type': voucher_type.name,
            'id': graphene.Node.to_global_id('Voucher', voucher.id)}
        response = staff_api_client.post_graphql(query, variables)
        content = get_graphql_content(response)
        data = content['data']['voucherUpdate']['errors'][0]
        assert data['field'] == field_name
        assert data['message'] == 'This field is required.'
