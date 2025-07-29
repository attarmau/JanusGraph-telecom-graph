from fastapi import FastAPI
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# JanusGraph connection
graph = Graph()
conn = DriverRemoteConnection('ws://localhost:8182/gremlin', 'g')
g = graph.traversal().withRemote(conn)

@app.get("/")
def root():
    return {"status": "JanusGraph Call Frequency API is live."}

@app.get("/call-frequency")
def get_call_frequencies():
    result = g.E().hasLabel('CALLS')\
        .project('from', 'to')\
        .by(__.outV().valueMap('name', 'lat', 'lng', 'phone'))\
        .by(__.inV().valueMap('name', 'lat', 'lng', 'phone'))\
        .toList()

    freq_map = {}
    for entry in result:
        from_id = entry['from']['phone'][0]
        to_id = entry['to']['phone'][0]
        key = tuple(sorted([from_id, to_id]))
        if key not in freq_map:
            freq_map[key] = {
                "from": entry['from'],
                "to": entry['to'],
                "count": 1
            }
        else:
            freq_map[key]["count"] += 1

    return list(freq_map.values())
