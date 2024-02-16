# dolarpan-scraper
This serverless function returns VEF/USD exchange rates, deployed in AWS Lambda.
The data is scrapped from telegram channels web page.

### Steps:

Create virtual environment:
```commandline
python3 -m venv venv
```

Install requirements for production:
```commandline
pip install -r ./requirements/prod.txt
```

To create .zip deployment package:
```commandline
chmod +x ./scripts/build_package.sh
./scripts/build_package.sh
```
