Cifas Integration
=================

Cifas WSDL
----------

The WSDL files can be retrieved as a zip file on the Cifas documentation website:
https://documentation.find-cifas.org.uk/Facilities/Summary/DC


They need to be placed into the `cifas/schema` folder.

### Updating the WSDL

- You need to place the new files in `cifas/schema`
- Fix the file paths in the schema files, they use relative paths to parent folders, just make everything flat
- Duplicate the `DirectServiceCIFAS.wsdl` file for the training service and replace the production URL by the UAT one and name it `TrainingDirectServiceCIFAS.wsd`
