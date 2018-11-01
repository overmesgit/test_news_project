from urllib.parse import urlparse


def get_normalize_url(url: str) -> str:
    """Url normalizer

    For more careful normalization check
    https://en.wikipedia.org/wiki/URL_normalization

    Parameters
    ----------
    url: str

    Returns
    -------
    str
        Normalized url
    """

    parsed_url = urlparse(url)
    return parsed_url.geturl()


def get_normalized_url_path(url: str) -> str:
    """Return normalized path of url without parameters

    Parameters
    ----------
    url

    Returns
    -------
    str
        Normalized path

    """
    parsed_url = urlparse(url)
    return parsed_url.path


def get_normalized_domain_name(url: str) -> str:
    """Return domain name of url without 'www.'

    Most of sites support request with www and without,
    to decrease ambiguous this function will remove www

    Parameters
    ----------
    url

    Returns
    -------
    str
        Normalized domain name
    """
    parsed_url = urlparse(url)
    normalized_domain_name = parsed_url.netloc
    if normalized_domain_name.startswith('www.'):
        normalized_domain_name = normalized_domain_name[4:]

    return normalized_domain_name
