# OAuth integration checklist

- LinkedIn: configure Developer app, redirect URI, OAuth state (CSRF protection), token exchange, target page/organization identity, and approved publishing scopes.
- Meta/Instagram: configure Meta app; ensure Professional account and linked Facebook Page as required; request current publishing scopes; validate state; exchange token; resolve target account.
- Encrypt tokens at rest with managed key service; never log tokens.
- Store authorized account, granted scopes, expiry, and audit trail.
- Add disconnect/revoke workflow and tenant-scoped access controls.
- Platform API access and app review may be required; confirm current official requirements before implementation.
