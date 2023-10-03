# Nokio bookeeping

Author: **Mikael Backlund** Owner: **Be Lean Building Solutions AB**

Nokio is a product that helps small business doing small bookkeeping tasks. These tasks
include:

* Keeping gneral ledger (GL)
* Performing Reconciliation of accounts
* VAT reporting
* Balance sheet
* Result sheet
* Closing of books

Domain name filed at namecheap.org: nokio.org

## Transaction

These are documents in MongoDB Atlas and in the collection 2023 of the database connected to org no. Immutable

```json
{
    "t_id": 4,
    "t_name": "Domain fee 1Y",
    "t_date": "2023-10-03T16:38:12Z",
    "t_description": "Domain name to map host IP to nokio.org",
    "t_data": {
        "T_Kassa +/- (1930)":           [0, 84.62], 
        "K_Post&Internet +/- (8265)":   [84.62, 0]
        },
    "t_method": "https://nokio.org/method/#Transaction_explained",
    "t_verification": 8
}
```

### Verificate

The verficate is a proof of the transaction

```json
{
    "v_id": 8,
    "v_image": "https://nokio.org/5569979445/4_1.png",
    "v_uploaded": "2023-10-02T14:38:12Z",
}
```

## Transaction store

Transaction store in a MongoDB document database on database per company.
One document represent a year and has the structure. There are no time in GL as it can be recalculated from the beginning of the year (immutable) with all the valid transactions. The last transaction flag is for knowing the highest numbered transaction in the GL. That also give the last updated time. Mutable

```json
{
    "556997-9445": 2023,
    "GeneralLedger": 
    {
        "T_Kassa +- (1930)" :         25 915.38,
        "S_Eget kapital -+ (2045)":  -25 000.00,
        "I_Income -+ (3000)" :         1 000.00,
        "K_Post&Internet +- (8265)":      84.62, 
    },
    "last_transcation": 4
}
```

## Kontoplanen

Is fixed with a name and a account number. This can be aliased at own will the account number is always the account identifier. Immutable.

```json
{
    "1630": ["Skattekonto", "T_Skattekonto +-" ],
    "1930": ["Kassa", "T_Kassa +-" ],
}
```

## Transaction templates

Are historic transactions that can be utilized to help out with the transaction data entering.

```json
{
    [
        {
            "name": "Domain fee",
            "structure": ["1930K", "8265D"]
        }, 
        {
            "name": "Salary",
            "structure": ["3000K", "1930D", "2640D"]
        }
    ]
}
```

## Reconciliation

Sometimes you need to reconciliate the account and make everything upto that data immutable.

## VAT

Run accounts against each other ingående - utgånde and grenerate a skatteverket fil

## Balance sheet

Dept versus tillgång and they should end up as zero

## Result sheet

intäkt - result and they should erqual eachother out

## Bokslut

Is about closing the books for the year and generate a sammanställning for årsredovisning and tax papers

## 3.12 rules

Gives the amount owned by company to major shareholders

## Git

```bash
    # start git on localhost
    git init

    # add files to local repo
    git add . -m "Inital commit"

    # Create a main branch
    git symbolic-ref HEAD refs/heads/main
    git commit -m "Adding branch main"

    # Add remote repo
    git remote add origin https://github.com/belean/nokio.git

    # Github doesn't support password get a PAT token from Github user. Store in .env and enter as password
    git config --local credential.helper ""
    git pull origin main --allow-unrelated-histories

    # push the changes to remote (origin)
    git push origin main
```
