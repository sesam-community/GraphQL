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

##### Query specific
* \<query\>-url
* \<query\>-query

Replace \<query\> with the URL route you send with the request to the connector through the input pipe's ```source.url``` parameter.

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
      "baseurl": "https://somewebpage.com",
      "client_id": "<client ID for Azure AD authentication>",
      "client_secret": "<client secret for Azure AD authentication>",
      "person-query": "{\"query\": \"{person{id name address{streetAddress postalCode country} dateOfBirth}}\"}",
      "person-url": "/person",
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
The quotation marks in the query need to be escaped as we are already working in a json text structure.

### Example input pipe config
```
{
  "_id": "<pipe-id>",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "<system-id>",
    "url": "person"
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