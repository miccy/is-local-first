Example Records is a local-first database.
Records can be read and written offline. Changes survive a restart with default settings.
Every device merges its own copy.
All prior record changes are retained.
Clients can use any compatible relay, including a self-hosted relay.
Every synced record is end-to-end encrypted by default. No option disables encryption.
Synced keys are exchanged using ML-KEM and changes are signed with ML-DSA.
This library has no concept of user identities.
The client and relay are released under the MIT license.
