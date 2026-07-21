# QQ音乐自动搜索播放脚本
Add-Type -AssemblyName System.Windows.Forms

# 1. 先把搜索内容放入剪贴板
Set-Clipboard -Value "周杰伦 稻香"

# 2. 通过 COM 对象操作窗口
$wshell = New-Object -ComObject WScript.Shell

# 3. 尝试激活 QQ 音乐（尝试多个可能的窗口标题）
$found = $false
$titles = @("QQ音乐", "QQ Music", "腾讯QQ音乐")
foreach ($t in $titles) {
    try {
        $result = $wshell.AppActivate($t)
        if ($result) {
            Write-Host "找到窗口: $t"
            $found = $true
            break
        }
    } catch {}
}

if (-not $found) {
    Write-Host "未找到 QQ 音乐窗口，请确保 QQ 音乐已打开"
    exit 1
}

Start-Sleep -Milliseconds 500

# 4. Ctrl+F 聚焦搜索框
[System.Windows.Forms.SendKeys]::SendWait("^f")
Start-Sleep -Milliseconds 300

# 5. 全选 + 粘贴（绕过输入法）
[System.Windows.Forms.SendKeys]::SendWait("^a")
Start-Sleep -Milliseconds 100
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds 500

# 6. 回车搜索
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 1500

# 7. 尝试播放（按 Tab 到结果列表，再 Enter）
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")

Write-Host "操作完成！"
