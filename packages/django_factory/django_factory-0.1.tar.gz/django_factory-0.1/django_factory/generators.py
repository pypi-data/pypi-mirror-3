from decimal import Decimal


def generate_boolean(field, factory):
    """Generate a boolean.

    Always returns False.

    :returns: False
    """
    return False


def generate_unicode(field, factory):
    """Generate a unicode sting.

    :returns: a unique string starting with the field name.
    :return_type: unicode
    """
    return factory.getUniqueUnicode(prefix=field.name)


def generate_int(field, factory):
    """Generate an int.

    :returns: a unique integer.
    :return_type: int
    """
    return factory.getUniqueInteger()


def generate_float(field, factory):
    """Generate a float.

    :returns: a unique float.
    :return_type: float
    """
    return factory.getUniqueInteger() + 0.1


def generate_decimal(field, factory):
    """Generate a Decimal.

    :returns: a unique Decimal.
    :return_type: Decimal
    """
    return Decimal(factory.getUniqueInteger())


def generate_date(field, factory):
    """Generate a date.

    :returns: a unique datetime.date.
    :return_type: datetime.date
    """
    return factory.getUniqueDate()


def generate_datetime(field, factory):
    """Generate a datetime.

    :returns: a unique datetime.datetime.
    :return_type: datetime.datetime
    """
    return factory.getUniqueDateTime()


def generate_time(field, factory):
    """Generate a time.

    :returns: a unique datetime.time.
    :return_type: datetime.time
    """
    return factory.getUniqueTime()


def generate_url(field, factory):
    """Generate a url.

    :returns: a unique url.
    :return_type: unicode
    """
    return u"http://" + generate_unicode(field, factory)


def generate_email(field, factory):
    """Generate an email.

    :returns: a unique email.
    :return_type: unicode
    """
    return generate_unicode(field, factory) + '@' + generate_unicode(field, factory)


def generate_comma_separated_integer(field, factory):
    """Generate an comma separated integer string.

    :returns: a unique comma separated integer string.
    :return_type: str
    """
    return "%d" % generate_int(field, factory)


def generate_ip_address(field, factory):
    """Generate an IP address.

    :returns: a unique IP address.
    :return_type: str
    """
    parts = []
    for i in range(4):
        parts.append(str(generate_int(field, factory) % 256))
    return ".".join(parts)


def generate_generic_ip_address(field, factory):
    """Generate a generic IP address.

    :returns: a unique IPv6 address.
    :return_type: str
    """
    parts = []
    for i in range(2):
        parts.append("%x" % (generate_int(field, factory) % 256, ))
    return "::".join(parts)
