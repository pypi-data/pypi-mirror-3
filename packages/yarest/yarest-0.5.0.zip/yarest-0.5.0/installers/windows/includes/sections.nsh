; YAREST windows installer section definitions
; Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

;----------------------------
; install sections
;----------------------------

Section "${AppName}" SEC_YAREST
  SectionIn RO
  DetailPrint "${INSTALL_YAREST_TEXT}"
  SetDetailsPrint listonly
  CreateDirectory "$INSTDIR"
  SetDetailsPrint both
SectionEnd

Section "Python" SEC_PYTHON
  Call DownloadAndInstallPython
SectionEnd

Section "pyCrypto" SEC_PYCRYPTO
  Call DownloadAndInstallPythonCrypto
SectionEnd

Section "wxPython" SEC_WXPYTHON
  Call DownloadAndInstallPythonWX
SectionEnd

Section "-final"
  DetailPrint "${INSTALL_YAREST_TEXT}"
  SetDetailsPrint listonly
  Call InstallYAREST
  Call InstallCustom
  Call InstallShortcuts
  Call InstallAddRemove
  SetDetailsPrint both
SectionEnd

;----------------------------
; uninstall sections
;----------------------------

Section "un.${AppName}" SEC_UN_YAREST
  SectionIn RO
  Call un.UninstallYAREST
SectionEnd

Section "un.wxPython" SEC_UN_WXPYTHON
  Call un.UninstallPythonWX
SectionEnd

Section "un.pyCrypto" SEC_UN_PYCRYPTO
  Call un.UninstallPythonCrypto
SectionEnd

Section "un.Python" SEC_UN_PYTHON
  Call un.UninstallPython
SectionEnd

Section "-un.final"
  Call un.InstallAddRemove
  Call un.InstallShortcuts
  Call un.InstallCustom
  RMDir "$INSTDIR"
SectionEnd
