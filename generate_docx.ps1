$sourceHtml = "C:\Users\USER\OneDrive\바탕 화면\뇌신경센터\sleep_apnea_stroke_article.html"
$destHtml = "C:\Users\USER\OneDrive\바탕 화면\언론기사\2026년 3월 언론기사\뇌신경센터\sleep_apnea_stroke_article.html"
$destDocx = "C:\Users\USER\OneDrive\바탕 화면\언론기사\2026년 3월 언론기사\뇌신경센터\sleep_apnea_stroke_article.docx"

Copy-Item $sourceHtml -Destination $destHtml -Force

Write-Host "Converting HTML to DOCX using Word COM object..."
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($destHtml)
    $doc.SaveAs([ref]$destDocx, [ref]16)
    $doc.Close()
    Write-Host "DOCX created successfully at $destDocx"
} catch {
    Write-Host "Error converting to docx: $_"
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
