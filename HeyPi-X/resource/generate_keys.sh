#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

openssl req -x509 -newkey rsa:2048 -days 3650 -keyout $DIR/rsa_private.pem -nodes -out \
    $DIR/rsa_cert.pem -subj "/CN=unused"