# GraphQL
Connector for Sesam to query API's that use the GraphQL query language. This version of the service authenticates through Microsoft Azure AD which provides a JWT that is added to the GraphQL request's headers.

### Environment variables
#### Required
* baseurl
* client_id
* client_secret
* grant_type
* resource
* token_url

#### Optional
* LOG_LEVEL

### Example system config
```
{
  "_id": "<system-id>",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "LOG_LEVEL": "DEBUG",
      "baseurl": "https://somewebpage.com/",
      "client_id": "<client ID for Azure AD authentication>",
      "client_secret": "<client secret for Azure AD authentication>",
      "grant_type": "client_credentials",
      "resource": "<Azure AD ID of the webapp you're querying>",
      "token_url": "https://login.windows.net/<token_service_id>/oauth2/token"
    },
    "image": "sesamcommunity/graphql:v1.0",
    "port": 5000
  },
  "verify_ssl": true
}
```
The quotation marks in the query need to be escaped as the query needs to be in json and we are already working in a json structure.

### Example input pipe config
```
{
  "_id": "<pipe-id>",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "<system-id>",
    "url": "/person?query={\"query\": \"{person{id name address{streetAddress postalCode country} dateOfBirth}}\"}"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["add", "_id",
          ["first", "_S.data.person.id"]
        ],
        ["create",
          ["apply", "create", "_S.data.person"]
        ],
        ["filter",
          ["eq", "rdf:type", "~:somesystem:person"]
        ]
      ],
      "create": [
        ["copy", "*"],
        ["add", "_id", "_S.id"],
        ["add", "rdf:type",
          ["ni", "somesystem:person"]
        ]
      ]
    }
  }
}
```
The query-string needs to have the quotation marks escaped as we're already working in a json format.