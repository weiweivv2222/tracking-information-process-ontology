import json
import hashlib
import glob
from rdflib import FOAF, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, PROV, RDFS, VOID, XSD

# Load JSON file
#json_filename = "1_event_process_started.json"
##json_filename = "2_event_process_finished.json"
#json_filename = "4_event_data_to_cdm_done_klant.json"
#json_filename = "4_event_data_to_cdm_done_adres.json"

# with open(json_filename, encoding='utf-8') as f:
#   json_file = json.load(f)



#%% # Initialize graph
g = Graph()
TIP = Namespace("https://w3id.org/tip/ontology/")
TIPD = Namespace("https://w3id.org/tip/data/")
g.bind("tip", TIP)
g.bind("tipd", TIPD)

# # Convert the general information of an Event

class EventGraphBuilder:
    def __init__(self, json_file):
        self.json_file = json_file
        self.event_uri = URIRef(f"{str(TIPD)}event/{json_file['eventId']}")
    
    def build_event_graph(self, g):
        g.add((self.event_uri, RDF.type, TIP.Event))
        g.add((self.event_uri, TIP.hasName, Literal(self.json_file['eventName'])))
        
        for evt in self.json_file['inputEventIds']:
            g.add((self.event_uri, TIP.hasInputEvent, URIRef(f"{str(TIPD)}event/{evt}")))
        
        g.add((self.event_uri, TIP.hasStartDate, Literal(self.json_file['createdAt'])))

        service_uri = URIRef(f"{str(TIPD)}service/{self.json_file['eventId']}")
        g.add((service_uri, RDF.type, TIP.Service))
        g.add((service_uri, TIP.hasName, Literal(self.json_file['serviceName'])))
        g.add((service_uri, TIP.hasVersion, Literal(self.json_file['serviceVersion'])))
        g.add((self.event_uri, TIP.isProducedBy, service_uri))

        if 'sagaId' in self.json_file.keys() and self.json_file['sagaId']:
            saga_uri = URIRef(f"{str(TIPD)}saga/{self.json_file['eventId']}")
            g.add((saga_uri, RDF.type, TIP.Saga))
            g.add((saga_uri, TIP.hasName, Literal(self.json_file['sagaName'])))
            g.add((saga_uri, TIP.hasId, Literal(self.json_file['sagaId'])))
            g.add((saga_uri, TIP.hasSagaSubjectId, Literal(self.json_file['sagaSubjectId'])))
            g.add((self.event_uri, TIP.hasSaga, saga_uri))

        # Extract validation errors from data object
        if "validationErrors" in self.json_file["data"].keys():
            if self.json_file["data"]["validationErrors"] and len(self.json_file["data"]["validationErrors"]) > 0:
                errCount = 0
                for err in self.json_file["data"]["validationErrors"]:
                    validation_uri = URIRef(f"{str(TIPD)}event/{self.json_file['eventId']}/error")
                    # validation_uri = URIRef(f"{str(TIPD)}event/{self.json_file['eventId']}/error/{errCount}")
                    g.add((validation_uri, RDF.type, TIP.ValidationError))
                    g.add((validation_uri, TIP.hasDataPropertyPath, Literal(err["propertyPath"])))
                    g.add((validation_uri, TIP.hasMessage, Literal(err["message"])))

                    g.add((self.event_uri, TIP.hasValidationErrors, validation_uri))
                    errCount += 1

        return g

# builder = EventGraphBuilder(json_file)
# g = builder.build_event_graph(g)
# event_uri = builder.event_uri

# g.serialize("output.ttl", format="ttl")
# print(g.serialize(format="ttl"))

# # Extract validation errors from data object


def get_object_id(objectid_dict):
  # Hash the ID with sha256 to get valid URIs
  if len(objectid_dict["key"]) != 1:
    raise ValueError(f"Too many keys found in objectId: {str(objectid_dict['key'])}")
  for _, val in objectid_dict["key"].items():
    return hashlib.sha256(str(val).encode("utf-8")).hexdigest()



def extract_object(g, data_obj, event_id):
    obj_name = data_obj.get("objectName", "EventData")
    obj_id = event_id
    
    if "objectId" in data_obj:
        try:
            obj_id = get_object_id(data_obj['objectId'])
        except ValueError as err:
            print(err)
    
    if "objectId" in data_obj and "mogId" in data_obj['objectId']:
        mog_id = data_obj['objectId']['mogId']
        g.add((event_uri, TIP.hasMogId, TIP[mog_id]))

    obj_uri = URIRef(f"{str(TIPD)}{obj_name.lower()}/{obj_id}")
    g.add((event_uri, TIP.hasData, obj_uri))
    g.add((obj_uri, RDF.type, TIP[obj_name]))

    skip_props = [
        "objectId", "objectName", "validationErrors", "objectRoot", 
        "objectSource", "objectEventId", "objectExpiredAt", "objectCreatedAt"
    ]
    for propPath, propValue in data_obj.items():
        if propPath not in skip_props and propValue:
            g.add((obj_uri, TIP[propPath], Literal(propValue)))

    return g

#%%
# read all json files from a folder
json_files = glob.glob("C:\\Users\\xg16060\\OneDrive - APG\\dev\\EDA\\tip_ontology\\src\\mappings\\*.json")

# Load and process JSON files
for json_filename in json_files:
    with open(json_filename, encoding='utf-8') as f:
        json_file = json.load(f)
    
    builder = EventGraphBuilder(json_file)
    g = builder.build_event_graph(g)
    event_uri = builder.event_uri
    g = extract_object(g, json_file["data"], json_file['eventId'])

# Save and print the graph
g.serialize("output.ttl", format="ttl")
print(g.serialize(format="ttl"))

