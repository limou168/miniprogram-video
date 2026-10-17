# QQ音乐自动搜索播放脚本（已校准）
# 用法: powershell -File qqmusic_search.ps1 "歌名"
param([string]$keyword)

if (-not $keyword) { $keyword = "周杰伦 稻香" }

Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, IntPtr dwExtraInfo);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
'@

# === 校准数据 ===
# QQ音乐搜索框相对窗口左上角的偏移量
$searchBoxOffsetX = 372
$searchBoxOffsetY = 36

# 1. 设置剪贴板
[System.Windows.Forms.Clipboard]::SetText($keyword)
Write-Host "搜索: $keyword"

# 2. 激活QQ音乐
$proc = Get-Process QQMusic -ErrorAction Stop
[Win32]::SetForegroundWindow($proc.MainWindowHandle)
Start-Sleep -Milliseconds 300

# 3. 点击搜索框
$rect = New-Object Win32+RECT
[Win32]::GetWindowRect($proc.MainWindowHandle, [ref]$rect)
$clickX = $rect.Left + $searchBoxOffsetX
$clickY = $rect.Top + $searchBoxOffsetY
[Win32]::SetCursorPos($clickX, $clickY)
Start-Sleep -Milliseconds 30
[Win32]::mouse_event([Win32]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 30
[Win32]::mouse_event([Win32]::MOUSEEVENTF_LEFTUP, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 400

# 4. 粘贴搜索
[System.Windows.Forms.SendKeys]::SendWait('^a')
Start-Sleep -Milliseconds 80
[System.Windows.Forms.SendKeys]::SendWait('^v')
Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
Start-Sleep -Milliseconds 1500

# 5. 播放第一首
[System.Windows.Forms.SendKeys]::SendWait('{TAB}')
Start-Sleep -Milliseconds 150
[System.Windows.Forms.SendKeys]::SendWait('{TAB}')
Start-Sleep -Milliseconds 150
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')

Write-Host "完成!"
