import datetime
from unittest.mock import Mock, patch

import pytest

from django.urls import reverse
from django_countries.fields import Country
from freezegun import freeze_time
from prices import Money, TaxedMoney
from saleor.account.models import Address
from saleor.checkout import views
from saleor.checkout.forms import CartVoucherForm, CountryForm
from saleor.checkout.utils import (
    add_variant_to_cart, change_billing_address_in_cart,
    change_shipping_address_in_cart, clear_shipping_method, create_order,
    get_cart_data_for_checkout,
    get_prices_of_products_in_discounted_categories, get_taxes_for_cart,
    get_voucher_discount_for_cart, get_voucher_for_cart,
    is_valid_shipping_method, recalculate_cart_discount,
    remove_voucher_from_cart)
from saleor.core.exceptions import InsufficientStock
from saleor.core.utils.taxes import (
    ZERO_MONEY, ZERO_TAXED_MONEY, get_taxes_for_country)
from saleor.discount import DiscountValueType, VoucherType
from saleor.discount.models import NotApplicable, Voucher
from saleor.product.models import Category
from saleor.shipping.models import ShippingZone

from .utils import compare_taxes, get_redirect_location


def test_country_form_country_choices():
    form = CountryForm(data={'csrf': '', 'country': 'PL'})
    assert form.fields['country'].choices == []

    zone = ShippingZone.objects.create(countries=['PL', 'DE'], name='Europe')
    form = CountryForm(data={'csrf': '', 'country': 'PL'})

    expected_choices = [
        (country.code, country.name) for country in zone.countries]
    expected_choices = sorted(
        expected_choices, key=lambda choice: choice[1])
    assert form.fields['country'].choices == expected_choices


def test_is_valid_shipping_method(
        cart_with_item, address, shipping_zone, vatlayer):
    cart = cart_with_item
    cart.shipping_address = address
    cart.save()
    # no shipping method assigned
    assert not is_valid_shipping_method(cart, vatlayer, None)
    shipping_method = shipping_zone.shipping_methods.first()
    cart.shipping_method = shipping_method
    cart.save()

    assert is_valid_shipping_method(cart, vatlayer, None)

    zone = ShippingZone.objects.create(name='DE', countries=['DE'])
    shipping_method.shipping_zone = zone
    shipping_method.save()
    assert not is_valid_shipping_method(cart, vatlayer, None)


def test_clear_shipping_method(cart, shipping_method):
    cart.shipping_method = shipping_method
    cart.save()
    clear_shipping_method(cart)
    cart.refresh_from_db()
    assert not cart.shipping_method


@pytest.mark.parametrize('cart_length, is_shipping_required, redirect_url', [
    (0, True, reverse('cart:index')),
    (0, False, reverse('cart:index')),
    (1, True, reverse('checkout:shipping-address')),
    (1, False, reverse('checkout:summary'))])
def test_view_checkout_index(
        monkeypatch, rf, cart_length, is_shipping_required, redirect_url):
    cart = Mock(
        __len__=Mock(return_value=cart_length),
        is_shipping_required=Mock(return_value=is_shipping_required))
    monkeypatch.setattr(
        'saleor.checkout.utils.get_cart_from_request', lambda req, qs: cart)
    url = reverse('checkout:index')
    request = rf.get(url, follow=True)

    response = views.checkout_index(request)

    assert response.url == redirect_url


def test_view_checkout_index_authorized_user(
        authorized_client, customer_user, request_cart_with_item):
    request_cart_with_item.user = customer_user
    request_cart_with_item.save()
    url = reverse('checkout:index')

    response = authorized_client.get(url, follow=True)

    redirect_url = reverse('checkout:shipping-address')
    assert response.request['PATH_INFO'] == redirect_url


def test_view_checkout_shipping_address(client, request_cart_with_item):
    url = reverse('checkout:shipping-address')
    data = {
        'email': 'test@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'street_address_1': 'Aleje Jerozolimskie 2',
        'street_address_2': '',
        'city': 'Warszawa',
        'city_area': '',
        'country_area': '',
        'postal_code': '00-374',
        'phone': '+48536984008',
        'country': 'PL'}

    response = client.get(url)

    assert response.request['PATH_INFO'] == url

    response = client.post(url, data, follow=True)

    redirect_url = reverse('checkout:shipping-method')
    assert response.request['PATH_INFO'] == redirect_url
    assert request_cart_with_item.email == 'test@example.com'


def test_view_checkout_shipping_address_with_invalid_data(
        client, request_cart_with_item):
    url = reverse('checkout:shipping-address')
    data = {
        'email': 'test@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'street_address_1': 'Aleje Jerozolimskie 2',
        'street_address_2': '',
        'city': 'Warszawa',
        'city_area': '',
        'country_area': '',
        'postal_code': '00-37412',
        'phone': '+48536984008',
        'country': 'PL'}

    response = client.post(url, data, follow=True)
    assert response.request['PATH_INFO'] == url


def test_view_checkout_shipping_address_authorized_user(
        authorized_client, customer_user, request_cart_with_item):
    request_cart_with_item.user = customer_user
    request_cart_with_item.save()
    url = reverse('checkout:shipping-address')
    data = {'address': customer_user.default_billing_address.pk}

    response = authorized_client.post(url, data, follow=True)

    redirect_url = reverse('checkout:shipping-method')
    assert response.request['PATH_INFO'] == redirect_url
    assert request_cart_with_item.email == customer_user.email


def test_view_checkout_shipping_address_without_shipping(
        request_cart, product_without_shipping, client):
    variant = product_without_shipping.variants.get()
    add_variant_to_cart(request_cart, variant)
    url = reverse('checkout:shipping-address')

    response = client.get(url)

    assert response.status_code == 302
    assert get_redirect_location(response) == reverse('checkout:summary')
    assert not request_cart.email


def test_view_checkout_shipping_method(
        client, shipping_zone, address, request_cart_with_item):
    request_cart_with_item.shipping_address = address
    request_cart_with_item.email = 'test@example.com'
    request_cart_with_item.save()
    url = reverse('checkout:shipping-method')
    data = {'shipping_method': shipping_zone.shipping_methods.first().pk}

    response = client.get(url)

    assert response.request['PATH_INFO'] == url

    response = client.post(url, data, follow=True)

    redirect_url = reverse('checkout:summary')
    assert response.request['PATH_INFO'] == redirect_url


def test_view_checkout_shipping_method_authorized_user(
        authorized_client, customer_user, shipping_zone, address,
        request_cart_with_item):
    request_cart_with_item.user = customer_user
    request_cart_with_item.email = customer_user.email
    request_cart_with_item.shipping_address = address
    request_cart_with_item.save()
    url = reverse('checkout:shipping-method')
    data = {'shipping_method': shipping_zone.shipping_methods.first().pk}

    response = authorized_client.get(url)

    assert response.request['PATH_INFO'] == url

    response = authorized_client.post(url, data, follow=True)

    redirect_url = reverse('checkout:summary')
    assert response.request['PATH_INFO'] == redirect_url


def test_view_checkout_shipping_method_without_shipping(
        request_cart, product_without_shipping, client):
    variant = product_without_shipping.variants.get()
    add_variant_to_cart(request_cart, variant)
    url = reverse('checkout:shipping-method')

    response = client.get(url)

    assert response.status_code == 302
    assert get_redirect_location(response) == reverse('checkout:summary')


def test_view_checkout_shipping_method_without_address(
        request_cart_with_item, client):
    url = reverse('checkout:shipping-method')

    response = client.get(url)

    assert response.status_code == 302
    redirect_url = reverse('checkout:shipping-address')
    assert get_redirect_location(response) == redirect_url


@patch('saleor.checkout.views.summary.send_order_confirmation')
def test_view_checkout_summary(
        mock_send_confirmation, client, shipping_zone, address,
        request_cart_with_item):
    request_cart_with_item.shipping_address = address
    request_cart_with_item.email = 'test@example.com'
    request_cart_with_item.shipping_method = (
        shipping_zone.shipping_methods.first())
    request_cart_with_item.save()
    url = reverse('checkout:summary')
    data = {'address': 'shipping_address'}

    response = client.get(url)

    assert response.request['PATH_INFO'] == url

    response = client.post(url, data, follow=True)

    order = response.context['order']
    assert order.user_email == 'test@example.com'
    redirect_url = reverse('order:payment', kwargs={'token': order.token})
    assert response.request['PATH_INFO'] == redirect_url
    mock_send_confirmation.delay.assert_called_once_with(order.pk)


@patch('saleor.checkout.views.summary.send_order_confirmation')
def test_view_checkout_summary_authorized_user(
        mock_send_confirmation, authorized_client, customer_user,
        shipping_zone, address, request_cart_with_item):
    request_cart_with_item.shipping_address = address
    request_cart_with_item.user = customer_user
    request_cart_with_item.email = customer_user.email
    request_cart_with_item.shipping_method = (
        shipping_zone.shipping_methods.first())
    request_cart_with_item.save()
    url = reverse('checkout:summary')
    data = {'address': 'shipping_address'}

    response = authorized_client.get(url)

    assert response.request['PATH_INFO'] == url

    response = authorized_client.post(url, data, follow=True)

    order = response.context['order']
    assert order.user_email == customer_user.email
    redirect_url = reverse('order:payment', kwargs={'token': order.token})
    assert response.request['PATH_INFO'] == redirect_url
    mock_send_confirmation.delay.assert_called_once_with(order.pk)


@patch('saleor.checkout.views.summary.send_order_confirmation')
def test_view_checkout_summary_save_language(
        mock_send_confirmation, authorized_client, customer_user,
        shipping_zone, address, request_cart_with_item, settings):
    settings.LANGUAGE_CODE = 'en'
    user_language = 'fr'
    authorized_client.cookies[settings.LANGUAGE_COOKIE_NAME] = user_language
    url = reverse('set_language')
    data = {'language': 'fr'}

    authorized_client.post(url, data)

    request_cart_with_item.shipping_address = address
    request_cart_with_item.user = customer_user
    request_cart_with_item.email = customer_user.email
    request_cart_with_item.shipping_method = (
        shipping_zone.shipping_methods.first())
    request_cart_with_item.save()
    url = reverse('checkout:summary')
    data = {'address': 'shipping_address'}

    response = authorized_client.get(url, HTTP_ACCEPT_LANGUAGE=user_language)

    assert response.request['PATH_INFO'] == url

    response = authorized_client.post(
        url, data, follow=True, HTTP_ACCEPT_LANGUAGE=user_language)

    order = response.context['order']
    assert order.user_email == customer_user.email
    assert order.language_code == user_language
    redirect_url = reverse('order:payment', kwargs={'token': order.token})
    assert response.request['PATH_INFO'] == redirect_url
    mock_send_confirmation.delay.assert_called_once_with(order.pk)


def test_view_checkout_summary_without_address(request_cart_with_item, client):
    url = reverse('checkout:summary')

    response = client.get(url)

    assert response.status_code == 302
    redirect_url = reverse('checkout:shipping-address')
    assert get_redirect_location(response) == redirect_url


def test_view_checkout_summary_without_shipping_zone(
        request_cart_with_item, client, address):
    request_cart_with_item.shipping_address = address
    request_cart_with_item.email = 'test@example.com'
    request_cart_with_item.save()

    url = reverse('checkout:summary')
    response = client.get(url)

    assert response.status_code == 302
    redirect_url = reverse('checkout:shipping-method')
    assert get_redirect_location(response) == redirect_url


def test_view_checkout_summary_with_invalid_voucher(
        client, request_cart_with_item, shipping_zone, address, voucher):
    voucher.usage_limit = 3
    voucher.save()

    request_cart_with_item.shipping_address = address
    request_cart_with_item.email = 'test@example.com'
    request_cart_with_item.shipping_method = (
        shipping_zone.shipping_methods.first())
    request_cart_with_item.save()

    url = reverse('checkout:summary')
    voucher_url = '{url}?next={url}'.format(url=url)
    data = {'discount-voucher': voucher.code}

    response = client.post(voucher_url, data, follow=True, HTTP_REFERER=url)

    assert response.context['cart'].voucher_code == voucher.code

    voucher.used = 3
    voucher.save()

    data = {'address': 'shipping_address'}
    response = client.post(url, data, follow=True)
    cart = response.context['cart']
    assert not cart.voucher_code
    assert not cart.discount_amount
    assert not cart.discount_name

    response = client.post(url, data, follow=True)
    order = response.context['order']
    assert not order.voucher
    assert not order.discount_amount
    assert not order.discount_name


def test_view_checkout_summary_with_invalid_voucher_code(
        client, request_cart_with_item, shipping_zone, address):
    request_cart_with_item.shipping_address = address
    request_cart_with_item.email = 'test@example.com'
    request_cart_with_item.shipping_method = (
        shipping_zone.shipping_methods.first())
    request_cart_with_item.save()

    url = reverse('checkout:summary')
    voucher_url = '{url}?next={url}'.format(url=url)
    data = {'discount-voucher': 'invalid-code'}

    response = client.post(voucher_url, data, follow=True, HTTP_REFERER=url)

    assert 'voucher' in response.context['voucher_form'].errors
    assert response.context['cart'].voucher_code is None


def test_view_checkout_place_order_with_expired_voucher_code(
        client, request_cart_with_item, shipping_zone, address, voucher):

    cart = request_cart_with_item

    # add shipping information to the cart
    cart.shipping_address = address
    cart.email = 'test@example.com'
    cart.shipping_method = (
        shipping_zone.shipping_methods.first())

    # set voucher to be expired
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    voucher.end_date = yesterday
    voucher.save()

    # put the voucher code to cart
    cart.voucher_code = voucher.code

    # save the cart
    cart.save()

    checkout_url = reverse('checkout:summary')

    # place order
    data = {'address': 'shipping_address'}
    response = client.post(checkout_url, data, follow=True)

    # order should not have been placed
    assert response.request['PATH_INFO'] == checkout_url

    # ensure the voucher was removed
    cart.refresh_from_db()
    assert not cart.voucher_code


def test_view_checkout_place_order_with_item_out_of_stock(
        client, request_cart_with_item,
        shipping_zone, address, voucher, product):

    cart = request_cart_with_item
    variant = product.variants.get()

    # add shipping information to the cart
    cart.shipping_address = address
    cart.email = 'test@example.com'
    cart.shipping_method = shipping_zone.shipping_methods.first()
    cart.save()

    # make the variant be out of stock
    variant.quantity = 0
    variant.save()

    checkout_url = reverse('checkout:summary')
    redirect_url = reverse('cart:index')

    # place order
    data = {'address': 'shipping_address'}
    response = client.post(checkout_url, data, follow=True)

    # order should have been aborted,
    # and user should have been redirected to its cart
    assert response.request['PATH_INFO'] == redirect_url


def test_view_checkout_place_order_without_shipping_address(
        client, request_cart_with_item, shipping_zone):

    cart = request_cart_with_item

    # add shipping information to the cart
    cart.email = 'test@example.com'
    cart.shipping_method = (
        shipping_zone.shipping_methods.first())

    # save the cart
    cart.save()

    checkout_url = reverse('checkout:summary')
    redirect_url = reverse('checkout:shipping-address')

    # place order
    data = {'address': 'shipping_address'}
    response = client.post(checkout_url, data, follow=True)

    # order should have been aborted,
    # and user should have been redirected to its cart
    assert response.request['PATH_INFO'] == redirect_url


def test_view_checkout_summary_remove_voucher(
        client, request_cart_with_item, shipping_zone, voucher, address):
    request_cart_with_item.shipping_address = address
    request_cart_with_item.email = 'test@example.com'
    request_cart_with_item.shipping_method = (
        shipping_zone.shipping_methods.first())
    request_cart_with_item.save()

    remove_voucher_url = reverse('checkout:summary')
    voucher_url = '{url}?next={url}'.format(url=remove_voucher_url)
    data = {'discount-voucher': voucher.code}

    response = client.post(
        voucher_url, data, follow=True, HTTP_REFERER=remove_voucher_url)

    assert response.context['cart'].voucher_code == voucher.code

    url = reverse('checkout:remove-voucher')

    response = client.post(url, follow=True, HTTP_REFERER=remove_voucher_url)

    assert not response.context['cart'].voucher_code


def test_create_order_insufficient_stock(
        request_cart, customer_user, product_without_shipping):
    variant = product_without_shipping.variants.get()
    add_variant_to_cart(request_cart, variant, 10, check_quantity=False)
    request_cart.user = customer_user
    request_cart.billing_address = customer_user.default_billing_address
    request_cart.save()

    with pytest.raises(InsufficientStock):
        create_order(
            request_cart, 'tracking_code', discounts=None, taxes=None)


def test_note_in_created_order(request_cart_with_item, address):
    request_cart_with_item.shipping_address = address
    request_cart_with_item.note = 'test_note'
    request_cart_with_item.save()
    order = create_order(
        request_cart_with_item, 'tracking_code', discounts=None, taxes=None)
    assert order.customer_note == request_cart_with_item.note


@pytest.mark.parametrize(
    'total, discount_value, discount_type, min_amount_spent, discount_amount', [
        ('100', 10, DiscountValueType.FIXED, None, 10),
        ('100.05', 10, DiscountValueType.PERCENTAGE, 100, 10)])
def test_get_discount_for_cart_value_voucher(
        total, discount_value, discount_type, min_amount_spent,
        discount_amount):
    voucher = Voucher(
        code='unique',
        type=VoucherType.VALUE,
        discount_value_type=discount_type,
        discount_value=discount_value,
        min_amount_spent=(
            Money(min_amount_spent, 'USD')
            if min_amount_spent is not None else None))
    subtotal = TaxedMoney(net=Money(total, 'USD'), gross=Money(total, 'USD'))
    cart = Mock(get_subtotal=Mock(return_value=subtotal))
    discount = get_voucher_discount_for_cart(voucher, cart)
    assert discount == Money(discount_amount, 'USD')


def test_get_discount_for_cart_value_voucher_not_applicable():
    voucher = Voucher(
        code='unique',
        type=VoucherType.VALUE,
        discount_value_type=DiscountValueType.FIXED,
        discount_value=10,
        min_amount_spent=Money(100, 'USD'))
    subtotal = TaxedMoney(net=Money(10, 'USD'), gross=Money(10, 'USD'))
    cart = Mock(get_subtotal=Mock(return_value=subtotal))
    with pytest.raises(NotApplicable) as e:
        get_voucher_discount_for_cart(voucher, cart)
    assert e.value.min_amount_spent == Money(100, 'USD')


@pytest.mark.parametrize(
    'shipping_cost, shipping_country_code, discount_value, discount_type,'
    'countries, expected_value', [
        (10, None, 50, DiscountValueType.PERCENTAGE, [], 5),
        (10, None, 20, DiscountValueType.FIXED, [], 10),
        (10, 'PL', 20, DiscountValueType.FIXED, [], 10),
        (5, 'PL', 5, DiscountValueType.FIXED, ['PL'], 5)])
def test_get_discount_for_cart_shipping_voucher(
        shipping_cost, shipping_country_code, discount_value,
        discount_type, countries, expected_value):
    subtotal = TaxedMoney(net=Money(100, 'USD'), gross=Money(100, 'USD'))
    shipping_total = TaxedMoney(
        net=Money(shipping_cost, 'USD'), gross=Money(shipping_cost, 'USD'))
    cart = Mock(
        get_subtotal=Mock(return_value=subtotal),
        is_shipping_required=Mock(return_value=True),
        shipping_method=Mock(
            get_total=Mock(return_value=shipping_total)),
        shipping_address=Mock(country=Country(shipping_country_code)))
    voucher = Voucher(
        code='unique', type=VoucherType.SHIPPING,
        discount_value_type=discount_type,
        discount_value=discount_value,
        countries=countries)
    discount = get_voucher_discount_for_cart(voucher, cart)
    assert discount == Money(expected_value, 'USD')


@pytest.mark.parametrize(
    'is_shipping_required, shipping_method, discount_value, discount_type,'
    'countries, min_amount_spent, subtotal, error_msg', [
        (True, Mock(shipping_zone=Mock(countries=['PL'])),
         10, DiscountValueType.FIXED, ['US'], None, Money(10, 'USD'),
         'This offer is not valid in your country.'),
        (True, None, 10, DiscountValueType.FIXED,
         [], None, Money(10, 'USD'),
         'Please select a shipping method first.'),
        (False, None, 10, DiscountValueType.FIXED,
         [], None, Money(10, 'USD'),
         'Your order does not require shipping.'),
        (True, Mock(price=Money(10, 'USD')), 10,
         DiscountValueType.FIXED, [], 5, Money(2, 'USD'),
         'This offer is only valid for orders over $5.00.')])
def test_get_discount_for_cart_shipping_voucher_not_applicable(
        is_shipping_required, shipping_method, discount_value,
        discount_type, countries, min_amount_spent, subtotal, error_msg):
    subtotal_price = TaxedMoney(net=subtotal, gross=subtotal)
    cart = Mock(
        get_subtotal=Mock(return_value=subtotal_price),
        is_shipping_required=Mock(return_value=is_shipping_required),
        shipping_method=shipping_method)
    voucher = Voucher(
        code='unique', type=VoucherType.SHIPPING,
        discount_value_type=discount_type,
        discount_value=discount_value,
        min_amount_spent=(
            Money(min_amount_spent, 'USD')
            if min_amount_spent is not None else None),
        countries=countries)
    with pytest.raises(NotApplicable) as e:
        get_voucher_discount_for_cart(voucher, cart)
    assert str(e.value) == error_msg


def test_get_discount_for_cart_product_voucher_not_applicable(monkeypatch):
    monkeypatch.setattr(
        'saleor.checkout.utils.get_prices_of_discounted_products',
        lambda cart, product: [])
    voucher = Voucher(
        code='unique', type=VoucherType.PRODUCT,
        discount_value_type=DiscountValueType.FIXED,
        discount_value=10)
    voucher.save()
    cart = Mock()

    with pytest.raises(NotApplicable) as e:
        get_voucher_discount_for_cart(voucher, cart)
    assert str(e.value) == 'This offer is only valid for selected items.'


def test_get_discount_for_cart_collection_voucher_not_applicable(monkeypatch):
    monkeypatch.setattr(
        'saleor.checkout.utils.get_prices_of_products_in_discounted_collections',  # noqa
        lambda cart, product: [])
    voucher = Voucher(
        code='unique', type=VoucherType.COLLECTION,
        discount_value_type=DiscountValueType.FIXED,
        discount_value=10)
    voucher.save()
    cart = Mock()

    with pytest.raises(NotApplicable) as e:
        get_voucher_discount_for_cart(voucher, cart)
    assert str(e.value) == 'This offer is only valid for selected items.'


def test_cart_voucher_form_invalid_voucher_code(
        monkeypatch, request_cart_with_item):
    form = CartVoucherForm(
        {'voucher': 'invalid'}, instance=request_cart_with_item)
    assert not form.is_valid()
    assert 'voucher' in form.errors


def test_cart_voucher_form_voucher_not_applicable(
        voucher, request_cart_with_item):
    voucher.min_amount_spent = 200
    voucher.save()
    form = CartVoucherForm(
        {'voucher': voucher.code}, instance=request_cart_with_item)
    assert not form.is_valid()
    assert 'voucher' in form.errors


def test_cart_voucher_form_active_queryset_voucher_not_active(
        voucher, request_cart_with_item):
    assert Voucher.objects.count() == 1
    voucher.start_date = datetime.date.today() + datetime.timedelta(days=1)
    voucher.save()
    form = CartVoucherForm(
        {'voucher': voucher.code}, instance=request_cart_with_item)
    qs = form.fields['voucher'].queryset
    assert qs.count() == 0


def test_cart_voucher_form_active_queryset_voucher_active(
        voucher, request_cart_with_item):
    assert Voucher.objects.count() == 1
    voucher.start_date = datetime.date.today()
    voucher.save()
    form = CartVoucherForm(
        {'voucher': voucher.code}, instance=request_cart_with_item)
    qs = form.fields['voucher'].queryset
    assert qs.count() == 1


def test_cart_voucher_form_active_queryset_after_some_time(
        voucher, request_cart_with_item):
    assert Voucher.objects.count() == 1
    voucher.start_date = datetime.date(year=2016, month=6, day=1)
    voucher.end_date = datetime.date(year=2016, month=6, day=2)
    voucher.save()

    with freeze_time('2016-05-31'):
        form = CartVoucherForm(
            {'voucher': voucher.code}, instance=request_cart_with_item)
        assert form.fields['voucher'].queryset.count() == 0

    with freeze_time('2016-06-01'):
        form = CartVoucherForm(
            {'voucher': voucher.code}, instance=request_cart_with_item)
        assert form.fields['voucher'].queryset.count() == 1

    with freeze_time('2016-06-03'):
        form = CartVoucherForm(
            {'voucher': voucher.code}, instance=request_cart_with_item)
        assert form.fields['voucher'].queryset.count() == 0


def test_get_taxes_for_cart(cart, vatlayer):
    taxes = get_taxes_for_cart(cart, vatlayer)
    compare_taxes(taxes, vatlayer)


def test_get_taxes_for_cart_with_shipping_address(cart, address, vatlayer):
    address.country = 'DE'
    address.save()
    cart.shipping_address = address
    cart.save()
    taxes = get_taxes_for_cart(cart, vatlayer)
    compare_taxes(taxes, get_taxes_for_country(Country('DE')))


def test_get_taxes_for_cart_with_shipping_address_taxes_not_handled(
        cart, settings, address, vatlayer):
    settings.VATLAYER_ACCESS_KEY = ''
    address.country = 'DE'
    address.save()
    cart.shipping_address = address
    cart.save()
    assert not get_taxes_for_cart(cart, None)


def test_get_voucher_for_cart(cart_with_voucher, voucher):
    cart_voucher = get_voucher_for_cart(cart_with_voucher)
    assert cart_voucher == voucher


def test_get_voucher_for_cart_expired_voucher(cart_with_voucher, voucher):
    date_yesterday = datetime.date.today() - datetime.timedelta(days=1)
    voucher.end_date = date_yesterday
    voucher.save()
    cart_voucher = get_voucher_for_cart(cart_with_voucher)
    assert cart_voucher is None


def test_get_voucher_for_cart_no_voucher_code(cart):
    cart_voucher = get_voucher_for_cart(cart)
    assert cart_voucher is None


def test_remove_voucher_from_cart(cart_with_voucher, voucher_translation_fr):
    cart = cart_with_voucher
    remove_voucher_from_cart(cart)

    assert not cart.voucher_code
    assert not cart.discount_name
    assert not cart.translated_discount_name
    assert cart.discount_amount == ZERO_MONEY


def test_recalculate_cart_discount(
        cart_with_voucher, voucher, voucher_translation_fr, settings):
    settings.LANGUAGE_CODE = 'fr'
    voucher.discount_value = 10
    voucher.save()

    recalculate_cart_discount(cart_with_voucher, None, None)
    assert cart_with_voucher.translated_discount_name == voucher_translation_fr.name  # noqa
    assert cart_with_voucher.discount_amount == Money('10.00', 'USD')


def test_recalculate_cart_discount_voucher_not_applicable(
        cart_with_voucher, voucher):
    cart = cart_with_voucher
    voucher.min_amount_spent = 100
    voucher.save()

    recalculate_cart_discount(cart_with_voucher, None, None)

    assert not cart.voucher_code
    assert not cart.discount_name
    assert cart.discount_amount == ZERO_MONEY


def test_recalculate_cart_discount_expired_voucher(cart_with_voucher, voucher):
    cart = cart_with_voucher
    date_yesterday = datetime.date.today() - datetime.timedelta(days=1)
    voucher.end_date = date_yesterday
    voucher.save()

    recalculate_cart_discount(cart_with_voucher, None, None)

    assert not cart.voucher_code
    assert not cart.discount_name
    assert cart.discount_amount == ZERO_MONEY


def test_get_cart_data_for_checkout(cart_with_voucher, vatlayer):
    line_price = TaxedMoney(
        net=Money('24.39', 'USD'), gross=Money('30.00', 'USD'))
    expected_data = {
        'cart': cart_with_voucher,
        'cart_are_taxes_handled': True,
        'cart_lines': [(cart_with_voucher.lines.first(), line_price)],
        'cart_shipping_price': ZERO_TAXED_MONEY,
        'cart_subtotal': line_price,
        'cart_total': line_price - cart_with_voucher.discount_amount}

    data = get_cart_data_for_checkout(
        cart_with_voucher, discounts=None, taxes=vatlayer)

    assert data == expected_data


def test_change_address_in_cart(cart, address):
    change_shipping_address_in_cart(cart, address)
    change_billing_address_in_cart(cart, address)

    cart.refresh_from_db()
    assert cart.shipping_address == address
    assert cart.billing_address == address


def test_change_address_in_cart_to_none(cart, address):
    cart.shipping_address = address
    cart.billing_address = address.get_copy()
    cart.save()

    change_shipping_address_in_cart(cart, None)
    change_billing_address_in_cart(cart, None)

    cart.refresh_from_db()
    assert cart.shipping_address is None
    assert cart.billing_address is None


def test_change_address_in_cart_to_same(cart, address):
    cart.shipping_address = address
    cart.billing_address = address.get_copy()
    cart.save(update_fields=['shipping_address', 'billing_address'])
    shipping_address_id = cart.shipping_address.id
    billing_address_id = cart.billing_address.id

    change_shipping_address_in_cart(cart, address)
    change_billing_address_in_cart(cart, address)

    cart.refresh_from_db()
    assert cart.shipping_address.id == shipping_address_id
    assert cart.billing_address.id == billing_address_id


def test_change_address_in_cart_to_other(cart, address):
    address_id = address.id
    cart.shipping_address = address
    cart.billing_address = address.get_copy()
    cart.save(update_fields=['shipping_address', 'billing_address'])
    other_address = Address.objects.create(country=Country('DE'))

    change_shipping_address_in_cart(cart, other_address)
    change_billing_address_in_cart(cart, other_address)

    cart.refresh_from_db()
    assert cart.shipping_address == other_address
    assert cart.billing_address == other_address
    assert not Address.objects.filter(id=address_id).exists()


def test_change_address_in_cart_from_user_address_to_other(
        cart, customer_user, address):
    address_id = address.id
    cart.user = customer_user
    cart.shipping_address = address
    cart.billing_address = address.get_copy()
    cart.save(update_fields=['shipping_address', 'billing_address'])
    other_address = Address.objects.create(country=Country('DE'))

    change_shipping_address_in_cart(cart, other_address)
    change_billing_address_in_cart(cart, other_address)

    cart.refresh_from_db()
    assert cart.shipping_address == other_address
    assert cart.billing_address == other_address
    assert Address.objects.filter(id=address_id).exists()


def test_get_prices_of_products_in_discounted_categories(cart_with_item):
    lines = cart_with_item.lines.all()
    # There's no discounted categories, therefore all of them are discoutned
    discounted_lines = get_prices_of_products_in_discounted_categories(
        lines, [])
    assert [
        line.variant.get_price()
        for line in lines
        for item in range(line.quantity)] == discounted_lines

    discounted_category = Category.objects.create(
        name='discounted', slug='discounted')
    discounted_lines = get_prices_of_products_in_discounted_categories(
        lines, [discounted_category])
    # None of the lines are belongs to the discounted category
    assert not discounted_lines
