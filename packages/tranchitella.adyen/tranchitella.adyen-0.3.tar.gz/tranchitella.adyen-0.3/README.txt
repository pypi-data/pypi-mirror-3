tranchitella.adyen
==================

This package offers a Python interface to the Adyen payment gateway.

Usage
-----

Create a new ``AdyenPaymentGateway`` object:

    >>> from tranchitella.adyen import AdyenPaymentGateway
    >>> obj = AdyenPaymentGateway(
    ...     url='https://pal-test.adyen.com/pal/servlet/soap/Payment',
    ...     user='ws@Company.YourCompany', password='YourPassword',
    ...     merchantAccount='MerchantAccount',
    ... )

Authorise a transaction:

    >>> obj.authorise('T-1', 100, 'EUR', 'FABIO TRANCHITELLA',
    ...     '5555444433331111', '12', '2012', '737', ipAddress='127.0.0.1')
    {'authCode': ... }

Cancel a transaction:

    >>> print obj.cancel('8112083591854919')
    True

Capture a transaction:

    >>> print obj.capture('8112083586124880', 100, 'EUR')
    True

Refund a transaction:

    >>> print obj.refund('8112083586124880', 100, 'EUR')
    True
