# Cherry Blossom Watch at the Brooklyn Botanic Garden

### Motivation

During the cherry blossom season, the Brooklyn Botanic Garden updates their website daily with a map of their cherry blossom garden. This map shows what stage each tree in the garden is at (Prebloom, First Bloom, Peak Bloom, and Post-Peak Bloom). I really wanted to go see the cherry blossom trees at the perfect time, but kept forgetting to check their website every day for updates. They do not have an alert system set up for letting users know via email or text whether the map has been updated. So, I decided to build my own alert system. I wanted to receive a text whenever the map had updated.

Update (2024): for this year, I wanted less alerts (sometimes the map would update multiple times per day), so I only run the action once a day in the morning. 

### Description

Uses Github Actions to:
- Scrape the BBG's cherry watch tracker for their data on the current state of the cherry blossom garden
- Using Jest image snapshots, takes a screenshot of the [cherry blossom map](https://www.bbg.org/collections/cherries), and determines if the image has changed from the prior snapshot
- If the image has changed (the map on their site has been updated), we alert recipients via Twilio of the updates to the garden with stats on each bloom phase and an image of the updated map.

<p align="center">
  <img src="https://user-images.githubusercontent.com/25395806/165341846-239d6da7-7f31-4266-893f-f6c4340243ed.PNG" width="400" height="auto">
</p>

Update (2024):
<p align="center">
  <img src="https://github.com/jennyckaplan/cherrywatch/assets/25395806/7dbfc3b5-7387-4c15-9591-f064fca1ad26" width="400" height="auto">
</p>


After some investigation, I found the relevant area of the code that held the cherry blossom data (which is what I send via text). While I could have used this to determine if the site had been updated (since this data is what dynamically generates the map) by storing it and comparing it to the previous data each time, I wanted to test out Jest Image Snapshots (and using Jest regression testing means I don't need to have any sort of database!). Therefore, this system only relies on visual regression testing to determine if the map has been updated, and so far has never once failed (by sending me an update when the data hasn't actually updated). I've verified this by making sure we send the data I scraped from the site along with the map in the text to recipients.

Update (2024): For this year, instead of just giving an overall percentage of the number of trees in each bloom phase, I realized that the Japanese garden's trees typically bloom much earlier than the main strip of Kanzan trees. Because of this, I'm experimenting with only sending the tree types that are 80% or more in Peak Bloom so you can see what trees are actually in full bloom at any point in time (and you have the map data, so you can also visually see where they are at the garden). I also added the BBG link to the tree type's images so you can see exactly what that type of tree looks like at each bloom stage!

### Generate the cherry blossom map
`yarn test`

### Update the cherry blossom map
`yarn test -u`

### Building

`cd docker && docker-compose up --build`

### Running

`cd docker && docker-compose up`
