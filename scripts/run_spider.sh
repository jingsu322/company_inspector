#!/usr/bin/env bash
# Optional: uncomment to auto-activate your conda environment
# source ~/anaconda3/etc/profile.d/conda.sh
# conda activate env-iospace

# Make sure you have activated the correct environment before running

# Ensure output directory exists
mkdir -p output

# Launch the Scrapy spider
scrapy crawl company_spider