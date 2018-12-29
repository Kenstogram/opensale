import graphene
from django_countries import countries
from django_prices_vatlayer.models import VAT
from saleor.core.permissions import MODELS_PERMISSIONS
from saleor.graphql.core.utils import str_to_enum
from saleor.site import AuthenticationBackends
from saleor.site.models import Site
from tests.api.utils import get_graphql_content


def test_query_authorization_keys(
        authorization_key, staff_api_client, permission_manage_settings):
    query = """
    query {
        shop {
            authorizationKeys {
                name
                key
            }
        }
    }
    """
    response = staff_api_client.post_graphql(
        query, permissions=[permission_manage_settings])
    content = get_graphql_content(response)
    data = content['data']['shop']
    assert data['authorizationKeys'][0]['name'] == 'FACEBOOK'
    assert data['authorizationKeys'][0]['key'] == authorization_key.key


def test_query_countries(user_api_client):
    query = """
    query {
        shop {
            countries {
                code
                country
            }
        }
    }
    """
    response = user_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content['data']['shop']
    assert len(data['countries']) == len(countries)


def test_query_countries_with_tax(user_api_client, vatlayer, tax_rates):
    query = """
    query {
        shop {
            countries {
                code
                vat {
                    standardRate
                    reducedRates {
                        rate
                        rateType
                    }
                }
            }
        }
    }
    """
    response = user_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content['data']['shop']['countries']
    vat = VAT.objects.first()
    country = next(
        country for country in data if country['code'] == vat.country_code)
    assert country['vat']['standardRate'] == tax_rates['standard_rate']
    rates = {
        rate['rateType']: rate['rate']
        for rate in country['vat']['reducedRates']}
    assert rates == tax_rates['reduced_rates']


def test_query_default_country(user_api_client, settings):
    query = """
    query {
        shop {
            defaultCountry {
                country
            }
        }
    }
    """
    response = user_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content['data']['shop']['defaultCountry']
    assert data['country'] == settings.DEFAULT_COUNTRY


def test_query_default_country_with_tax(
        user_api_client, settings, vatlayer, tax_rates):
    settings.DEFAULT_COUNTRY = 'PL'
    query = """
    query {
        shop {
            defaultCountry {
                code
                vat {
                    standardRate
                }
            }
        }
    }
    """
    response = user_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content['data']['shop']['defaultCountry']
    assert data['code'] == settings.DEFAULT_COUNTRY
    assert data['vat']['standardRate'] == tax_rates['standard_rate']


def test_query_currencies(user_api_client, settings):
    query = """
    query {
        shop {
            currencies
            defaultCurrency
        }
    }
    """
    response = user_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content['data']['shop']
    assert len(data['currencies']) == len(settings.AVAILABLE_CURRENCIES)
    assert data['defaultCurrency'] == settings.DEFAULT_CURRENCY


def test_query_name(user_api_client, site_settings):
    query = """
    query {
        shop {
            name
            description
        }
    }
    """
    response = user_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content['data']['shop']
    assert data['description'] == site_settings.description
    assert data['name'] == site_settings.site.name


def test_query_domain(user_api_client, site_settings, settings):
    query = """
    query {
        shop {
            domain {
                host
                sslEnabled
                url
            }
        }
    }
    """
    response = user_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content['data']['shop']
    assert data['domain']['host'] == site_settings.site.domain
    assert data['domain']['sslEnabled'] == settings.ENABLE_SSL
    assert data['domain']['url']


def test_query_languages(settings, user_api_client):
    query = """
    query {
        shop {
            languages {
                code
                language
            }
        }
    }
    """
    response = user_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content['data']['shop']
    assert len(data['languages']) == len(settings.LANGUAGES)


def test_query_permissions(staff_api_client, permission_manage_users):
    query = """
    query {
        shop {
            permissions {
                code
                name
            }
        }
    }
    """
    response = staff_api_client.post_graphql(
        query, permissions=[permission_manage_users])
    content = get_graphql_content(response)
    data = content['data']['shop']
    permissions = data['permissions']
    permissions_codes = {permission.get('code') for permission in permissions}
    assert len(permissions_codes) == len(MODELS_PERMISSIONS)
    for code in permissions_codes:
        assert code in [
            str_to_enum(code.split('.')[1]) for code in MODELS_PERMISSIONS]


def test_query_navigation(user_api_client, site_settings):
    query = """
    query {
        shop {
            navigation {
                main {
                    name
                }
                secondary {
                    name
                }
            }
        }
    }
    """
    response = user_api_client.post_graphql(query)
    content = get_graphql_content(response)
    navigation_data = content['data']['shop']['navigation']
    assert navigation_data['main']['name'] == site_settings.top_menu.name
    assert navigation_data['secondary']['name'] == site_settings.bottom_menu.name


def test_shop_settings_mutation(
        staff_api_client, site_settings, permission_manage_settings):
    query = """
        mutation updateSettings($input: ShopSettingsInput!) {
            shopSettingsUpdate(input: $input) {
                shop {
                    headerText,
                    includeTaxesInPrices
                }
            }
        }
    """
    variables = {
        'input': {
            'includeTaxesInPrices': False,
            'headerText': 'Lorem ipsum'}}
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_settings])
    content = get_graphql_content(response)
    data = content['data']['shopSettingsUpdate']['shop']
    assert data['includeTaxesInPrices'] == False
    assert data['headerText'] == 'Lorem ipsum'
    site_settings.refresh_from_db()
    assert not site_settings.include_taxes_in_prices


def test_shop_domain_update(staff_api_client, permission_manage_settings):
    query = """
        mutation updateSettings($input: SiteDomainInput!) {
            shopDomainUpdate(input: $input) {
                shop {
                    name
                    domain {
                        host,
                    }
                }
            }
        }
    """
    new_name = 'saleor test store'
    variables = {
        'input': {
            'domain': 'lorem-ipsum.com',
            'name': new_name}}
    site = Site.objects.get_current()
    assert site.domain != 'lorem-ipsum.com'
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_settings])
    content = get_graphql_content(response)
    data = content['data']['shopDomainUpdate']['shop']
    assert data['domain']['host'] == 'lorem-ipsum.com'
    assert data['name'] == new_name
    site.refresh_from_db()
    assert site.domain == 'lorem-ipsum.com'
    assert site.name == new_name


def test_homepage_collection_update(
        staff_api_client, collection, permission_manage_settings):
    query = """
        mutation homepageCollectionUpdate($collection: ID!) {
            homepageCollectionUpdate(collection: $collection) {
                shop {
                    homepageCollection {
                        id,
                        name
                    }
                }
            }
        }
    """
    collection_id = graphene.Node.to_global_id('Collection', collection.id)
    variables = {'collection': collection_id}
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_settings])
    content = get_graphql_content(response)
    data = content['data']['homepageCollectionUpdate']['shop']
    assert data['homepageCollection']['id'] == collection_id
    assert data['homepageCollection']['name'] == collection.name
    site = Site.objects.get_current()
    assert site.settings.homepage_collection == collection


def test_homepage_collection_update_set_null(
        staff_api_client, collection, site_settings,
        permission_manage_settings):
    query = """
        mutation homepageCollectionUpdate($collection: ID) {
            homepageCollectionUpdate(collection: $collection) {
                shop {
                    homepageCollection {
                        id
                    }
                }
            }
        }
    """
    site_settings.homepage_collection = collection
    site_settings.save()
    variables = {'collection': None}
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_settings])
    content = get_graphql_content(response)
    data = content['data']['homepageCollectionUpdate']['shop']
    assert data['homepageCollection'] is None
    site_settings.refresh_from_db()
    assert site_settings.homepage_collection is None


def test_query_default_country(user_api_client, settings):
    settings.DEFAULT_COUNTRY = 'US'
    query = """
    query {
        shop {
            defaultCountry {
                code
                country
            }
        }
    }
    """
    response = user_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content['data']['shop']['defaultCountry']
    assert data['code'] == settings.DEFAULT_COUNTRY
    assert data['country'] == 'United States of America'


def test_query_geolocalization(user_api_client):
    query = """
        query {
            shop {
                geolocalization {
                    country {
                        code
                    }
                }
            }
        }
    """
    GERMAN_IP = '79.222.222.22'
    response = user_api_client.post_graphql(
        query, HTTP_X_FORWARDED_FOR=GERMAN_IP)
    content = get_graphql_content(response)
    data = content['data']['shop']['geolocalization']
    assert data['country']['code'] == 'DE'

    response = user_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content['data']['shop']['geolocalization']
    assert data['country'] is None


AUTHORIZATION_KEY_ADD = """
mutation AddKey($key: String!, $password: String!, $keyType: AuthorizationKeyType!) {
    authorizationKeyAdd(input: {key: $key, password: $password}, keyType: $keyType) {
        errors {
            field
            message
        }
        authorizationKey {
            name
            key
        }
    }
}
"""

def test_mutation_authorization_key_add_existing(
        staff_api_client, authorization_key, permission_manage_settings):

    # adding a key of type that already exists should return an error
    assert authorization_key.name == AuthenticationBackends.FACEBOOK
    variables = {'keyType': 'FACEBOOK', 'key': 'key', 'password': 'secret'}
    response = staff_api_client.post_graphql(
        AUTHORIZATION_KEY_ADD, variables,
        permissions=[permission_manage_settings])
    content = get_graphql_content(response)
    assert content['data']['authorizationKeyAdd']['errors'][0]['field'] == 'keyType'


def test_mutation_authorization_key_add(
        staff_api_client, permission_manage_settings):

    # mutation with correct input data should create a new key instance
    variables = {'keyType': 'FACEBOOK', 'key': 'key', 'password': 'secret'}
    response = staff_api_client.post_graphql(
        AUTHORIZATION_KEY_ADD, variables,
        permissions=[permission_manage_settings])
    content = get_graphql_content(response)
    assert content['data']['authorizationKeyAdd']['authorizationKey']['key'] == 'key'


def test_mutation_authorization_key_delete(
        staff_api_client, authorization_key, permission_manage_settings):

    query = """
    mutation DeleteKey($keyType: AuthorizationKeyType!) {
        authorizationKeyDelete(keyType: $keyType) {
            errors {
                field
                message
            }
            authorizationKey {
                name
                key
            }
        }
    }
    """

    assert authorization_key.name == AuthenticationBackends.FACEBOOK

    # deleting non-existing key should return an error
    variables = {'keyType': 'FACEBOOK'}
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_settings])
    content = get_graphql_content(response)
    assert content['data']['authorizationKeyDelete']['authorizationKey']
