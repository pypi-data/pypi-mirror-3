# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import time
import hashlib
from contextlib import contextmanager

from browserid.utils import encode_bytes, bundle_certs_and_assertion

from browserid import certificates
from browserid import jwt
from browserid.verifiers import remote

# These are values used to generate dummy DSA keys.
# I took them directly from the javacript jwcrypto source code, which claims:
#    """
#    the following are based on the first FIPS186-3 test vectors for 1024/160
#    SHA-256 under the category A.2.3 Verifiable Canonical Generation of the
#    Generator g
#    """
DUMMY_Q = long("e21e04f911d1ed7991008ecaab3bf775984309c3", 16)

DUMMY_P = long("""
  ff600483db6abfc5b45eab78594b3533d550d9f1bf2a992a7a8daa6dc34f8045ad4e6e0c429
  d334eeeaaefd7e23d4810be00e4cc1492cba325ba81ff2d5a5b305a8d17eb3bf4a06a349d39
  2e00d329744a5179380344e82a18c47933438f891e22aeef812d69c8f75e326cb70ea000c3f
  776dfdbd604638c2ef717fc26d02e17
""".replace(" ", "").replace("\n", "").strip(), 16)

DUMMY_G = long("""
  c52a4a0ff3b7e61fdf1867ce84138369a6154f4afa92966e3c827e25cfa6cf508b90e5de419
  e1337e07a2e9e2a3cd5dea704d175f8ebf6af397d69e110b96afb17c7a03259329e4829b0d0
  3bbc7896b15b4ade53e130858cc34d96269aa89041f409136c7242a38895c9d5bccad4f389a
  f1d7a4bd1398bd072dffa896233397a
""".replace(" ", "").replace("\n", "").strip(), 16)


def _hex(value):
    """Like the builtin hex(), but without formatting guff."""
    value = hex(value)[2:]
    if value.endswith("L"):
        value = value[:-1]
    return value


def fetch_public_key(hostname):
    """Fetch the BrowserID public key for the given hostname.

    Actually, this implementation generates the key locally based on
    a hash of the hostname.  This lets us exercise all the crypto code
    while using predictable local values.
    """
    return get_keypair(hostname)[0]


def get_keypair(hostname):
    """Generate a dummy keypair for the given hostname.

    This method generates a dummy DSA keypair for the given hostname.
    It returns a tuple (pub, priv) where "pub" is a dict of values for
    the public key, and "priv" is a DSA128Key object containing the
    private key.  Multiple calls to this method for the same hostname
    are guaranteed to produce the same key.

    To make this work we take advantage of the fact that DSA key generation
    is just "generate x by some random method, where 0 < x < q".  Replace
    "some random method" with "sha1 hash of hostname" and we're all set.
    """
    # Use pre-agreed parameters for p, q and g.
    q = DUMMY_Q
    p = DUMMY_P
    g = DUMMY_G
    # Generate private key x by "some random method".
    x = long(hashlib.sha1(hostname).hexdigest(), 16)
    assert x != 0, "SHA1(hostname) is zero - what are the odds?!"
    # Calculate public key y as usual.
    y = pow(g, x, p)
    data = {
      "algorithm": "DS",
      "p": _hex(p),
      "q": _hex(q),
      "g": _hex(g),
      "y": _hex(y),
      "x": _hex(x),
    }
    privkey = jwt.DS128Key(data)
    del data["x"]
    return data, privkey


def make_assertion(email, audience, issuer=None, exp=None,
                    assertion_sig=None, certificate_sig=None,
                    new_style=True):
    """Generate a new dummy assertion for the given email address.

    This method lets you generate BrowserID assertions using dummy private
    keys. Called with just an email and audience it will generate an assertion
    from browserid.org.

    By specifying the "exp", "assertion_sig" or "certificate_sig" arguments
    it is possible generate invalid assertions for testing purposes.
    """
    if issuer is None:
        issuer = "browserid.org"
    if exp is None:
        exp = int((time.time() + 60) * 1000)
    # Get private key for the email address itself.
    email_pub, email_priv = get_keypair(email)
    # Get private key for the hostname so we can sign it.
    iss_pub, iss_priv = get_keypair(issuer)
    # Generate the assertion, signed with email's public key.
    assertion = {
        "exp": exp,
        "aud": audience,
    }
    assertion = jwt.generate(assertion, email_priv)
    if assertion_sig is not None:
        assertion = ".".join(assertion.split(".")[:-1] +
                                [encode_bytes(assertion_sig)])
    # Generate the certificate signing the email's public key
    # with the issuer's public key.
    certificate = {
        "iss": issuer,
        "exp": exp,
        "principal": {"email": email},
        "public-key": email_pub,
    }
    certificate = jwt.generate(certificate, iss_priv)
    if certificate_sig is not None:
        certificate = ".".join(certificate.split(".")[:-1] +
                                [encode_bytes(certificate_sig)])
    # Combine them into a BrowserID bundled assertion.
    return bundle_certs_and_assertion([certificate], assertion, new_style)


@contextmanager
def patched_urlopen(replacement=None, exc=None, value=None):
    def _urlopen(*args, **kwargs):
        if exc is not None:
            raise exc
        return value
    if replacement is None:
        replacement = _urlopen
    old_urlopen = (certificates.secure_urlopen, remote.secure_urlopen)
    certificates.secure_urlopen = replacement
    remote.secure_urlopen = replacement
    yield
    certificates.secure_urlopen, remote.secure_urlopen = old_urlopen


@contextmanager
def patched_key_fetching(replacement=None, exc=None):
    """Patch the key fetching mechanism with the given callable.

    This is to allow easier testing.
    """
    def raise_exception(*args, **kwargs):
        raise exc

    if exc is not None:
        replacement = raise_exception
    if replacement is None:
        replacement = fetch_public_key
    old_callable = certificates.fetch_public_key
    certificates.fetch_public_key = replacement
    yield
    certificates.fetch_public_key = old_callable
