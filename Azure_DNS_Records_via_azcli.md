## How to create DNS records via az-cli
If you are frequently creating DNS records, it is much easier to set up az cli to do it without having to log into the Azure Web portal.

### First set up AZ CLI

1. Install **az cli** [from here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)

2. Log in to az cli with
```az login```

3. Set table output as default (optional, qol)
```
az configure --defaults output=table
```
4. List and set your subscription
```
az account list
az account set --subscription [SUBSCRIPTION-NAME]
```

5. List and set your Location
```
az group list
az configure --defaults location=australiaeast
```

6. List and set your Resource Group
```
az group list
az configure --defaults group=[RESOURCE-GROUP-NAME]
```

### Now you can create DNS records

1. Create DNS records with
```
az network dns record-set a add-record --zone-name [ZONE-NAME] --ttl 600 --record-set-name [RECORD-NAME] --ipv4-address [IP-ADDRESS]
```

### (Optional) How to delete a DNS record set
1. List DNS records with
```
az network dns record-set list --zone-name [ZONE-NAME]
```

2. Delete one DNS record set with
```
az network dns record-set a delete --zone-name [ZONE-NAME] --name [RECORD-NAME]
```

## (Alias) Create Aliases for easy Creation
1. Create the aliases with the zone and ttl baked in
```
alias azcdns="az network dns record-set a delete --zone-name [ZONE-NAME] --ttl 600"
alias azdns="az network dns record-set list --zone-name [ZONE-NAME]"
alias azddns="az network dns record-set list --zone-name [ZONE-NAME]"
```

2. Use them like this (create / list / delete)
```
az-dns-create --name [HOSTNAME] --ipv4-address [IP-ADDRESS]
az-dns-list
az-dns-delete --name [HOSTNAME]
```
