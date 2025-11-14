#!/bin/bash

# Variables
TERRAFORM_VERSION="1.13.5"
TMP_DIR="/tmp/terraform_install"

# Création dossier temporaire
mkdir -p $TMP_DIR
cd $TMP_DIR || exit

# Téléchargement du binaire officiel
wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip

# Dézipper
unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip

# Déplacement dans /usr/local/bin (remplace l'existant)
sudo mv terraform /usr/local/bin/terraform

# Vérification
terraform -version

# Nettoyage
cd ~ || exit
rm -rf $TMP_DIR

echo "Terraform ${TERRAFORM_VERSION} installé avec succès !"
