const puppeteer = require('puppeteer');
var fs = require('fs');


/**
 * filename generator helper
 * @param viewport
 * @param tt time type
 * @returns {string}
 */
function getFileName(viewport, tt) {
    var d = new Date();
    var date = [
        d.getUTCFullYear(),
        d.getUTCMonth() + 1,
        d.getUTCDate()
    ];
    var time = [
        d.getHours() <= 9 ? '0' + d.getHours() : d.getHours(),
        d.getMinutes() <= 9 ? '0' + d.getMinutes() : d.getMinutes(),
        d.getSeconds() <= 9 ? '0' + d.getSeconds() : d.getSeconds(),
        d.getMilliseconds()
    ];
    var resolution = viewport.width + "x" + viewport.height;
    return tt + '_' + date.join('-') + '_' + time.join('-') + "_" + resolution + '.png';
}


/**
 * Read the Cobra config
 * @type {string}
 */
if(process.argv.length < 5) {
    console.log('Usage: report.js <work_directory> <start_time> <end_time>');
    process.exit()
}
var start = process.argv[3];
var end = process.argv[4];

process.chdir(process.argv[2]);
console.log('PWD:' + process.cwd());

var config = 'config';
if(!fs.existsSync(config)){
    console.log('Critical: config not found!');
    process.exit();
}

//read config
var secret_key = null;
var cobra_ip = null;
var data = fs.readFileSync(config, "utf-8");
data.split(/\r?\n/).forEach(function (line) {
    if (line.indexOf('secret_key') !== -1) {
        secret_key = line.split('secret_key:')[1].trim();
    }
    if (line.indexOf('cobra_ip') !== -1) {
        cobra_ip = line.split('cobra_ip:')[1].trim();
    }
});
if (secret_key == null) {
    console.log('Critical: Secret key not assignment');
    process.exit()
}

/**
 * Capture
 */
var viewport = {width: 1300, height: 1000};
var tt = 'w';
var domain = 'http://' + cobra_ip + '/report?start=' + start + '&end=' + end;
var file = 'reports/' + getFileName(viewport, tt);

puppeteer.launch().then(async browser => {
    var sleep = function (time) {
    return new Promise(function (resolve, reject) {
        setTimeout(function () {
            resolve();
        }, time);
    })
};
    try {
        const page = await
        browser.newPage();
        await page.setViewport({width: 1300, height: 1000});
        await page.goto(domain);
        await sleep(1000);
        await page.screenshot({path: file});
        await browser.close();
        await console.log('Success:' + file)
    } catch (err) {
        console.log('Critical: Unable to load the address, Please check the address');
        process.exit();
    }
});


