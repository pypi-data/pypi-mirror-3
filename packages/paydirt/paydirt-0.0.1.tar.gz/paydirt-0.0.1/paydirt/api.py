from decimal import Decimal, ROUND_UP

from suds.client import Client

from exceptions import PaymentsDirectFailure

CURRENCIES = {
    'AUD': ('Australian Dollar', 100),
    'CAD': ('Canadian Dollar', 100),
    'CHF': ('Swiss Franc', 100),
    'EUR': ('Euro', 100),
    'GBP': ('English Pound', 100),
    'HKD': ('Hong Kong Dollar', 100),
    'JPY': ('Japanese Yen', 1),
    'NZD': ('New Zealand Dollar', 100),
    'SGD': ('Singapore Dollar', 100),
    'USD': ('US Dollar', 100),
}


class API(object):

    ENDPOINT = 'https://cc.gw02.ctel.com.au/txn.asmx'

    def __init__(self, wsdl, merchant_id, username, password, currency="AUD", *args, **kwargs):
        self.merchant_id = merchant_id
        self.username = username
        self.password = password
        self.currency = currency
        self.minor = CURRENCIES[currency][1]
        self.client = Client(wsdl)
        self.client.set_options(location=self.ENDPOINT)

    def _perform_credit_card_transaction(self, txn, ref=None, card=None, expiry=None, cvv=None, name=None, amt=None, auth=None):
        assert card is not None
        assert expiry is not None
        assert isinstance(amt, Decimal)

        # Construct a complex request type.
        request = self.client.factory.create('PerformCreditCardTxn')

        # All transactions made with this instance of the API will
        # share the same authentication credentials, so these are
        # not arguments to the method.
        request.Merchant = self.merchant_id
        request.OperatorUsername = self.username
        request.OperatorPassword = self.password

        # Each type of transaction will have a simple wrapper to
        # this private method for simplicity.
        request.TxnType.value = txn

        # Specify the per transaction details, including adjusting
        # the amount as per the currency rules.
        request.CustomerReference = ref
        request.CardNumber = card
        request.CardExpiry = expiry
        request.CardCVV = cvv
        request.CardHolderName = name
        request.Amount = (amt*self.minor).to_integral(rounding=ROUND_UP)
        request.AuthorisationNumber = auth

        response = self.client.service.PerformCreditCardTxn(request)

        if not response.Successful:
            raise PaymentsDirectFailure(response)

        return dict(response)

    def payment(self, **kwargs):
        return self._perform_credit_card_transaction(txn='Payment', **kwargs)

    def refund(self, **kwargs):
        return self._perform_credit_card_transaction(txn='Refund', **kwargs)

    def preauthorisation(self, **kwargs):
        return self._perform_credit_card_transaction(txn='PreAuthorisation', **kwargs)

    def completion(self, auth=None, **kwargs):
        assert auth is not None
        return self._perform_credit_card_transaction(txn='Completion', auth=auth, **kwargs)


class TestAPI(API):

    ENDPOINT = 'https://ccdemo.gw02.ctel.com.au/txn.asmx'

    def payment(self, cvv='100', amt=Decimal('1.00'), **kwargs):
        # In test mode, use the last 2 digits of the cvv
        # as the decimal part of the amount, no matter
        # what the amt value passed in is. This allows us
        # to control the response code via the form.
        amt = amt.to_integral() + Decimal(cvv[-2:]) / 100

        defaults = {
            'ref': 'Python Test',
            'card': '4564000000000000',
            'expiry': '1107',
            'cvv': cvv,
            'name': 'Test Card',
            'amt': amt,
            }
        defaults.update(kwargs)
        return super(TestAPI, self).payment(**defaults)
