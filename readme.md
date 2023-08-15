# whoHas

WhoHas is a minimalist approach to an RBAC (role based access control) framework. I was inspired by the simplicity of AWS's IAM system, and the very fine granularity of OSO.

WhoHas is a python client that models a similar RBAC policy to AWS IAM. Namely;
- Users have permissions on a different resources
- User can belong to groups
- Groups can have permissions just like actors.

By default all access is denied. 


## design goal

My design goal was to make this RBAC super simple. No complex DSLs to learn, minimal pip dependencies, and high customisability. The system is designed to be very fast for reads, fast for writes, and not as fast for queries.

## backends

WhoHas has been designed to decouple its runtime interface from whatever backend is storing the result. My goal was to develop 3 such backends, a local JSON based approach, a reddis cluster implementation and a DynamoDB storage solution. With different backends we get different performance tradeoffs, for example we can leverage DynamoDB's GSIs for faster group structure lookups.


