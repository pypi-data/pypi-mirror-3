; YAREST 32-bit windows installer main include file
; Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>
;
; Requires the Inetc plug-in: http://nsis.sourceforge.net/Inetc_plug-in
; Requires the Nsisunz plug-in: http://nsis.sourceforge.net/Nsisunz_plug-in

!define AppIcon "logo.ico"                            ; icon file to use, must be in the same folder as this script
!define AppName "YAREST"                              ; application name used everywhere
!define AppRegKey "Software\${AppName}"               ; root registry key to use
!define AppVersion "0.4"                              ; current version information

; url where we download the pyCrypto zip package
!define PythonCryptoDownloadUrl "http://www.voidspace.org.uk/downloads/pycrypto-2.3.win32-py2.7.zip"
; file name only of the pyCrypto zip package
!define PythonCryptoDownloadFile "pycrypto-2.3.win32-py2.7.zip"
; file name only of the msi installer inside the zip package
!define PythonCryptoInstallFile "pycrypto-2.3.win32-py2.7.msi"

; url where we download the Python msi installer
!define PythonDownloadUrl "http://python.org/ftp/python/2.7.2/python-2.7.2.msi"
; file name only of the Python msi installer
!define PythonDownloadFile "python-2.7.2.msi"
; directory name used if we install Python, will get created under %SYSTEMROOT%
; used by the 'SetPythonDefaultInstallDir' function in "includes/functions.nsh"
!define PythonInstallDirName "python27"

; url where we download the wxPython exe installer
!define PythonWXDownloadUrl "http://downloads.sourceforge.net/wxpython/wxPython2.8-win32-unicode-2.8.12.1-py27.exe"
; file name only of the Python exe installer
!define PythonWXDownloadFile "wxPython2.8-win32-unicode-2.8.12.1-py27.exe"
; path (relative to the Python install directory) of the uninstaller created when we install it
!define PythonWXUninstallerFile "Lib\site-packages\wx-2.8-msw-unicode\unins000.exe"

;----------------------------
; installer attributes
;----------------------------

  CRCCheck force
  Name "${AppName}"
  OutFile "${AppOutputFile}"
  RequestExecutionLevel admin
  XPStyle on

  InstallDir "$PROGRAMFILES\${AppName}"
  InstallDirRegKey HKLM "${AppRegKey}" ""

;----------------------------
; interface configuration
;----------------------------

  !define MUI_ABORTWARNING
  !define MUI_ICON "${AppIcon}"

;----------------------------
; includes
;----------------------------

!include "LogicLib.nsh"
!include "MUI2.nsh"
!include "Sections.nsh"

!include "includes/EnvVarUpdate.nsh"
!include "includes/descriptions.nsh"
!include "includes/sections.nsh"
!include "includes/functions.nsh"
!include "includes/pages.nsh"
!include "includes/languages.nsh"
