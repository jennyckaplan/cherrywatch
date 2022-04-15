# Cherry Blossom Watch at the Brooklyn Botanic Garden

Runs a Github Action that scrapes the BBG's cherry watch tracker
for their map and data on the current state of the cherry blossom garden. Using
Jest image snapshots, we can determine if this map has changed and alert users 
using Twilio.

### Generate the cherry blossom map
`yarn test`

### Update the cherry blossom map
`yarn test -u`

### Building

`cd docker && docker-compose up --build`

### Running

`cd docker && docker-compose up`
