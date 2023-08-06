; YAREST windows installer function definitions
; Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

;----------------------------
; Variables
;----------------------------

Var DESC_PYTHON
Var DESC_PYCRYPTO
Var DESC_WXPYTHON
Var INSTALLER_PATH
Var PYTHON_DIR
Var SELECTED
Var UNINSTALLER_PATH

;----------------------------
; remove string whitespace
;----------------------------

!define Trim "!insertmacro Trim"
 
!macro Trim ResultVar String
  Push "${String}"
  Call Trim
  Pop "${ResultVar}"
!macroend

Function Trim
	Exch $R1 ; Original string
	Push $R2
 
Loop:
	StrCpy $R2 "$R1" 1
	StrCmp "$R2" " " TrimLeft
	StrCmp "$R2" "$\r" TrimLeft
	StrCmp "$R2" "$\n" TrimLeft
	StrCmp "$R2" "$\t" TrimLeft
	GoTo Loop2
TrimLeft:	
	StrCpy $R1 "$R1" "" 1
	Goto Loop
 
Loop2:
	StrCpy $R2 "$R1" 1 -1
	StrCmp "$R2" " " TrimRight
	StrCmp "$R2" "$\r" TrimRight
	StrCmp "$R2" "$\n" TrimRight
	StrCmp "$R2" "$\t" TrimRight
	GoTo Done
TrimRight:	
	StrCpy $R1 "$R1" -1
	Goto Loop2
 
Done:
	Pop $R2
	Exch $R1
FunctionEnd

;----------------------------
; Callbacks
;----------------------------

Function .onInit
  IntOp $SELECTED ${SF_SELECTED} | ${SF_RO}
  Call GetPythonInstallDir
  ${If} $PYTHON_DIR == ""
    SectionSetFlags ${SEC_PYTHON} $SELECTED
    SectionSetFlags ${SEC_PYCRYPTO} $SELECTED
    SectionSetFlags ${SEC_WXPYTHON} $SELECTED
    StrCpy $DESC_PYTHON "${PYTHON_NOT_INSTALLED}"
    StrCpy $DESC_PYCRYPTO "${PYCRYPTO_NOT_INSTALLED}"
    StrCpy $DESC_WXPYTHON "${WXPYTHON_NOT_INSTALLED}"
  ${Else}
    SectionSetFlags ${SEC_PYTHON} ${SF_RO}
    StrCpy $DESC_PYTHON "${PYTHON_ALREADY_INSTALLED}"

    SetOutPath "$TEMP"
    File "${RootSrcDir}/installers/windows/scripts/checkforpycrypto.py"
    nsExec::ExecToStack /OEM '"$PYTHON_DIR\python.exe" checkforpycrypto.py'
    pop $0
    pop $1
    ${Trim} $0 $1
    ${If} $0 == "INSTALLED"
      SectionSetFlags ${SEC_PYCRYPTO} ${SF_RO}
      StrCpy $DESC_PYCRYPTO "${PYCRYPTO_ALREADY_INSTALLED}"
    ${Else}
      SectionSetFlags ${SEC_PYCRYPTO} $SELECTED
      StrCpy $DESC_PYCRYPTO "${PYCRYPTO_NOT_INSTALLED}"
    ${EndIf}
    Delete "$TEMP\checkforpycrypto.py"

    SetOutPath "$TEMP"
    File "${RootSrcDir}/installers/windows/scripts/checkforwxpython.py"
    nsExec::ExecToStack /OEM '"$PYTHON_DIR\python.exe" checkforwxpython.py'
    pop $0
    pop $1
    ${Trim} $0 $1
    ${If} $0 == "INSTALLED"
      SectionSetFlags ${SEC_WXPYTHON} ${SF_RO}
      StrCpy $DESC_WXPYTHON "${WXPYTHON_ALREADY_INSTALLED}"
    ${Else}
      SectionSetFlags ${SEC_WXPYTHON} $SELECTED
      StrCpy $DESC_WXPYTHON "${WXPYTHON_NOT_INSTALLED}"
    ${EndIf}
    Delete "$TEMP\checkforwxpython.py"
  ${EndIf}
FunctionEnd

Function un.onInit
  Call un.GetPythonUninstallString
  ${If} $UNINSTALLER_PATH != ""
    StrCpy $DESC_PYTHON "${PYTHON_WE_INSTALLED}"
  ${Else}
    SectionSetFlags ${SEC_UN_PYTHON} ${SF_RO}
    StrCpy $DESC_PYTHON "${PYTHON_WE_NO_INSTALL}"
  ${EndIf}

  Call un.GetPythonCryptoUninstallString
  ${If} $UNINSTALLER_PATH != ""
    StrCpy $DESC_PYCRYPTO "${PYCRYPTO_WE_INSTALLED}"
  ${Else}
    SectionSetFlags ${SEC_UN_PYCRYPTO} ${SF_RO}
    StrCpy $DESC_PYCRYPTO "${PYCRYPTO_WE_NO_INSTALL}"
  ${EndIf}

  Call un.GetPythonWXUninstallString
  ${If} $UNINSTALLER_PATH != ""
    StrCpy $DESC_WXPYTHON "${WXPYTHON_WE_INSTALLED}"
  ${Else}
    SectionSetFlags ${SEC_UN_WXPYTHON} ${SF_RO}
    StrCpy $DESC_WXPYTHON "${WXPYTHON_WE_NO_INSTALL}"
  ${EndIf}
FunctionEnd

;----------------------------
; Python
;----------------------------

Function DownloadAndInstallPython
  inetc::get /CAPTION "${DOWNLOAD_PYTHON_TEXT}" "${PythonDownloadUrl}" "$TEMP\${PythonDownloadFile}" /END
  pop $0
  ${If} $0 != "OK"
    MessageBox MB_OK|MB_ICONEXCLAMATION "${DOWNLOAD_PYTHON_ERR}"
    Abort
  ${EndIf}

  DetailPrint "${INSTALL_PYTHON_TEXT}"
  SetDetailsPrint listonly
  Call SetPythonDefaultInstallDir
  ExecWait 'msiexec /i "$TEMP\${PythonDownloadFile}" ALLUSERS=1 ADDLOCAL=Extensions TARGETDIR="$PYTHON_DIR" /qn' $0
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONEXCLAMATION "${INSTALL_PYTHON_ERR}"
    Abort
  ${EndIf}

  Rename "$TEMP\${PythonDownloadFile}" "$INSTDIR\${PythonDownloadFile}"
  StrCpy $INSTALLER_PATH "$INSTDIR\${PythonDownloadFile}"
  Call SetPythonInstallDir
  WriteRegStr HKLM "${AppRegKey}" "PythonUninstaller" "$INSTALLER_PATH"
  ${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$PYTHON_DIR"
  SetDetailsPrint both
FunctionEnd

Function GetPythonInstallDir
  ReadRegStr $PYTHON_DIR HKLM "${AppRegKey}" "PythonInstallDir"
  ${If} $PYTHON_DIR == ""
    ; no python found yet, let's see if it's on the PATH
    SetOutPath "$TEMP"
    File "${RootSrcDir}/installers/windows/scripts/getpythondir.py"
    nsExec::ExecToStack 'python "$TEMP\getpythondir.py"'
	Pop $0
    ${If} $0 != "error"
      ; see if we have a directory
      Pop $1
      ${Trim} $PYTHON_DIR $1
      ${If} $PYTHON_DIR != ""
        Call SetPythonInstallDir
        Delete "$TEMP\getpythondir.py"
        return
      ${EndIf}
    ${EndIf}
    Delete "$TEMP\getpythondir.py"

    ; not on the PATH, let's see if we can find it in the registry
    ReadRegStr $PYTHON_DIR HKLM "Software\Python\Pythoncore\2.7" "InstallPath"
    ${If} $PYTHON_DIR != ""
      Call SetPythonInstallDir
      return
    ${EndIf}
    ReadRegStr $PYTHON_DIR HKCU "Software\Python\Pythoncore\2.7" "InstallPath"
    ${If} $PYTHON_DIR != ""
      Call SetPythonInstallDir
      return
    ${EndIf}
    ReadRegStr $PYTHON_DIR HKLM "Software\Python\Pythoncore\2.6" "InstallPath"
    ${If} $PYTHON_DIR != ""
      Call SetPythonInstallDir
      return
    ${EndIf}
    ReadRegStr $PYTHON_DIR HKCU "Software\Python\Pythoncore\2.6" "InstallPath"
    ${If} $PYTHON_DIR != ""
      Call SetPythonInstallDir
      return
    ${EndIf}

    ; anything else?
  ${EndIf}
FunctionEnd

Function SetPythonDefaultInstallDir
  ReadEnvStr $0 SYSTEMDRIVE
  StrCpy $PYTHON_DIR "$0\${PythonInstallDirName}"
FunctionEnd

Function SetPythonInstallDir
  WriteRegStr HKLM "${AppRegKey}" "PythonInstallDir" "$PYTHON_DIR"
FunctionEnd

Function un.GetPythonInstallDir
  ReadRegStr $PYTHON_DIR HKLM "${AppRegKey}" "PythonInstallDir"
FunctionEnd

Function un.GetPythonUninstallString
  ReadRegStr $UNINSTALLER_PATH HKLM "${AppRegKey}" "PythonUninstaller"
FunctionEnd

Function un.UninstallPython
  Call un.GetPythonUninstallString
  ${If} $UNINSTALLER_PATH != ""
    DetailPrint "${UNINSTALL_PYTHON_TEXT}"
    SetDetailsPrint listonly
    ExecWait 'msiexec /x "$UNINSTALLER_PATH" /qn'
    Delete "$UNINSTALLER_PATH"
    Call un.GetPythonInstallDir
    ${un.EnvVarUpdate} $0 "PATH" "R" "HKLM" $PYTHON_DIR
    DeleteRegValue HKLM "${AppRegKey}" "PythonInstallDir"
    DeleteRegValue HKLM "${AppRegKey}" "PythonUninstaller"
    SetDetailsPrint both
  ${EndIf}
FunctionEnd

;----------------------------
; pyCrypto
;----------------------------

Function DownloadAndInstallPythonCrypto
  inetc::get /CAPTION "${DOWNLOAD_PYCRYPTO_TEXT}" "${PythonCryptoDownloadUrl}" "$TEMP\${PythonCryptoDownloadFile}" /END
  pop $0
  ${If} $0 != "OK"
    MessageBox MB_OK|MB_ICONEXCLAMATION "${DOWNLOAD_PYCRYPTO_ERR}"
    Abort
  ${EndIf}

  nsisunz::Unzip "$TEMP\${PythonCryptoDownloadFile}" "$TEMP"
  Delete "$TEMP\${PythonCryptoDownloadFile}"

  DetailPrint "${INSTALL_PYCRYPTO_TEXT}"
  SetDetailsPrint listonly
  Call GetPythonInstallDir
  ExecWait 'msiexec /i "$TEMP\${PythonCryptoInstallFile}" TARGETDIR="$PYTHON_DIR" /qn' $0
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONEXCLAMATION "${INSTALL_PYCRYPTO_ERR}"
    Abort
  ${EndIf}

  Rename "$TEMP\${PythonCryptoInstallFile}" "$INSTDIR\${PythonCryptoInstallFile}"
  StrCpy $INSTALLER_PATH "$INSTDIR\${PythonCryptoInstallFile}"
  WriteRegStr HKLM "${AppRegKey}" "pyCryptoUninstaller" "$INSTALLER_PATH"
  SetDetailsPrint both
FunctionEnd

Function un.GetPythonCryptoUninstallString
  ReadRegStr $UNINSTALLER_PATH HKLM "${AppRegKey}" "pyCryptoUninstaller"
FunctionEnd

Function un.UninstallPythonCrypto
  Call un.GetPythonCryptoUninstallString
  ${If} $UNINSTALLER_PATH != ""
    DetailPrint "${UNINSTALL_PYCRYPTO_TEXT}"
    SetDetailsPrint listonly
    ExecWait 'msiexec /x "$UNINSTALLER_PATH" /qn'
    Delete "$UNINSTALLER_PATH"
    DeleteRegValue HKLM "${AppRegKey}" "pyCryptoUninstaller"
    SetDetailsPrint both
  ${EndIf}
FunctionEnd

;----------------------------
; wxPython
;----------------------------

Function DownloadAndInstallPythonWX
  inetc::get /CAPTION "${DOWNLOAD_WXPYTHON_TEXT}" "${PythonWXDownloadUrl}" "$TEMP\${PythonWXDownloadFile}" /END
  pop $0
  ${If} $0 != "OK"
    MessageBox MB_OK|MB_ICONEXCLAMATION "${DOWNLOAD_WXPYTHON_ERR}"
    Abort
  ${EndIf}

  DetailPrint "${INSTALL_WXPYTHON_TEXT}"
  SetDetailsPrint listonly
  Call GetPythonInstallDir
  ExecWait '"$TEMP\${PythonWXDownloadFile}" /VERYSILENT' $0
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONEXCLAMATION "${INSTALL_WXPYTHON_ERR}"
    Abort
  ${EndIf}

  Delete "$TEMP\${PythonWXDownloadFile}"
  StrCpy $INSTALLER_PATH "$PYTHON_DIR\${PythonWXUninstallerFile}"
  WriteRegStr HKLM "${AppRegKey}" "wxPythonUninstaller" "$INSTALLER_PATH"
  SetDetailsPrint both
FunctionEnd

Function un.GetPythonWXUninstallString
  ReadRegStr $UNINSTALLER_PATH HKLM "${AppRegKey}" "wxPythonUninstaller"
FunctionEnd

Function un.UninstallPythonWX
  Call un.GetPythonWXUninstallString
  ${If} $UNINSTALLER_PATH != ""
    DetailPrint "${UNINSTALL_WXPYTHON_TEXT}"
    SetDetailsPrint listonly
    ExecWait '"$UNINSTALLER_PATH" /VERYSILENT'
    DeleteRegValue HKLM "${AppRegKey}" "wxPythonUninstaller"
    SetDetailsPrint both
  ${EndIf}
FunctionEnd

;----------------------------
; YAREST
;----------------------------

Function InstallYAREST
  Call GetPythonInstallDir
  ${If} $PYTHON_DIR == ""
    MessageBox MB_OK|MB_ICONEXCLAMATION "${INSTALL_ERR_NO_PYTHON}"
    Abort
  ${EndIf}

  CreateDirectory "$TEMP\${AppName}-${AppVersion}"

  CreateDirectory "$TEMP\${AppName}-${AppVersion}\resources"
  SetOutPath "$TEMP\${AppName}-${AppVersion}\resources"
  File /r "${RootSrcDir}\resources\*.*"

  CreateDirectory "$TEMP\${AppName}-${AppVersion}\yarest"
  SetOutPath "$TEMP\${AppName}-${AppVersion}\yarest"
  File /r "${RootSrcDir}\yarest\*.*"

  SetOutPath "$TEMP\${AppName}-${AppVersion}"
  File "${RootSrcDir}\*.py"
  File "${RootSrcDir}\*.txt"

  ExecWait '"$PYTHON_DIR\python.exe" setup.py install' $0
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONEXCLAMATION "${INSTALL_YAREST_ERR}"
    Abort
  ${EndIf}

  SetOutPath "$INSTDIR"
  File "${AppIcon}"
  WriteRegStr HKLM "${AppRegKey}" "" $INSTDIR
FunctionEnd

Function un.UninstallYAREST
  DetailPrint "${UNINSTALL_YAREST_TEXT}"
  SetDetailsPrint listonly
  Call un.GetPythonInstallDir
  RMDir /r "$PYTHON_DIR\Lib\site-packages\yarest*"
  Delete "$PYTHON_DIR\Scripts\yarest*"
  Delete "$INSTDIR\${AppIcon}"
  WriteRegStr HKLM "${AppRegKey}" "" ""
  SetDetailsPrint both
FunctionEnd

Function InstallAddRemove
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${AppName}" "DisplayIcon" "$INSTDIR\${AppIcon}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${AppName}" "DisplayName" "${AppName}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${AppName}" "DisplayVersion" "${AppVersion}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${AppName}" "UninstallString" "$INSTDIR\uninstall.exe"
FunctionEnd

Function un.InstallAddRemove
  Delete "$INSTDIR\uninstall.exe"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${AppName}"
FunctionEnd
