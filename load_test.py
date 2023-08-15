from random import seed
from random import randint
from whohas import AuthoriserInterface, JsonBackend
seed(1)



auth_interface = AuthoriserInterface(JsonBackend("123"))

for _ in range(10000):
    a = randint(0, 100000)
    b = randint(0, 100000)
    user = f"user_{a}_{b}"
    resource = f"resource_{a}_{b}"
    auth_interface.allow(user, "owns", resource)


assert auth_interface.can_this(user, "owns", resource)

