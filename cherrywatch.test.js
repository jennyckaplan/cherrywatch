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

    await page.waitForSelector("#map");

    // remove the DOM nodes we don't want in the screenshot
    await page.evaluate(() => {
      const mapContainer = document.querySelector("#map");

      const elementsToRemove = document.querySelectorAll("#map > :not(.cherrystages, #cherrymap)");

      elementsToRemove.forEach((element) => {
        mapContainer.removeChild(element);
      });
    });

    const map = await page.$("#map");

    const today = new Date().toLocaleDateString().replace(/\//g, '-');
    const image = await map.screenshot({
      path: `./images/${today}.png`,
    });

    expect(image).toMatchImageSnapshot();
  });

  afterAll(async () => {
    await page.close();
    await browser.close();
  });
});
