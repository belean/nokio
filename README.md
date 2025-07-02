# Nokio bookeeping

Author: **Mikael Backlund** Owner: **Be Lean Building Solutions AB**

Nokio is an Open Source product (GPL3) that helps small business doing small and easy bookkeeping tasks. These tasks
include:

- Keeping general ledger (GL)
- Performing Reconciliation of accounts
- VAT reporting
- Balance sheet
- Result sheet
- Closing of books

Domain name filed at namecheap.org: nokio.org

## Installation

To run the FastAPI app execute

```bash
cd ~/Projects/nokio
poetry shell
uvicorn nokio.app.main:app --reload
```

To start appsmith environment

- Start Docker desktop

```bash
cd ~/Projects/appsmith
docker-compose up -d
```

## Transaction

These are documents in MongoDB Atlas and in the collection 2023 of the database connected to org no. Immutable

```json
{
  "t_id": 4,
  "t_name": "Domain fee 1Y",
  "t_date": "2023-10-03T16:38:12Z",
  "t_description": "Domain name to map host IP to nokio.org",
  "t_data": {
    "T_Kassa +/- (1930)": [0, 84.62],
    "K_Post&Internet +/- (8265)": [84.62, 0]
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
  "v_uploaded": "2023-10-02T14:38:12Z"
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
        "A_Kassa +- (1930)" :         25 915.38,
        "D_Eget kapital -+ (2045)":  -25 000.00,
        "I_Income -+ (3000)" :         1 000.00,
        "C_Post&Internet +- (8265)":      84.62,
    },
    "last_transcation": 4
}
```

## Kontoplanen

Is fixed with a name and a account number. This can be aliased at own will the account number is always the account identifier. Immutable.

```json
{
  "1630": ["Skattekonto", "T_Skattekonto +-"],
  "1930": ["Kassa", "T_Kassa +-"]
}
```

## Transaction templates

Are historic transactions that can be utilized to help out with the transaction data entering.

```json
{
  "templates": [
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

Sometimes you need to reconciliate the account and make everything upto that date immutable. Start with entering the ammount on the accounts 1630, 1930, 1940, 1385 at a certain date. Calculate the sum since the last consolidation and compare. Check with the user if it is correct or not. If correct then lock each transaction since last and log the consilidation datetime. If not correct display the unlocked transactions and let the user correct manually faulty transactions. Find the last entered consolidate_date for the last and the second last.

## VAT

Run accounts against each other ingående - utgånde and grenerate a skatteverket fil

## Balance sheet

Dept versus assets and they should always end up as zero

## Result sheet

income - cost = result and they should erqual each other out

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

## FastAPI

### FastAPI routes

| Endpoint             | Request type | Description                                                                                                  |
| -------------------- | ------------ | ------------------------------------------------------------------------------------------------------------ |
| /transaction         | GET          | Get a list of transactions with sorting options. Options: Sort by id asc and name asc and date desc.         |
| /transaction/{t_id}  | GET          | Get transaction by t_id                                                                                      |
| /transaction         | POST         | Create new transaction                                                                                       |
| /template            | GET          | Get list of templates                                                                                        |
| /template/{temp_id}  | GET          | Get template by id                                                                                           |
| /template            | POST         | Create new template                                                                                          |
| /accounts            | GET          | Get a list of accounts to consolidate                                                                        |
| /consilidation       | POST         | User provided balance for some accounts                                                                      |
| /consilidation_error | GET          | Calculate the error between the latest consilidation + transaction should equal the provided account balance |

or use debugging by using \*\*FastAPI (nokio) and set breakpoints

Try it out in the web browser
http://127.0.0.1:8000/transactions?orgnr=556997-9445
http://127.0.0.1:8000/transactions?orgnr=556997-9445&sort_by=id
or
http://127.0.0.1:8000/docs

## AWS Amplify build setting

```yaml
version: 1
backend:
  phases:
    build:
      commands:
        - "# Execute Amplify CLI with the helper script"
        - update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.8 11
        - /usr/local/bin/pip3.8 install --user pipenv
        - amplifyPush --simple
frontend:
  phases:
    preBuild:
      commands:
        - yarn install
    build:
      commands:
        - yarn run build
        - node ./node_modules/gulp/bin/gulp.js licenses
  artifacts:
    baseDirectory: build
    files:
      - "**/*"
  cache:
    paths:
      - node_modules/**/*
```

## Connect Appsmith docker container to FastAPI on localhost

<https://stackoverflow.com/questions/24319662/from-inside-of-a-docker-container-how-do-i-connect-to-the-localhost-of-the-mach>

and

<https://docs.appsmith.com/connect-data/how-to-guides/how-to-work-with-local-apis-on-appsmith?connect-method=localhost>
