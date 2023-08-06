# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json

from browserid.verifiers import Verifier
from browserid.utils import (secure_urlopen,
                             decode_json_bytes,
                             unbundle_certs_and_assertion)
from browserid.errors import (InvalidSignatureError,
                              ConnectionError,
                              AudienceMismatchError)

BROWSERID_VERIFIER_URL = "https://browserid.org/verify"


class RemoteVerifier(Verifier):
    """Class for remote verification of BrowserID identity assertions.

    This class submits assertions to the browserid.org verifier service
    for remote verification.  It's slower but potentially a little bit
    safer than the still-under-development LocalVerifier class.
    """

    def __init__(self, audiences=None, verifier_url=None):
        if verifier_url is None:
            verifier_url = BROWSERID_VERIFIER_URL
        super(RemoteVerifier, self).__init__(audiences)
        self.verifier_url = verifier_url

    def verify(self, assertion, audience=None):
        """Verify the given BrowserID assertion.

        This method posts the given BrowserID assertion to the remote verifier
        service.  If it is successfully verified then a dict giving the
        email and audience is returned.  If it is not valid then an error
        is raised.

        If the 'audience' argument is given, it first verifies that the
        audience of the assertion matches the one given.  This can help
        avoid doing lots of crypto for assertions that can't be valid.
        If you don't specify an audience, you *MUST* validate the audience
        value returned by this method.
        """
        # Check the audience locally.
        # No point talking to the network if we know it's going to fail.
        # If no explicit audience was given, this will also parse it out
        # for inclusion in the request to the remote verifier service.
        audience = self.check_audience(assertion, audience)
        # Encode the data into x-www-form-urlencoded.
        post_data = {"assertion": assertion, "audience": audience}
        post_data = "&".join("%s=%s" % item for item in post_data.items())
        # Post it to the verifier.
        try:
            resp = secure_urlopen(self.verifier_url, post_data)
        except ConnectionError, e:
            # BrowserID server sends "500 server error" for broken assertions.
            # For now, just translate that directly.  Should check by hand.
            if "500" in str(e):
                raise ValueError("Malformed assertion")
            raise
        # Read the response, being careful to raise an appropriate
        # error if the server does something funny.
        try:
            try:
                info = resp.info()
            except AttributeError:
                info = {}
            content_length = info.get("Content-Length")
            if content_length is None:
                data = resp.read()
            else:
                data = resp.read(int(content_length))
            data = json.loads(data)
        except ValueError:
            raise ConnectionError("server returned invalid response")
        # Did it come back clean?
        if data.get('status') != "okay":
            raise InvalidSignatureError(str(data))
        if data.get('audience') != audience:
            raise AudienceMismatchError(data.get("audience"), audience)
        return data
