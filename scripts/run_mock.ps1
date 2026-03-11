param(
  [string]$ClientName = "SampleClinic",
  [string]$Industry = "medical",
  [string]$Region = "Busan Haeundae",
  [string]$BudgetRange = "500-800 KRW x10000 / month"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "H:\inbound\src"

python H:\inbound\src\run_proposal.py `
  --client-name $ClientName `
  --industry $Industry `
  --region $Region `
  --budget-range $BudgetRange `
  --target-segments "women 20s,women 30s" `
  --constraints "medical ad compliance,no exaggerated claims" `
  --backend mock `
  --output-format both `
  --table-policy forbid `
  --save-json-report `
  --output-dir H:\inbound\proposals\generated
