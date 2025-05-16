#!/bin/bash

# Build the test image
docker build -t route-listener-test .

# Run the tests with necessary capabilities
docker run --rm \
    --cap-add=NET_ADMIN \
    --cap-add=NET_RAW \
    --cap-add=NET_BROADCAST \
    --cap-add=SYS_ADMIN \
    route-listener-test \
    pytest tests/test_router_advertisement.py -v 