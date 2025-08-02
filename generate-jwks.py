#!/bin/python

from jwcrypto import jwk
import jwt
import datetime
import uuid
import argparse
import os

ALGORITHM = "RS512"
ALG_KTY = "RSA"
ALG_TYPE = "JWT"
ALG_SIZE = 4096
ALK_KEY_ID = str(uuid.uuid4())
JWT_ID = str(uuid.uuid4())
PRIVATE_KEY_PEM = "private_key.pem"

parser = argparse.ArgumentParser(description="JWT keys and tokens generator")
parser.add_argument(
    "--issuer", type=str, default="localhost", help="The issuer of the JWT"
)
parser.add_argument(
    "--subject", type=str, default="user", help="The subject of the JWT"
)
parser.add_argument(
    "--audience", type=str, default="development", help="The audience of the JWT"
)
parser.add_argument(
    "--expiry", type=int, default=365, help="The expiration time of the JWT in days"
)
parser.add_argument(
    "--import-private-key",
    action="store_true",
    default=False,
    help="Import private key",
)
parser.add_argument(
    "--export-jwks",
    action="store_true",
    default=False,
    help="Export the public.jwks file.",
)

# Parse the arguments
args = parser.parse_args()

if args.import_private_key and os.path.exists(PRIVATE_KEY_PEM):
    print("Private key found.")
    with open(PRIVATE_KEY_PEM, "r") as f:
        pem_private_key = f.read()
    str_to_byte = pem_private_key.encode("utf-8")
    private_key = jwk.JWK.from_pem(str_to_byte, password=None)
else:
    print("Private key not found or import is disabled.")
    # Generate a private key
    private_key = jwk.JWK.generate(
        size=ALG_SIZE, alg=ALGORITHM, kty=ALG_KTY, kid=JWT_ID
    )
    # Export the private key in PEM format
    pem_private_key = private_key.export_to_pem(private_key=True, password=None)
    # Save the private key to a file
    with open(PRIVATE_KEY_PEM, "wb") as f:
        f.write(pem_private_key)

# Export the public key from private key
public_key = jwk.JWK.export_public(private_key)

# Define the header and claim set for the JWT
header = {"alg": ALGORITHM, "typ": ALG_TYPE}

payload = {
    "iss": args.issuer,
    "sub": args.subject,
    "aud": args.audience,
    "exp": datetime.datetime.now(datetime.timezone.utc)
    + datetime.timedelta(days=args.expiry),  # Expiration time set to 20 days from now
    "iat": datetime.datetime.now(datetime.timezone.utc),  # Issued at time
    "jti": JWT_ID,  # JWT ID
}

# Generate the JWT token
token = jwt.encode(
    payload=payload, headers=header, key=pem_private_key, algorithm=ALGORITHM
)

print("Generated JWT Token:")
print(token)

if args.export_jwks:
    print("Exporting JWKS to public.jwks")
    keys = '{"keys": [' + public_key + "]}"
    with open("public.jwks", "w") as w:
        w.write(keys)
