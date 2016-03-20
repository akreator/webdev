function foo() { /*function declarations are hoisted to top of scope*/
  function bar() { //1
    return 3;
  }
  return bar();//3
  function bar() {//2
    return 8;
  }
}
console.log(foo(); //8


function foo2() { /* function expressions are NOT hoisted -- name is loaded, but not assignment.  executed in order */
  var bar = function() {
    return 3;
  };
  return bar;
  var bar = function() {
    return 8;
  };
}
console.log(foo2()()); //bar is returned AS A FUNCTION

/* Other notes:
 - no function declarations inside non-function blocks such as if-statements
 - https://javascriptweblog.wordpress.com/2010/07/06/function-declarations-vs-function-expressions/
 - function expression preferable, although declarations are easier for debugging
   - can name anonymous functions, but doesn't work in IE

*/
