; YAREST support consumer 32-bit windows installer script
; Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>
;
; See the "x86.nsh" file for the main configuration options

; the root directory of the distribution, modify this to fit your environment
!define RootSrcDir "/home/mike/yarest"

; installer file to generate
!define AppOutputFile "consumer-win32.exe"

; folder where start menu shortcuts are created
!define AppShortcutsFolder "$SMPROGRAMS"

; include the main definitions file
!include "x86.nsh"

;----------------------------
; install/uninstall custom files
;----------------------------

Function InstallCustom
  CreateDirectory "$INSTDIR\examples"
  SetOutPath "$INSTDIR\examples"
  File /r "${RootSrcDir}\examples\*.*"

  SetOutPath "$INSTDIR"
  File "${RootSrcDir}/ACKNOWLEDGE.txt"
  File "${RootSrcDir}/CHANGELOG.txt"
  File "${RootSrcDir}/LICENSE.txt"
  File "${RootSrcDir}/README.txt"
FunctionEnd

Function un.InstallCustom
  RMDir /r "$INSTDIR\examples"
  Delete "$INSTDIR\ACKNOWLEDGE.txt"
  Delete "$INSTDIR\CHANGELOG.txt"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\README.txt"
FunctionEnd

;----------------------------
; install/uninstall shortcuts
;----------------------------

Function InstallShortcuts
  SetShellVarContext all
  CreateDirectory "${AppShortcutsFolder}"
  CreateShortCut "${AppShortcutsFolder}\${AppName} Consumer.lnk" "$PYTHON_DIR\Scripts\yarest.exe" "" "$INSTDIR\${AppIcon}"
FunctionEnd

Function un.InstallShortcuts
  SetShellVarContext all
  Delete "${AppShortcutsFolder}\${AppName} Consumer.lnk"
  RMDir "${AppShortcutsFolder}"
FunctionEnd
