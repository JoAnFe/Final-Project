#!/usr/bin/env bash
set -euo pipefail

ROOT=./pki
mkdir -p $ROOT/{ca,broker,gateway,devices,crl}
cd $ROOT

# CA
openssl ecparam -name prime256v1 -genkey -noout -out ca/ca.key
openssl req -x509 -new -key ca/ca.key -sha256 -days 3650 \
  -subj "/CN=SmartAgri Root CA" -out ca/ca.crt

# Broker cert
openssl ecparam -name prime256v1 -genkey -noout -out broker/broker.key
openssl req -new -key broker/broker.key -subj "/CN=broker.local" -out broker/broker.csr
openssl x509 -req -in broker/broker.csr -CA ca/ca.crt -CAkey ca/ca.key -CAcreateserial \
 -out broker/broker.crt -days 1095 -sha256 -extfile <(printf "subjectAltName=DNS:broker,DNS:broker.local,IP:127.0.0.1")

# Gateway cert
openssl ecparam -name prime256v1 -genkey -noout -out gateway/gateway.key
openssl req -new -key gateway/gateway.key -subj "/CN=gateway-1" -out gateway/gateway.csr
openssl x509 -req -in gateway/gateway.csr -CA ca/ca.crt -CAkey ca/ca.key -CAcreateserial \
 -out gateway/gateway.crt -days 730 -sha256

# Device factory function
mkdir -p devices/issued
issue_device () {
  DID="$1"
  openssl ecparam -name prime256v1 -genkey -noout -out "devices/${DID}.key"
  openssl req -new -key "devices/${DID}.key" -subj "/CN=${DID}" -out "devices/${DID}.csr"
  openssl x509 -req -in "devices/${DID}.csr" -CA ca/ca.crt -CAkey ca/ca.key -CAcreateserial \
   -out "devices/${DID}.crt" -days 365 -sha256
  cp "devices/${DID}.crt" "devices/issued/"
}
# issue_device device-001

# Empty CRL
openssl ca -gencrl -keyfile ca/ca.key -cert ca/ca.crt -out crl/ca.crl -config ../openssl.cnf
echo "PKI ready under security/pki"
