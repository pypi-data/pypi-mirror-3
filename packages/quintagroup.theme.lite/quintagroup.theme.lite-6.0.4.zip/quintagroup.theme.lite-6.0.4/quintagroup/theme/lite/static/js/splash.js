var randnum = Math.random();
var inum = 3;
// Change this number to the number of images you are using.
var rand1 = Math.round(randnum * (inum-1)) + 1;
css = new Array;
css[1] = "/++theme++quintagroup.theme.lite/css/splash.css";
css[2] = "/++theme++quintagroup.theme.lite/css/splash1.css";
css[3] = "/++theme++quintagroup.theme.lite/css/splash2.css";
// Ensure you have an array item for every image you are using.
var cs = css[rand1];
// Deactivate cloaking device -->
//jQuery(function(){jQuery("#portal-top").css('background-image', 'url(' + image + ')')});
var headID = document.getElementsByTagName("head")[0];
var cssNode = document.createElement('link');
cssNode.type = 'text/css';
cssNode.rel = 'stylesheet';
cssNode.href = cs;
cssNode.media = 'screen';
headID.appendChild(cssNode);