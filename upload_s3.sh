#!/bin/sh
set -euo pipefail
aws s3 cp --recursive build/ s3://review-me

