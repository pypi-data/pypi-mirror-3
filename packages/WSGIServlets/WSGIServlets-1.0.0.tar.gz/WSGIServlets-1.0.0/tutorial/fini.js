/* Copyright 2011 Daniel J. Popowich

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

*/


function popUp(url) {
    var frame = document.getElementById('popup');
    var mask = document.getElementById('mask');
    if (! (frame || mask)) return;
    var docheight = (document.height != undefined)
	                ? document.height
  	                : document.body.offsetHeight;

    var docwidth = (document.width != undefined)
	             ? document.width
	             : document.body.offsetWidth;

    //    mask.style.height = docheight + "px";
    //    mask.style.width = docwidth + "px";
    //    frame.style.height = (window.innerHeight * .8) + "px";
    frame.src = url;
    mask.style.visibility = 'visible';
}

function popUpClose() {
    var frame = document.getElementById('popup');
    var mask = document.getElementById('mask');
    if (! (frame || mask)) return;
    mask.style.visibility = 'hidden';
    frame.src = "about:blank";
}
