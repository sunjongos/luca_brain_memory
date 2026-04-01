# AIndb Daily Sync Client (POC)
# Namyangju Baek Hospital Technical Director Luca

$serverUrl = "http://localhost:8888/config"
$localConfigFile = "central_config.json"

Write-Host "🏥 AIndb Daily Sync 시작합니다... 원장님 잠시만 기다려 주십시오! 🫡" -ForegroundColor Cyan

try {
    # 1. Fetch config from central server
    $response = Invoke-RestMethod -Uri $serverUrl -Method Get -ErrorAction Stop
    
    # 2. Save locally
    $response | ConvertTo-Json | Out-File $localConfigFile
    
    # 3. Success Message
    Write-Host "🚀 동기화 성공! 최신 지침(v$($response.version))을 수혈받았습니다." -ForegroundColor Green
    Write-Host "--------------------------------------------------"
    Write-Host "현재 적용된 글로벌 지침:"
    foreach ($line in $response.global_instructions) {
        Write-Host "✅ $line"
    }
    Write-Host "--------------------------------------------------"
}
catch {
    Write-Host "❌ 서버 연결 실패! (URL: $serverUrl)" -ForegroundColor Red
    Write-Host "원장님, 전산팀 망 상태를 확인하거나 중앙 서버가 켜져 있는지 확인해 주세요." -ForegroundColor Yellow
}
