$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "H:\inbound\src"

python H:\inbound\src\run_batch_proposals.py `
  --input-csv H:\inbound\scripts\sample_clients.csv `
  --backend mock `
  --output-dir H:\inbound\proposals\generated_batch `
  --table-policy forbid `
  --max-quality-retries 2 `
  --strict-quality
