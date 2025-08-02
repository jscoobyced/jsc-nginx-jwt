# Nginx Auth JWT Module

Run NGinx as a proxy with authentication using JWTs.

## Quick start

- **Authentication**:
  Uses JSON Web Tokens (JWTs) for user authentication.

To create your keys and tokens, use the `generate-jwks.py` script:

```
python3 generate-jwks.py --subject=user --issuer=localhost --audience=development --expiry=365 --import-private-key --export-jwks
```

Where:

- `--subject`: The subject of the JWT (default is "user").
- `--issuer`: The issuer of the JWT (default is "localhost").
- `--audience`: The audience for the JWT (default is "development").
- `--expiry`: The expiry time for the JWT in days (default is 365).
- `--import-private-key`: If set, import a private key from a PEM file
- `--export-jwks`: If set, export JWKS (JSON Web Key Set) to a file.

The first time, you only need the following command:

```
python3 generate-jwks.py --subject=user --issuer=localhost --audience=development --expiry=365 --export-jwks
```

This will create the `public.jwks` file (which is mounted as a volume in the docker-compose file) and display your JWT to use in the `Authentication` HTTP Header.

- **Configuration**:
  Update the `nginx.conf` file with your proxy settings.

- **Docker**:
  Then `docker-compose-up` to start your containers.
