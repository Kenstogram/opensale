from ..core.types.common import Error


def can_finalize_draft_order(order, errors):
    """Return a list of errors associated with the order.

    Checks, if given order has a proper customer data, shipping
    address and method set up and return list of errors if not.
    """
    if order.get_total_quantity() == 0:
        errors.append(
            Error(
                field='lines',
                message='Could not create order without any products.'))
    if order.is_shipping_required():
        method = order.shipping_method
        shipping_address = order.shipping_address
        shipping_not_valid = (
            method and shipping_address and
            shipping_address.country.code not in method.shipping_zone.countries)  # noqa
        if shipping_not_valid:
            errors.append(
                Error(
                    field='shipping',
                    message='Shipping method is not valid for chosen shipping '
                            'address'))
    return errors
