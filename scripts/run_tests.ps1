$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "H:\inbound\src"
python -m unittest discover -s H:\inbound\tests -p "test_*.py"
