## fcrepo-serial-restore

Script to restore a Fedora 4 repository from the serialized form created by fcrepo4-exts/fcrepo-camel-toolbox.

The script will have the following features:
  - restore via the fcrepo REST endpoint;
  - basic HTTP authentication;
  - restore from various serializations (e.g. turtle, rdf-xml, etc.) supported by the camel-toolbox serializer.
