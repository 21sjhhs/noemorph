/* Optional browser regression. Usage: node tests/viewer.browser.cjs [standalone.html] [screenshot.png] */
const assert = require('node:assert/strict');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
(async () => {
  const browser = await chromium.launch({channel:'chrome',headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1000}}), errors=[];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(pathToFileURL(path.resolve(process.argv[2] || 'examples/knowledge-map.html')).href);
    await page.locator('.node').first().waitFor();
    await page.waitForTimeout(350);
    await page.locator('[data-view="all"]').click();
    await page.waitForTimeout(350);
    const camera = () => page.locator('#viewport').getAttribute('transform');
    const readCamera = value => { const [x,y,k] = value.match(/-?[\d.]+(?:e[-+]?\d+)?/g).map(Number); return {x,y,k}; };
    const burst = (deltaY,count=1,deltaMode=0) => page.evaluate(({deltaY,count,deltaMode})=>{
      const graph=document.querySelector('#graph'), r=graph.getBoundingClientRect();
      const world = document.querySelector('#viewport'), original=world.setAttribute.bind(world);
      let writes=0;world.setAttribute=(key,value)=>{if(key==='transform')writes++;return original(key,value)};
      for(let i=0;i<count;i++)graph.dispatchEvent(new WheelEvent('wheel',{deltaY,deltaMode,clientX:r.left+180,clientY:r.top+150,bubbles:true,cancelable:true}));
      return new Promise(resolve=>requestAnimationFrame(()=>{world.setAttribute=original;resolve(writes)}));
    },{deltaY,count,deltaMode});
    const r=await page.locator("#graph").boundingBox(), anchor={x:Math.trunc(r.x+180)-r.x,y:Math.trunc(r.y+150)-r.y};
    let before=readCamera(await camera());
    assert.equal(await burst(-1,100),1,'100 wheel events should cause one SVG camera paint');
    let after=readCamera(await camera());
    assert.ok(after.k>before.k,'wheel zoom should respond');
    assert.ok(Math.abs((anchor.x-before.x)/before.k-(anchor.x-after.x)/after.k)<1e-6,'pointer world X stays fixed');
    assert.ok(Math.abs((anchor.y-before.y)/before.k-(anchor.y-after.y)/after.k)<1e-6,'pointer world Y stays fixed');
    for(const deltaMode of [0,1,2]) {
      await burst(-10000,100,deltaMode);
      assert.equal(readCamera(await camera()).k,3.5);
      await burst(20,1,deltaMode);
      assert.ok(readCamera(await camera()).k<3.5,'must reverse immediately after reaching max zoom');
      await burst(10000,100,deltaMode);
      assert.equal(readCamera(await camera()).k,.08);
      await burst(-20,1,deltaMode);
      assert.ok(readCamera(await camera()).k>.08,'must reverse immediately after reaching min zoom');
    }
    await page.locator('#fit-button').click();await page.waitForTimeout(350);
    before=readCamera(await camera());
    const box=await page.locator('#graph').boundingBox();
    await page.mouse.move(box.x+180,box.y+150);await page.mouse.wheel(0,-100);await page.waitForTimeout(100);
    assert.ok(readCamera(await camera()).k>before.k,'native mouse wheel responds');
    const scale=readCamera(await camera()).k;
    await page.setViewportSize({width:1350,height:920});await page.waitForTimeout(150);
    assert.equal(readCamera(await camera()).k,scale,'window resize must not reset user zoom');
    before=readCamera(await camera());
    await page.locator('#minimap').dispatchEvent('wheel',{deltaY:-60,clientX:1100,clientY:350,bubbles:true,cancelable:true});
    await page.waitForTimeout(40);
    assert.ok(readCamera(await camera()).k>before.k,'wheel over minimap overlay still zooms the graph');
    const stable=await camera();
    const variants=await page.evaluate(()=>{const d=JSON.parse(document.querySelector('#graph-data').textContent);return d.graphs||[d]});
    for(const language of ['en','zh-CN','en','zh-CN']) {
      await page.locator(`[data-ui-lang="${language}"]`).click();
      await page.waitForTimeout(80);
      const current=readCamera(await camera());
      assert.equal(current.k,readCamera(stable).k,'language switches retain zoom');
      const variant=variants.find(g=>g.meta.language===language);
      if(variant) {
        assert.equal(await page.locator('#question-title').textContent(),variant.meta.question,'interface-follow mode selects the full matching graph');
        const issues=await page.evaluate(g=>(window.NoemorphLanguages||window.SocratesLanguages).languageIssues(g),variant);
        assert.deepEqual(issues,[],'selected content variant has no obvious untranslated prose');
      }
    }
    await page.locator('#run-settings-button').click();
    assert.equal(await page.locator('input[name="presentation_language"][value="en"]').isChecked(),true);
    assert.equal(await page.locator('input[name="presentation_language"][value="en"]').isDisabled(),true);
    await page.locator('#close-run-dialog').click();
    if(process.argv[3])await page.screenshot({path:process.argv[3],fullPage:true});
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({ok:true,nodes:await page.locator('.node').count(),wheelBurst:'100 events / 1 paint',checks:['pixel/line/page wheel','limits and reversal','pointer anchoring','native wheel','resize preserves zoom','language preserves camera','required English setting'],errors}));
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1});
