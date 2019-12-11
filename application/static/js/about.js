'use strict';

const time = document.querySelector('#time');
$(document).ready(function () {
  $("#about").fadeTo("slow",1.0);
  time.onload=setInterval(()=>time.innerHTML=new Date().toLocaleString().slice(10,19));
  console.log(Math.random().toString(36).substring(2));
});