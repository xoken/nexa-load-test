# Load Tests for Nexa using Locust

### Deployment
`locust -f <file> --host <host>`

### Configuration
Session key should be updated in `testConfig.ini`. 

Update blocksSynced to reflect best-synced if you wish to avoid querying blocks that may not have been synced
