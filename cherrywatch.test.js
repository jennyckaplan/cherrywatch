const puppeteer = require("puppeteer")
const { toMatchImageSnapshot } = require("jest-image-snapshot")

const url = 'https://www.bbg.org/collections/cherries'

describe("visual snapshots", () => {

  let browser;
  let page;

  beforeAll(async () => {
    browser = await puppeteer.launch();
  });

  it('get visual snapshot of cherry watch map', async () => {
    page = await browser.newPage();
    await page.goto(url);
    await page.waitForSelector("#cherrymap");
    const map = await page.$("#cherrymap");
    const today = new Date().toLocaleDateString().replace(/\//g, '-');
    const image = await map.screenshot({
      path: `./images/${today}.png`,
    });

    // TODO: highlight the diff each day + save
    expect(image).toMatchImageSnapshot();
  });

  afterAll(async () => {
    await page.close();
    await browser.close();
  });
});
