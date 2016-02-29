console.log("Running test.js")

var a = [1, 2, 3, 4, 5];

var a = [1, "two", 3];

var a = function(text) {
  console.log("function called");
  console.log(text);
}

a('hello!');

var a = {};
a["hello"] = "hey";
a["hi"] = "wooo";

var a = {
  "hello" : "no",
  "a" : "b",
  "cool" : function(x) {
    console.log("X is: ");
    console.log("x");
  };
}

a[cool]("stuff");

function sayhi() {
  console.log("hi");
}


console.log("RUNNING");


if (5 == "5") { //check same value
  console.log("true");
}

if (5 === "5") { //check same value AND type
  console.log("true");
}

while (i++ < 5) {
  console.log("hey");
}
