# cat
Connectome Analysis Toolbox

----

Create a connection to a CATMAID instance in Python.
```
from cat.connection import Connection
c = Connection( CATMAID_URL, USERNAME, PASSWORD, CATMAID_PROJECT_ID )
c.login()
```

Retrieve a skeleton morphology, its neuron name and information about synapses
```
from cat import morphology
skeleton = morphology.get_skeleton(c, SKELETON_ID )
```

Update the skeleton graph edges with distance between to skeleton nodes
and compute the total cable length of the skeleton
```
from cat import labeling, features
labeling.update_skeleton_edge_with_distance( skeleton )
print features.get_total_cable_length( skeleton )
```