import json

from rdflib import FOAF, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, PROV, RDFS, VOID, XSD

# Load JSON file
# json_filename = "1_event_process_started.json"
# json_filename = "2_event_process_finished.json"
# json_filename = "4_event_data_to_cdm_done_klant.json"
json_filename = "4_event_data_to_cdm_done_adres.json"

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
input_events = []
for evt in json_file['inputEventIds']:
  g.add((event_uri, TIP.hasInputEvent, URIRef(f"{str(TIPD)}event/{evt}")))

g.add((event_uri, TIP.hasStartDate, Literal(json_file['createdAt'])))


# Build the subject URI for the service
service_uri = URIRef(f"{str(TIPD)}service/{json_file['eventId']}")
g.add((service_uri, RDF.type, TIP.Service))
g.add((service_uri, TIP.hasName, Literal(json_file['serviceName'])))
g.add((service_uri, TIP.hasVersion, Literal(json_file['serviceVersion'])))
g.add((event_uri, TIP.isProducedBy, service_uri))

# Build the subject URI for the saga
if 'sagaId' in json_file.keys() and json_file['sagaId']:
  saga_uri = URIRef(f"{str(TIPD)}saga/{json_file['eventId']}")
  g.add((saga_uri, RDF.type, TIP.Saga))
  g.add((saga_uri, TIP.hasName, Literal(json_file['sagaName'])))
  g.add((saga_uri, TIP.hasId, Literal(json_file['sagaId'])))
  g.add((saga_uri, TIP.hasSagaSubjectId, Literal(json_file['sagaSubjectId'])))
  g.add((event_uri, TIP.hasSaga, saga_uri))


#%% # Extract validation errors from data object
if "validationErrors" in json_file["data"].keys():
  if json_file["data"]["validationErrors"] and len(json_file["data"]["validationErrors"]) > 0:
    errCount = 0
    for err in json_file["data"]["validationErrors"]:
      validation_uri = URIRef(f"{str(TIPD)}event/{json_file['eventId']}/error")
      # validation_uri = URIRef(f"{str(TIPD)}event/{json_file['eventId']}/error/{errCount}")
      g.add((validation_uri, RDF.type, TIP.ValidationError))
      g.add((validation_uri, TIP.hasDataPropertyPath, Literal(err["propertyPath"])))
      g.add((validation_uri, TIP.hasMessage, Literal(err["message"])))

      g.add((event_uri, TIP.hasValidationErrors, validation_uri))
      errCount += 1


def get_object_id(objectid_dict):
  if len(objectid_dict["key"]) != 1:
    raise f"Too many keys found in objectId: {str(objectid_dict['key'])}"
  for _, val in objectid_dict["key"].items():
    if isinstance(val, str):
      return val.replace(" ", "_")
    else:
      return val


def extract_object(g, data_obj, event_id) -> Graph:
  obj_name = "EventData"
  if "objectName" in data_obj.keys() and data_obj["objectName"]:
    obj_name = data_obj["objectName"]

  try:
    obj_id = get_object_id(data_obj['objectId'])
  except Exception as err: 
    obj_id = event_id

  try:
    mog_id = data_obj['objectId']['mogId']
    g.add((event_uri, TIP.hasMogId, TIP[mog_id]))
  except Exception as err: 
    pass

  obj_uri = URIRef(f"{str(TIPD)}{obj_name.lower()}/{obj_id}")

  g.add((event_uri, TIP.hasData, obj_uri))
  g.add((obj_uri, RDF.type, TIP[obj_name]))

  # Loop over property/values in the "data" object, 
  # and skip generic data object properties like objectId, objectName
  skip_props = [
    "objectId", "objectName", "validationErrors", "objectRoot", 
    "objectSource", "objectEventId", "objectExpiredAt", "objectCreatedAt"
  ]
  for propPath, propValue in data_obj.items():
    if propPath in skip_props or not propValue:
      continue
    g.add((obj_uri, TIP[propPath], Literal(propValue)))
  return g




g = extract_object(g, json_file["data"], json_file['eventId'])

# Save and print the graph
g.serialize("output.ttl", format="ttl")
print(g.serialize(format="ttl"))
