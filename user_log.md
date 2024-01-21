# Nokio user log

## Next steps

1. Import Bokio backup readout
1. New transaction Button and clear text area
1. Save transaction as a template, update template list
1. Delete transaction if not consolidated
1. FastAPI in Docker container started with docker compose start
1. Finish the emailing belean/Sciple/Nokio to One Lambda
1. Finish the Bokio import
1. AWS cognito user sign up
1. Google analytics for cash
1. ~~Appsmith web page for accessing the Python FastAPI~~
1. ~~Nicer logging with one logger for the entire module, like [Python Logging]~~
1. ~~Unit test fixtures in pytest to set up and tear down test suite~~
1. ~~Python API for separating presentation and logic~~
1. ~~Web landing page to attract users~~
1. ~~Configure amplify hosting~~
1. ~~Favicon to website and~~
1. ~~Create a text edit area with json validator with [ajv] or [Json Form]~~
1. ~~see <https://docs.appsmith.com/core-concepts/writing-code/ext-libraries>~~
1. ~~Create a text edit area with and sum calculation.~~

## Mikael @ 2024-01-01

- Appsmith web page for accessing the Python FastAPI
- Using JSONForm
- using FastAPI
- Validating t_data

## Mikael @ 2023-12-30

- testing JSONForm

## Mikael @ 2023-12-27

- Connecting Appsmith in container with FastAPI on host with host.docker.internal

## Mikael @ 2023-12-26

- Starting appsmith:
  - Start docker deamon in Mac OS by Docker Desktop
  - cd /Users/backis/Projects/appsmith
  - docker compose start
  - Login at http://localhost
    with backis2012@gmail.com and `b****S*2*`
  - Select dev
- Adding save as template
- Cleaned up templates in MongoDB (as info@belean.se)
- Connect with Fast api on port 8000
  - open 8000 on docker in Appsmith

## Mikael @ 2023-12-17

- Now trans, trans list and trans template work together

## Mikael @ 2023-12-16

- Start to play with with Appsmith
- Appsmith license key: 28E896-A51C90-579DFC-2611C1-5C4011-V3

## Mikael @ 2023-12-03

- Started with a Streamlit GUI

## Mikael @ 2023-11-29

- Reformat bokio_import and debugging and test remains
  - KONTO
  - SRU
  - UB
  - IB
  - RES

## Mikael @ 2023-11-28

- Converting SIE file to json. Done with:
  - Konto
  - IB

## Mikael @ 2023-11-25

- Updated favicon.ico with python project svg2ico in ~/Projects and Inkscape for png image.
- Created a new be lean logotype in Landing page

## Mikael @ 2023-11-19

- Activated domain nokio.org in [Namecheap]
  - <www.nokio.org> -> d3hb68lkbfe00j.cloudfront.net
  - <www.nokio.org> -> d3hb68lkbfe00j.cloudfront.net
  - Recreated nokio-web amplify app
  - Centered cards in SectionTeam

## Mikael@2023-11-05

- Cloning the Sciple website i.e. landing page.

  - Updated build setting to Python 3.8
  - updated py_modules in setup.py in Sciple/website before cloning

  ```bash
  "amplify status" will show you what you've added already and if it's locally configured or deployed
  "amplify add <category>" will allow you to add features like user login or a backend API
  "amplify push" will build all your local backend resources and provision it in the cloud
  "amplify console" to open the Amplify Console and view your project status
  "amplify publish" will build all your local backend and frontend resources (if you have hosting category added) and provision it in the cloud
  ```

  - Creative Tim is not open source and not for public GH repos

## mikael@2023-10-10

- Nicer logging for module [Python Logging](https://betterstack.com/community/guides/logging/how-to-start-logging-with-python/)
- Pytest setup and teardown [Pytest fixtures](https://docs.pytest.org/en/6.2.x/fixture.html)
- FastAPI working for transactions [FastAPI Handbook – How to Develop, Test, and Deploy APIs](https://www.freecodecamp.org/news/fastapi-quickstart/)

## mikael@2023-10-08

- Connected the transaction with the GL via MongoDB Atlas and ran a test
- Changed the nokio_user password in .env file

## Releases

- P1A:
  - Nicer logging with one logger for the entire module, like [Python Logging]
  - Unit test fixtures in pytest to set up and tear down test suite
  - Python API for separating presentation and logic
  - Web landing page to attract users
  - Configure amplify hosting

## References

- [Python Logging](https://betterstack.com/community/guides/logging/how-to-start-logging-with-python/)

- [FastAPI](https://fastapi.tiangolo.com/)

- [Streamlit]()

- [Namecheap](https://ap.www.namecheap.com/domains/domaincontrolpanel/nokio.org/advancedns)

- [ajv](https://ajv.js.org/)

- [Json Form](https://docs.appsmith.com/reference/widgets/json-form)
