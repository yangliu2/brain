# Naive
This is a package that will use manual input of knowledge into the database
and various tools to retrieve and display that knowledge

# Neo4j 
`neo4j_db.py`  
Using neo4j graphical database to store relationships. Reading credential
from json file. 
Credential file at `brain/naive/neo4j.json` is in the format of: 
```
{
    "user": "<user name for neo4j>",
    "password": "<password for neo4j>",
    "uri": "<uri for neo4j>"
}
```

`Neo4j.create_node`  
Create a new node with the given type and name. It will check whether a node
with the same type and name exists using `Neo4j.find_node`.

`Neo4j.create_relationship`  
Create a new relationship with the given relationship, node1 type, node2 type,
node1 name, and node2 name. If will check whether a relationship between the
nodes already exists using `Neo4j.find_relationship`. 

# TODO
Check and make sure the type of nodes belongs to a specific list. If it 
doesn't, then find the closest choice to reduce duplicate types. 

Make the adding manual relationship from concept net flows better. Make sure
it doesn't quit again after 1 manual addition.

# Export data from cloud database
Use the following command in the web query to get json lines generated. Then
copy the json lines as the export.  
```CALL apoc.export.json.all(null,{useTypes:true, stream: true})```
