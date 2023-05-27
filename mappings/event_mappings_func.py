import json
from rdflib import FOAF, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, PROV, RDFS, VOID, XSD

def load_json_file(filename):
    """
    Load JSON file and return its content as a Python dictionary.
    Args:
        filename (str): The name of the JSON file.
    Returns:
        dict: The content of the JSON file as a dictionary.
    """
    with open(filename, encoding='utf-8') as f:
        return json.load(f)



def add_event_data(json_file, g):
    
    event_uri = URIRef(f"{str(TIPD)}event/{json_file['eventId']}")
    g.add((event_uri, RDF.type, TIP.Event))
    g.add((event_uri, TIP.hasName, Literal(json_file['eventName'])))
    g.add((event_uri, TIP.hasInputEvent, Literal(json_file['inputEventIds'])))
    g.add((event_uri, TIP.hasStartDate, Literal(json_file['createdAt'])))
    return event_uri,g

def add_service_data(json_file, event_uri, g):
    
    service_uri = URIRef(f"{str(TIPD)}service/{json_file['eventId']}")
    g.add((service_uri, RDF.type, TIP.Service))
    g.add((service_uri, TIP.hasName, Literal(json_file['serviceName'])))
    g.add((service_uri, TIP.hasVersion, Literal(json_file['serviceVersion'])))
    g.add((event_uri, TIP.isProducedBy, service_uri))
    return service_uri,g
def add_saga_data(json_file, event_uri, g):
    
    saga_uri = URIRef(f"{str(TIPD)}saga/{json_file['eventId']}")
    g.add((saga_uri, RDF.type, TIP.Saga))
    g.add((saga_uri, TIP.hasName, Literal(json_file['sagaName'])))
    g.add((saga_uri, TIP.hasId, Literal(json_file['sagaId'])))
    g.add((saga_uri, TIP.hasSagaSubjectId, Literal(json_file['sagaSubjectId'])))
    g.add((event_uri, TIP.hasSaga, saga_uri))
    return g
def extract_validation_errors(json_file, event_uri, g):
    
    if json_file["data"]["validationErrors"] and len(json_file["data"]["validationErrors"]) > 0:
        errCount = 0
        for err in json_file["data"]["validationErrors"]:
            validation_uri = URIRef(f"{str(TIPD)}event/{json_file['eventId']}/error/{errCount}")
            g.add((validation_uri, RDF.type, TIP.ValidationError))
            g.add((validation_uri, TIP.hasDataPropertyPath, Literal(err["propertyPath"])))
            g.add((validation_uri, TIP.hasMessage, Literal(err["message"])))
            g.add((event_uri, TIP.hasValidationErrors, validation_uri))
            errCount += 1
    return g

def extract_klant(g, json_file) -> Graph:

  # Extract data for klant object
  klant_uri = URIRef(f"{str(TIPD)}klant/{json_file['data']['objectId']['key']['burgerservicenummer']}")


  g.add((klant_uri, RDF.type, TIP.Klant))

  # Loop over property/values in the "data" object
  skip_props = ["objectName", "objectId", "validationErrors"]
  for propPath, propValue in json_file["data"].items():
    if propPath in skip_props or not propValue:
      continue

    g.add((klant_uri, TIP[propPath], Literal(propValue)))
  return g

#%%
# Initialize graph
g = Graph()
TIP = Namespace("https://w3id.org/tip/ontology/")
TIPD = Namespace("https://w3id.org/tip/data/")
g.bind("tip", TIP)
g.bind("tipd", TIPD)

# Load JSON file
json_filename = "4_event_data_to_cdm_done_klant.json"
json_file=load_json_file("4_event_data_to_cdm_done_klant.json")

# Generate the predicate/object of the Event from the JSON content
event_uri, g = add_event_data(json_file, g)
service_uri, g = add_service_data(json_file, event_uri, g)
g = add_saga_data(json_file, event_uri, g)
g = extract_validation_errors(json_file, event_uri, g)


g = extract_klant(g, json_file)

# Save and print the graph
g.serialize("output.ttl", format="ttl")
print(g.serialize(format="ttl"))
