; BastionCrypto External Helper Inno Setup Script

[Setup]
DisableStartupPrompt=yes
AppName=BastionCrypto External Helper Application
AppVerName=BastionCrypto External Editor 0.0.1
AppPublisher=Alan Milligan, Last BastionNetwork
AppPublisherURL=http://www.last-bastion.net
AppVersion=0.0.1
AppSupportURL=http://www.last-bastion.net/BastionCrypto
AppUpdatesURL=http://www.last-bastion.net/BastionCrypto
DefaultDirName={pf}\BastionCrypto
DefaultGroupName=BastionCrypto External Helper
AllowNoIcons=yes
LicenseFile=..\LICENSE.txt
ChangesAssociations=yes
OutputBaseFilename=bastioncrytpo-setup

[Registry]
; Register file type for use by helper app
Root: HKCR; SubKey: "BastionCrypto.Helper"; ValueType: string; ValueData: "BastionCrypto External Helper"; Flags: uninsdeletekeyifempty
Root: HKCR; SubKey: "BastionCrypto.Helper"; ValueType: binary; ValueName: "EditFlags"; ValueData: "00 00 01 00"; Flags: uninsdeletevalue
Root: HKCR; SubKey: "BastionCrypto.Helper\shell"; Flags: uninsdeletekeyifempty
Root: HKCR; SubKey: "BastionCrypto.Helper\shell\open"; Flags: uninsdeletekeyifempty
Root: HKCR; SubKey: "BastionCrypto.Helper\shell\open\command"; ValueType: string; ValueData: """{app}\bastioncrypto.exe"" ""%1"""; Flags: uninsdeletekeyifempty
Root: HKCR; SubKey: ".bastioncrypto"; ValueType: string; ValueData: "BastionCrypto.Helper"; Flags: uninsdeletekeyifempty
Root: HKCR; SubKey: ".bastioncrypto"; ValueType: string; ValueName: "PerceivedType"; ValueData: "BastionCrypto"; Flags: uninsdeletevalue
Root: HKCR; SubKey: ".bastioncrypto"; ValueType: string; ValueName: "Content Type"; ValueData: "application/x-bastioncrypto"; Flags: uninsdeletevalue
Root: HKCR; SubKey: "MIME\Database\Content Type\application/x-bastioncrypto"; ValueType: string; ValueName: "Extension"; ValueData: ".bastioncrypto"; Flags: uninsdeletevalue
Root: HKCR; SubKey: "MIME\Database\Content Type\application/x-bastioncrypto"; Flags: uninsdeletekeyifempty

[Files]
Source: "..\dist\*.*"; DestDir: "{app}"; Flags: ignoreversion
Source: "*.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CHANGES.txt"; DestDir: "{app}"; Flags: ignoreversion

