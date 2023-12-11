# Nokio user log

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

## Next steps

1. ~~Nicer logging with one logger for the entire module, like [Python Logging]~~
1. ~~Unit test fixtures in pytest to set up and tear down test suite~~
1. ~~Python API for separating presentation and logic~~
1. ~~Web landing page to attract users~~
1. ~~Configure amplify hosting~~
1. Finish the emailing belean/Sciple/Nokio to One Lambda
1. Import Bokio backup readout
1. Streamlit web page for accesing the Python FastAPI
1. AWS cognito user sign up
1. Google analytics for cash
1. ~~Favicon to website and~~
1. Create a text edit area with json validator
1. see <https://docs.appsmith.com/core-concepts/writing-code/ext-libraries>
1. Create a text edit area with and sum calculation.

## References

- [Python Logging](https://betterstack.com/community/guides/logging/how-to-start-logging-with-python/)

- [FastAPI](<https://fastapi.tiangolo.com/>)

- [Streamlit]()

- [Namecheap](https://ap.www.namecheap.com/domains/domaincontrolpanel/nokio.org/advancedns)
