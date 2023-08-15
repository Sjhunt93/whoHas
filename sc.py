from enum import Enum, auto

class Condition(Enum):
    eEquals = auto()
    eStartsWith = auto()


class ActorModel():
    id: str
    groups: str

class GroupStructure():
    class InvalidGroup(Exception):
        pass

    groups = {}
    # def __init__(self) -> None:
    #     self.groups = {}

    def set(group_name, perform_action: str, on_resource: str):
        Authoriser.set(group_name, perform_action, on_resource)

    def add_actor_to_group(actor, group_name):
        if Authoriser.probe_actor(actor):
            hash_actor = hash(actor)
            if group_name in GroupStructure.groups:
                GroupStructure.groups[group_name].insert(hash_actor)
            else:
                GroupStructure.groups[group_name] = set([hash_actor])

            if hash_actor in GroupStructure.groups:
                GroupStructure.groups[hash_actor].insert(group_name)
            else:
                GroupStructure.groups[hash_actor] = set([group_name])
            
        else:
            raise GroupStructure.InvalidGroup()

class RegisterResource:
    name: str
    actions: list   

class LocalStorage:
    def __init__(self) -> None:
        pass

class Authoriser:
    class UnhashableType(Exception):
        pass

    data = {}
    groups = []

    # an actor must be hashable
    # a resource must be hashable
    @staticmethod
    def create_hash_entires(actor, resource):
        try:
            return hash(actor), hash(resource)
        except Exception as e:
            raise Authoriser.UnhashableType("Cannot hash actor or resource type")

    
    def set(actor, perform_action: str, on_resource: str):
        hash_actor, hash_resource = Authoriser.create_hash_entires(actor, on_resource)
        if hash_actor in Authoriser.data:
            Authoriser.data[hash_actor][hash_resource].insert(perform_action)
        else:
            Authoriser.data[hash_actor] = {hash_resource : set([perform_action])}

    def can_this(actor, perform_action, on_resource, condition=Condition.eEquals):

        hash_actor, hash_resource = Authoriser.create_hash_entires(actor, on_resource)
        
        if hash_actor not in Authoriser.data:
            return False
        if hash_resource not in Authoriser.data[hash_actor]:
            return False
        groups = GroupStructure.groups.get(hash_actor, [])
        for g in groups:
            if Authoriser.can_this(g, perform_action=perform_action, on_resource=on_resource):
                return True

        return perform_action in Authoriser.data[hash_actor][hash_resource]
    
    def what_can_this_user_do(user):
        pass
    def probe_actor(actor):
        hash_value, _ = Authoriser.create_hash_entires(actor, "")
        return hash_value in Authoriser.data
    
    def save():
        pass
    #def register_group(name: str):




Authoriser.set(actor="sam", perform_action="read", on_resource="emails")
Authoriser.set(actor="peadar", perform_action="write", on_resource="emails")

GroupStructure.set(group_name="devs", perform_action="hack", on_resource="emails")
GroupStructure.add_actor_to_group(actor="sam", group_name="devs")

print(Authoriser.can_this(actor="sam", perform_action="read", on_resource="emails"))
print(Authoriser.can_this(actor="peadar", perform_action="read", on_resource="emails"))
print(Authoriser.can_this(actor="sam", perform_action="write", on_resource="emails"))
print(Authoriser.can_this(actor="peadar", perform_action="write", on_resource="emails"))
print(Authoriser.can_this(actor="sam", perform_action="hack", on_resource="emails"))
print(Authoriser.can_this(actor="peadar", perform_action="hack", on_resource="emails"))

