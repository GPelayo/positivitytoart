
#pip install openai
mkdir temp
pip install SQLAlchemy --target=temp/python
cd temp
rm -r python/*.dist-info
zip -r SQLAlchemy.zip python
aws lambda publish-layer-version --layer-name sqlalchemy-test --description "The python package SqlAlchemy for PositivityToArt" --zip-file fileb://SQLAlchemy.zip --compatible-runtimes "python3.9"
#rm -rf temp

