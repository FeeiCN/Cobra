/**
 * Use PhantomJS to capture the report page
 *
 * @author    Feei <feei#feei.cn>
 * @homepage  https://github.com/wufeifei/cobra
 * @license   MIT, see LICENSE for more details.
 * @copyright Copyright (c) 2017 Feei. All rights reserved
 */
"use strict";
/**
 * http://phantomjs.org/api/webpage/
 *
 * Web page api
 */
var page = require('webpage').create();
/**
 * http://phantomjs.org/api/fs/
 *
 * file system api
 */
var fs = require('fs');
/**
 * http://phantomjs.org/api/system/
 *
 * system
 */
var system = require('system');

/**
 * filename generator helper
 * @param viewport
 * @param tt time type
 * @returns {string}
 */

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
if(system.args.length < 4) {
    console.log('Usage: report.js <work_directory> <start_time> <end_time>');
    phantom.exit(1);
}
var start = system.args[2];
var end = system.args[3];

// change work directory
fs.changeWorkingDirectory(system.args[1]);
console.log('PWD: ' + fs.workingDirectory);
var config_path = 'config';
// check file exists
if (!fs.exists(config_path)) {
    console.log('Critical: config not found!');
    phantom.exit(1);
}
// read config
var secret_key = null;
var cobra_domain = null;
var config = fs.read(config_path, 'utf8');
config.split(/\r?\n/).forEach(function (line) {

    if (line.indexOf('secret_key') !== -1) {
        secret_key = line.split('secret_key:')[1].trim();
    }
    if (line.indexOf('cobra_ip') !== -1) {
        cobra_domain = line.split('cobra_ip:')[1].trim();
    }
});

if (secret_key == null) {
    console.log('Critical: Secret key not assignment');
    phantom.exit(1);
}

/**
 * View Page size
 * @type {{width: number, height: number}}
 */
page.viewportSize = {width: 1300, height: 1000};
var tt = 'w';
console.log('TimeType: ' + tt);
var domain = 'http://' + cobra_domain + '/report?start=' + start + '&end=' + end;
var file = 'reports/' + getFileName(page.viewportSize, tt);
/**
 * Capture
 */
page.open(domain, function (status) {
    if (status !== 'success') {
        console.log('Critical: Unable to load the address!');
        phantom.exit(1);
    } else {
        /**
         * Draw chart need time
         */
        window.setTimeout(function () {
            page.render(file);
            console.log('Success: ' + file);
            phantom.exit();
        }, 1000);
    }
});