import url_utils as url

class Node(object):
    def __init__(self, ovh_object):
        for k, v in ovh_object.items():
	    setattr(self, k, v)
    def __str__(self):
        return str(self.__dict__)


class Nodes(object):

    def __init__(self, api, path):
        self.nodes = []
        node_ids = api.get(path)
        ### If IDs list
        if isinstance(node_ids, list):
            for n_id in node_ids:
                n = Node(api.get(url.join(path, n_id)))
                if Node is not None:
                    self.nodes.append(n)
        ### If immediate entity
        elif isinstance(node_ids, dict):
            self.nodes.append(Node(node_ids))
        ### Automatic sorting
        self.sort()
    
    def items(self):
        return self.nodes

    def sort(self):
        if not self.nodes:
            return self
        if any(att.lower() == 'name' for att in self.nodes[0].__dict__.keys()):
            self.nodes.sort(key=lambda node: node.name, reverse=False)
        elif any(att.lower() == 'date' for att in self.nodes[0].__dict__.keys()):
            self.nodes.sort(key=lambda node: node.date, reverse=True)
        elif any(att.lower() == 'id' for att in self.nodes[0].__dict__.keys()):
            self.nodes.sort(key=lambda node: node.id, reverse=False)
        return self

    def __repr__(self):
        txt = ''
        for n in self.nodes:
            txt += str(n)
        return txt

