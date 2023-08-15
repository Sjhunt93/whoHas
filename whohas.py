from abc import ABC
from hashlib import md5
import json
from enum import Enum, auto


class OutputHelper():
    def format_actions(action):
        return "any action" if action == "*" else action
    def format_resource(resource):
        return "any resource" if resource == "*" else f"{resource} resource"

class Hasher:
    HashType = 'plain' # or md5
    class UnhashableType(Exception):
        pass
    def create_hash(var):
        try:
            if Hasher.HashType == "plain":
                return var
            elif Hasher.HashType == "md5":
                return md5(json.dumps(var).encode()).hexdigest()
            else:
                raise Hasher.UnhashableType(f"HashType not configured")    
        except Exception as e:
            raise Hasher.UnhashableType(f"Cannot hash type {type(var)}")

class AuthoriserBackend(ABC):
    class Queries:
        class Types(Enum):
            actor = auto
            role = auto
            group = auto
            resource = auto
        #class Condition(Enum):




    # the backend allows the end-user to choose a database or local storage device
    # actor and resource are hashable types (so str)
    # for performance reasons do as little validation in the backend as possible
    # action should be str
    def __init__(self, backendId) -> None:
        self.backendId = backendId
    def set_role(self, actor, resource, action):
        pass
        
    def check_role(self, actor, resource, action):
        pass

    def actor_exists(self, actor):
        pass
    def add_actor_to_group(self, actor, group_name):
        pass
    
    def groups_for_actor(self, group_name):
        pass

    # def query(self, actor, )
    # depending on your backend you might have to save and load the data
    # for example if you use dynamodb then save/load makes 0 sense
    def save():
        pass
    def load():
        pass

class JsonBackend(AuthoriserBackend):
    # the backend allows the end-user to choose a database or local storage device
    def __init__(self, backendId) -> None:
        super().__init__(backendId)
        self.data_structure = {}
        self.groups = {}
    
    def set_role(self, actor: str, resource: str, action: str):
        if actor in self.data_structure:
            if resource in self.data_structure[actor]:
                self.data_structure[actor][resource].add(action)
            else:
                self.data_structure[actor][resource] = set([action])
        else:
            self.data_structure[actor] = {resource : set([action])}

    
    
    def check_role(self, actor, resource, action):

        # we use this helper to avoid recursion
        def check_role_helper(data_structure: dict, actor, resource, action):
            
            if actor not in data_structure:
                return False
            if "*" in data_structure[actor]:
                if action in data_structure[actor]["*"]:
                    return True
            if resource not in data_structure[actor]:
                return False
            return action in data_structure[actor][resource] or "*" in data_structure[actor][resource]

        if check_role_helper(self.data_structure, actor, resource, action):
            return True
        
        groups = self.groups_for_actor(actor)
        for g in groups:
            if check_role_helper(self.data_structure, g, resource, action):
                return True
        return False
    
    def actor_exists(self, actor):
        return actor in self.data_structure
    
    def add_actor_to_group(self, actor, group_name):
        # we maintain two lists here
        # 1. the users belonging to a given group
        if group_name in self.groups:
            self.groups[group_name].add(actor)
        else:
            self.groups[group_name] = set([actor])

        # 2. the groups a user belongs to
        if actor in self.groups:
            self.groups[actor].add(group_name)
        else:
            self.groups[actor] = set([group_name])

    def groups_for_actor(self, group_name):
        return self.groups.get(group_name, [])
    
    def query_actor(self, actor):
        output = []
        permissions = self.data_structure.get(actor, {})
        print(permissions)
        for resource, actions in permissions.items():
            print("\t", resource, actions)
            for a in actions:
                output.append(f"Can perform {OutputHelper.format_actions(a)} on resource {OutputHelper.format_resource(resource)}")
        groups = self.groups_for_actor(actor)
        for g in groups:
            perms = self.data_structure.get(g, {})
            for resource, actions in perms.items():
                for a in actions:
                    output.append(f"Can perform {OutputHelper.format_actions(a)} on resource {OutputHelper.format_resource(resource)}")
            
        print(permissions)
        return output

    def save():
        pass
    def load():
        pass

class AuthoriserInterface:
    class InvalidGroupStructure(Exception):
        pass

    def __init__(self, backend: AuthoriserBackend) -> None:
        self.backend = backend

    def allow(self, actor, to_perform_action, on_resource):
        self.backend.set_role(
            actor=Hasher.create_hash(actor),
            resource=Hasher.create_hash(on_resource),
            action=to_perform_action
        )
    
    def allow_group(self, group_name: str, to_perform_action, on_resource):
        self.allow(group_name, to_perform_action, on_resource)

    def add_actor_to_group(self, actor, group_name):
        if not self.backend.actor_exists(Hasher.create_hash(group_name)):
            raise AuthoriserInterface.InvalidGroupStructure("group does not exists")
        self.backend.add_actor_to_group(Hasher.create_hash(actor), Hasher.create_hash(group_name))


    def can_this(self, actor, perform_action, on_resource):
        
        return self.backend.check_role(
            actor=Hasher.create_hash(actor), 
            resource=Hasher.create_hash(on_resource),
            action=perform_action
        )
    def query():
        pass

    def save():
        pass
    

Hasher.HashType == "plain"
assert Hasher.create_hash("hello") == Hasher.create_hash("hello")

backend = JsonBackend("test")
auth_interface = AuthoriserInterface(backend)


auth_interface.allow(actor="sam", to_perform_action="s3:read", on_resource="test-bucket")
assert auth_interface.can_this(actor="sam", perform_action="s3:read", on_resource="test-bucket")
assert not auth_interface.can_this(actor="tim", perform_action="s3:read", on_resource="test-bucket")

auth_interface.allow_group(group_name="hackers", to_perform_action="bug:fix", on_resource="repos")
auth_interface.add_actor_to_group("sam", "hackers")

assert auth_interface.can_this(actor="sam", perform_action="bug:fix", on_resource="repos")


# wildcard tests
auth_interface.allow(actor="lars", to_perform_action="s3:read", on_resource="*")
assert auth_interface.can_this(actor="lars", perform_action="s3:read", on_resource="prod-logs")

auth_interface.allow(actor="lars", to_perform_action="*", on_resource="api-key-table")
assert auth_interface.can_this(actor="lars", perform_action="delete", on_resource="api-key-table")


auth_interface.allow_group(group_name="k8devs", to_perform_action="k8:update", on_resource="*")
auth_interface.allow_group(group_name="k8devs", to_perform_action="k8:delete", on_resource="*")
auth_interface.allow_group(group_name="k8devs", to_perform_action="k8:monitor", on_resource="*")
auth_interface.allow_group(group_name="k8devs", to_perform_action="k8:create", on_resource="*")
auth_interface.add_actor_to_group("lars", "k8devs")
for action in ["k8:update", "k8:create", "k8:monitor", "k8:delete"]:
    assert auth_interface.can_this("lars", action, on_resource="super-cluster-2")

assert not auth_interface.can_this("lars", "k8:destroy", on_resource="super-cluster-2")

items = auth_interface.backend.query_actor("lars")
for i in items:
    print(i)