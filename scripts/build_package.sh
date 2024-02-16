echo BUILDING DEPLOYMENT PACKAGE .ZIP
mkdir -p package
pip install --target ./package/ -r requirements/prod.txt
zip -r ./deployment_package.zip ./package/
cd app
zip ../deployment_package.zip lambda_function.py