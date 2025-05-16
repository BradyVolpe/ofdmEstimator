# ——— SET-UP / REPAIR THE VENV ———
cd ~/Development/ofdmEstimator || { echo "Folder not found"; exit 1; }

# nuke any existing venv (you already ok’d this)
rm -rf venv

# create a fresh venv with the default python3
python3 -m venv venv || { echo "venv creation failed"; exit 1; }

# activate it (zsh syntax)
source venv/bin/activate

# upgrade pip (nice to have)
python -m pip install --upgrade pip wheel setuptools

# show where the executables now live
echo -e "\n🔎 Sanity-check paths & versions"
which python
python --version
which pip
pip --version