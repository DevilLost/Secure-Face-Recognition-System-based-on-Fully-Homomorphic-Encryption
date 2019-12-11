/**
 * 首页
 */

'use strict';

const time = document.querySelector('#time');
$(document).ready(function() {
  $("#index").fadeTo("slow", 1.0);
  time.onload = setInterval(() => time.innerHTML = new Date().toLocaleString().slice(9, 19));
})