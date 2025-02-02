Write-Host "STEP2 will take a while to install. STEP2 intalls Python and all Python and Java packages used by the NLP Suite. Please, be patient and wait for the message Installation Completed!"
Write-Host ""
Write-Host "STEP2 relies on Git. If you have not done so already, please download Git at this link https://git-scm.com/downloads (select the Windows link; it will automatically detect whether your machine is 32-bit or 64-bit on the top line Click here to download the latest...). Run the downloaded exe file."
Write-Host ""
$AREYOUSURE = Read-Host "Do you wish to continue (Yes if you have already installed Git and wish to continue; No to exit)? [y/n]"
if ( $AREYOUSURE -ne "y") {
    exit
}

cd "${PSScriptRoot}\..\"

conda create -n NLP python=3.8 -y
conda activate NLP

conda install pytorch torchvision cudatoolkit -c pytorch
pip install -r ../src/requirements.txt

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\NLP_Suite.lnk")
$Shortcut.TargetPath = "${PSScriptRoot}\run_NLP-Suite.bat"
$Shortcut.IconLocation = "${PSScriptRoot}\logo.ico"
$Shortcut.Save()

git init ..
git remote add -m current-stable -f origin https://github.com/NLP-Suite/NLP-Suite.git
git checkout -f current-stable
git add -A .
git stash
git pull -f origin current-stable

Write-Host "----------------------" -ForegroundColor Green
Write-Host "Installation Completed! Although installation completed, errors may have occurred in the installation of specific Python packages. Please, scroll up to see if errors occurred or use CTRL+F to search for words such as error or fail." -ForegroundColor Green
Write-Host "----------------------" -ForegroundColor Green

$ENDPROMPT = Read-Host "Press Return to close this window."
exit
