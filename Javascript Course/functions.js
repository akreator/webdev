//printAWord('eylmao'); <-- this call raises error: because it is a function expression, it cannot be referenced before it is created.

var printAWord = function(word) {
  if (firstCall) {
    console.log('1)This function was declared with a function expression, and is known as an anonymous function.');
    console.log('2)This function is not processed until it is called.  As a result, it can be modified by other parts of the script.');
    console.log('3)According to the book, variables declared in here are "protected."  Let\'s find out.');
    console.log('4)Even though this method was declared here, secretWord and firstCall can be changed but MUST be declared before this function is called.');
    console.log('5)printWords does not have that luxury.');
  }
  console.log(word + secretWord);
}

var getAWord = (function() {
  console.log('1)This function is an "Immediately Invoked Function Expression," or an IIFE');
  console.log('2)This function is called as soon as the interpreter sees it -- even when running through script when processing');
  return 'a word';
}());

var secretWord = 'ass';
var firstCall = true;
printAWord('dick');
firstCall = false;
secretWord = 'butts';
printAWord('dick2');
printWords(['print', 'words']);



function printWords(words) {
  console.log('1)' + secretWord + '<-- this will be undefined until secretWord is defined (and secretWord can be changed, too)');
  for (word in words) {
    console.log(word);
  }
  console.log('2)This function was created with a function declaration and is known as a named function.');
  console.log('3)As a result, it was preloaded and can be called from anywhere in the script');
}
