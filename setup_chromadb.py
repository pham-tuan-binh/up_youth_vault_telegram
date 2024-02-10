from upyouth_vault_assist.upyouth_vault_interface import *

# Set up UpYouth Vault
vault = UpYouthVault("https://script.google.com/macros/s/AKfycbwvy35Xvp7oAzoEzpvYgCCQ4HdcID-PrfPaXWoDMfg-I6evdN64cgzCYtL1CWPnxQ0wjA/exec")

data = vault.retrieveResources()

for document in data:
    vault.addResourceToChroma(document)