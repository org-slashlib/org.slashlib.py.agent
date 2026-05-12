write-host "Setting up environment for `Python Agent` ..."

# Die Policy für den Prozess setzen (sicher ist sicher)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# Python Bytecode-Cache umleiten (Muss vor dem Python-Start passieren!)
# $PSScriptRoot sorgt dafür, dass der Pfad absolut zum Skript aufgelöst wird
$env:PYTHONPYCACHEPREFIX = "$PSScriptRoot\..\.pycache"
# Required to locate and run python modules in src path
$env:PYTHONPATH = "src"

# Sourcen der python Umgebung
. .\envs\py311\Scripts\Activate.ps1

write-host "... done" -ForegroundColor Green
