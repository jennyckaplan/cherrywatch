# Cherry Blossom Watch at the Brooklyn Botanic Garden

### Motivation

During the cherry blossom season, the Brooklyn Botanic Garden updates their website daily with a map of their cherry blossom garden. This map shows what stage each tree in the garden is at (Prebloom, First Bloom, Peak Bloom, and Post-Peak Bloom). I really wanted to go see the cherry blossom trees at the perfect time, but kept forgetting to check their website every day for updates. They do not have an alert system set up for letting users know via email or text whether the map has been updated. So, I decided to build my own alert system. I wanted to receive a text whenever the map had updated.

### Description

Uses Github Actions to:
- Scrape the BBG's cherry watch tracker for their data on the current state of the cherry blossom garden
- Using Jest image snapshots, takes a screenshot of the [cherry blossom map](https://www.bbg.org/collections/cherries), and determines if the image has changed from the prior snapshot
- If the image has changed (the map on their site has been updated), we alert recipients via Twilio of the updates to the garden with stats on each bloom phase and an image of the updated map.

<p align="center">
  <img src="https://user-images.githubusercontent.com/25395806/165341846-239d6da7-7f31-4266-893f-f6c4340243ed.PNG" width="400" height="auto">
</p>

After some investigation, I found the relevant area of the code that held the cherry blossom data (which is what I send via text). While I could have used this to determine if the site had been updated (since this data is what dynamically generates the map), I wanted to test out Jest Image Snapshots, since I've been using Jest at work and want to implement visual regression tests. Therefore, this system only relies on visual regression testing to determine if the map has been updated, and so far has never once failed (by sending me an update when the data hasn't actually updated). I've verified this by making sure we send the data I scraped from the site along with the map in the text to recipients.

### Generate the cherry blossom map
`yarn test`

### Update the cherry blossom map
`yarn test -u`

### Building

`cd docker && docker-compose up --build`

### Running

`cd docker && docker-compose up`
