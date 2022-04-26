# Cherry Blossom Watch at the Brooklyn Botanic Garden

Uses Github Actions to:
- Scrape the BBG's cherry watch tracker for their data on the current state of the cherry blossom garden
- Using Jest image snapshots, takes a screenshot of the [cherry blossom map](https://www.bbg.org/collections/cherries), and determines if the image has changed from the prior snapshot
- If the image has changed (the map on their site has been updated), we alert recipients via Twilio of the updates to the garden with stats on each bloom phase and an image of the updated map.

<img src="https://user-images.githubusercontent.com/25395806/165341846-239d6da7-7f31-4266-893f-f6c4340243ed.PNG" width="400" height="auto">

### Generate the cherry blossom map
`yarn test`

### Update the cherry blossom map
`yarn test -u`

### Building

`cd docker && docker-compose up --build`

### Running

`cd docker && docker-compose up`
