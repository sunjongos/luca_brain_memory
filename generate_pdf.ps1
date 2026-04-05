$htmlPath = "C:\Users\USER\OneDrive\바탕 화면\언론기사\2026년 3월 언론기사\뇌신경센터\sleep_apnea_stroke_article.html"
$pdfPath = "C:\Users\USER\OneDrive\바탕 화면\언론기사\2026년 3월 언론기사\뇌신경센터\sleep_apnea_stroke_article.pdf"

$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$chromePath86 = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

$browser = ""
if (Test-Path $edgePath) { $browser = $edgePath }
elseif (Test-Path $chromePath) { $browser = $chromePath }
elseif (Test-Path $chromePath86) { $browser = $chromePath86 }

if ($browser -ne "") {
    Write-Host "Using browser at $browser"
    Start-Process -FilePath $browser -ArgumentList "--headless", "--disable-gpu", "--print-to-pdf=$pdfPath", "`"$htmlPath`"" -Wait -NoNewWindow
    Write-Host "PDF generated."
} else {
    Write-Host "No suitable browser found for PDF generation."
}
