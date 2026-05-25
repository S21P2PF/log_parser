#!/bin/bash
cd "$(dirname "$0")/scripts" || exit
python3 parcer.py
python3 decoder.py
python3 loger.py
python3 sorter.py
rm -f ../data/requests.txt ../data/responses.txt ../data/requests_decoded.txt ../data/responses_decoded.txt