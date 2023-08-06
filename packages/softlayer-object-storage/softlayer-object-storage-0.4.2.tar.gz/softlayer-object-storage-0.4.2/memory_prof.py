import object_storage
sl_storage = object_storage.get_client('kmcdonald:user1', '2VRXIpqiyoxU', datacenter='dal05')

import objgraph
objgraph.show_refs([sl_storage], filename='client.png')
container = sl_storage['test']
objgraph.show_refs([container], filename='container.png')

obj = container['test']
objgraph.show_refs([obj], filename='obj.png')
