#define MyAppName "Avicole Pro"
#define MyAppVersion "3.1.0"
#define MyAppPublisher "Avicole Pro"
#define MyAppExeName "AvicolePro.exe"

[Setup]
AppId={{8C546E73-2B75-4E15-94AB-E72407F66801}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\Avicole Pro
DefaultGroupName=Avicole Pro
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=installer
OutputBaseFilename=AvicolePro-Setup-3.1.0
SetupIconFile=assets\avicole_pro.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer une icône sur le bureau"; GroupDescription: "Raccourcis supplémentaires :"; Flags: unchecked

[Files]
Source: "dist\AvicolePro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Avicole Pro"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Avicole Pro"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer Avicole Pro"; Flags: nowait postinstall skipifsilent
