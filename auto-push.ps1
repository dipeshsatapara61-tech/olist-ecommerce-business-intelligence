$ErrorActionPreference = "Continue"

Write-Host "Automatic GitHub Sync Started!" -ForegroundColor Green
Write-Host "Monitoring your project folder..." -ForegroundColor Cyan
Write-Host "Press CTRL+C to stop." -ForegroundColor Yellow

$lastSnapshot = ""
$lastChange = Get-Date

while ($true) {
    try {
        $snapshot = (
            Get-ChildItem -Path . -File -Recurse -Force |
            Where-Object {
                $_.FullName -notmatch '[\\/]\.git[\\/]' -and
                $_.FullName -ne (Join-Path (Get-Location).Path "auto-push.ps1")
            } |
            ForEach-Object {
                "$($_.FullName)|$($_.Length)|$($_.LastWriteTimeUtc.Ticks)"
            } |
            Sort-Object
        ) -join "`n"

        if ($snapshot -ne $lastSnapshot) {
            $lastSnapshot = $snapshot
            $lastChange = Get-Date
            Write-Host "Changes detected. Waiting for editing to finish..." -ForegroundColor Yellow
        }

        if (((Get-Date) - $lastChange).TotalSeconds -ge 15) {
            $status = git status --porcelain --untracked-files=all

            if ($status) {
                git add -A

                git diff --cached --quiet

                if ($LASTEXITCODE -ne 0) {
                    $message = "Auto-sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

                    git commit -m $message

                    if ($LASTEXITCODE -eq 0) {
                        $branch = git branch --show-current
                        git push origin $branch

                        if ($LASTEXITCODE -eq 0) {
                            Write-Host "Successfully synced with GitHub!" -ForegroundColor Green
                        }
                        else {
                            Write-Host "Push failed. Check your internet or GitHub login." -ForegroundColor Red
                        }
                    }
                }
            }

            $lastChange = Get-Date
        }
    }
    catch {
        Write-Host "Sync error: $_" -ForegroundColor Red
    }

    Start-Sleep -Seconds 3
}
