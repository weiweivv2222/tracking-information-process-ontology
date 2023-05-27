import json

from rdflib import FOAF, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, PROV, RDFS, VOID, XSD

# Load JSON file
# json_filename = "1_event_process_started.json"
json_filename = "4_event_data_to_cdm_done_klant.json"
with open(json_filename, encoding='utf-8') as f:
  json_file = json.load(f)

# Initialize graph
g = Graph()
TIP = Namespace("https://w3id.org/tip/ontology/")
TIPD = Namespace("https://w3id.org/tip/data/")
g.bind("tip", TIP)
g.bind("tipd", TIPD)



#%% # Generate the predicate/object of the Event from the JSON content

# Build the subject URI for the event

event_uri = URIRef(f"{str(TIPD)}event/{json_file['eventId']}")
g.add((event_uri, RDF.type, TIP.Event))
g.add((event_uri, TIP.hasName, Literal(json_file['eventName'])))
g.add((event_uri, TIP.hasInputEvent, Literal(json_file['inputEventIds'])))
g.add((event_uri, TIP.hasStartDate, Literal(json_file['createdAt'])))


# Build the subject URI for the service
service_uri = URIRef(f"{str(TIPD)}service/{json_file['eventId']}")
g.add((service_uri, RDF.type, TIP.Service))
g.add((service_uri, TIP.hasName, Literal(json_file['serviceName'])))
g.add((service_uri, TIP.hasVersion, Literal(json_file['serviceVersion'])))


# Build the subject URI for the sage
saga_uri = URIRef(f"{str(TIPD)}saga/{json_file['eventId']}")
g.add((saga_uri, RDF.type, TIP.Saga))
g.add((saga_uri, TIP.hasName, Literal(json_file['sagaName'])))
g.add((saga_uri, TIP.hasId, Literal(json_file['sagaId'])))
g.add((saga_uri, TIP.hasSagaSubjectId, Literal(json_file['sagaSubjectId'])))



g.add((event_uri, TIP.isProducedBy, service_uri))
g.add((event_uri, TIP.hasSaga, saga_uri))
print(g.serialize(format="ttl"))

#%% # Extract validation errors from data object
if json_file["data"]["validationErrors"] and len(json_file["data"]["validationErrors"]) > 0:
  errCount = 0
  for err in json_file["data"]["validationErrors"]:
    validation_uri = URIRef(f"{str(TIPD)}event/{json_file['eventId']}/error/{errCount}")
    g.add((validation_uri, RDF.type, TIP.ValidationError))
    g.add((validation_uri, TIP.hasDataPropertyPath, Literal(err["propertyPath"])))
    g.add((validation_uri, TIP.hasMessage, Literal(err["message"])))

    g.add((event_uri, TIP.hasValidationErrors, validation_uri))
    errCount += 1

#%%

# TODO: extract objectId and objectName?
#Extract objectId from data object
# if json_file["data"]["objectId"] and len(json_file["data"]["objectId"]) > 0:
#   objCount = 0
#   for obj in json_file["data"]["objectId"]:
#     object_uri = URIRef(f"{str(TIPD)}event/{json_file['eventId']}/objectId/{objCount}")
#     g.add((object_uri, RDF.type, TIP.EventData))
#     g.add((object_uri, TIP.hasDataPropertyPath, Literal(obj["mogId"])))
#     g.add((object_uri, TIP.hasMessage, Literal(obj["key"])))

#     g.add((event_uri, TIP.hasDataAttribute, object_uri))
#     objCount += 1
#%%
def extract_klant(g, json_file) -> Graph:

  # Extract data for klant object
  klant_uri = URIRef(f"{str(TIPD)}klant/{json_file['data']['objectId']['key']['burgerservicenummer']}")

  g.add((event_uri, TIP.hasData, klant_uri))

  g.add((klant_uri, RDF.type, TIP.Klant))

  # Loop over property/values in the "data" object
  skip_props = ["objectName", "objectId", "validationErrors"]
  for propPath, propValue in json_file["data"].items():
    if propPath in skip_props or not propValue:
      continue

    # data_prop_uri = URIRef(f"{str(TIPD)}event/{json_file['eventId']}/data/{propPath}")
    # g.add((data_prop_uri, RDF.type, TIP.EventData))
    # g.add((data_prop_uri, TIP.hasDataPropertyPath, Literal(propPath)))
    # g.add((data_prop_uri, TIP.hasDataValue, Literal(propValue)))

    g.add((klant_uri, TIP[propPath], Literal(propValue)))
  return g


def extract_adres(g, json_file) -> Graph:

  # Extract data for klant object
  klant_uri = URIRef(f"{str(TIPD)}adres/{json_file['data']['objectId']['key']['adresBK']}".replace(" ", "_"))

  g.add((event_uri, TIP.hasData, klant_uri))

  g.add((klant_uri, RDF.type, TIP.Address))

  # Loop over property/values in the "data" object
  skip_props = ["objectName", "objectId", "validationErrors"]
  for propPath, propValue in json_file["data"].items():
    if propPath in skip_props or not propValue:
      continue

    # data_prop_uri = URIRef(f"{str(TIPD)}event/{json_file['eventId']}/data/{propPath}")
    # g.add((data_prop_uri, RDF.type, TIP.EventData))
    # g.add((data_prop_uri, TIP.hasDataPropertyPath, Literal(propPath)))
    # g.add((data_prop_uri, TIP.hasDataValue, Literal(propValue)))

    g.add((klant_uri, TIP[propPath], Literal(propValue)))
  return g


g = extract_klant(g, json_file)
#g = extract_adres(g, json_file)

# Save and print the graph
g.serialize("output.ttl", format="ttl")
print(g.serialize(format="ttl"))
