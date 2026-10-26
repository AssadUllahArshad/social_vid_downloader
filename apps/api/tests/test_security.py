import pytest

from app.providers import providers
from app.security import InvalidUrl, public_destination, validate_url


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "http://127.0.0.1/",
        "http://169.254.169.254/",
        "https://youtube.com.evil.test/watch",
        "https://evil.youtube.com/",
        "https://user:pass@youtube.com/watch",
        "https://youtube.com:8080/",
        "https://youtube.com%2eevil.test/",
        "https://youtube.com/ bad",
        "ftp://youtube.com/",
    ],
)
def test_restricted_urls(url):
    with pytest.raises(InvalidUrl):
        validate_url(url)


@pytest.mark.parametrize(
    "host,platform",
    [
        ("youtu.be", "youtube"),
        ("www.instagram.com", "instagram"),
        ("fb.watch", "facebook"),
        ("vm.tiktok.com", "tiktok"),
        ("snapchat.com", "snapchat"),
    ],
)
def test_detection(host, platform):
    normalized, detected = validate_url(f"https://{host}/media#fragment")
    assert detected == platform
    assert "#" not in normalized


@pytest.mark.parametrize("address", ["127.0.0.1", "10.0.0.1", "169.254.169.254", "::1", "fe80::1", "192.168.1.1"])
def test_private_dns(address):
    with pytest.raises(InvalidUrl):
        public_destination("https://youtube.com/watch", resolver=lambda *a, **kw: [(None, None, None, None, (address, 443))])


def test_capabilities_truthful():
    assert len(providers) == 6
    assert all(providers[p].capabilities.enabled for p in ["youtube", "facebook", "instagram", "tiktok"])
    assert providers["snapchat"].capabilities.enabled
    assert providers["snapchat"].capabilities.supportsSpotlight
    assert not providers["snapchat"].capabilities.supportsStories
    assert not providers["whatsapp"].capabilities.enabled
    assert not providers["instagram"].capabilities.supportsStories


def test_mixed_public_private_dns():
    def resolver(*args, **kwargs):
        return [(None, None, None, None, ("8.8.8.8", 443)), (None, None, None, None, ("10.0.0.1", 443))]

    with pytest.raises(InvalidUrl):
        public_destination("https://youtube.com/watch", resolver=resolver)
