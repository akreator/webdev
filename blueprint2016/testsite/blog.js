$(document).ready(function() {
  var firebase = new Firebase('https://flickering-inferno-6238.firebaseio.com/');

  function createBlogPost(post) {
    var title = $("<h1/>").text(post.title);
    var content = $("<p/>").text(post.content);
    //tiny mce: var content = $("<h1>").html(post.title);
    var footer = $("<p/>").text("Published by" + post.author + " on " + post.date);

    var blogPostHTML = $("<div/>").append([title, content, footer]);
    $("content").prepend(blogPostHTML);
  }

  firebase.on("child_added", function(snapshot) {
    var blogPost = snapshot.val();
    createBlogPost(blogPost);
  });

  $("form").on("submit", function(e) {
    e.preventDefault();

    var title = $("#title").val();
    var content = $("#content").val();
    var author = "Audrey";
    var date = new Date().toDateString();

    var blogPost = {
      title : title,
      content : content,
      author : author,
      date : date
    }
    firebase.push(blogPost);
  });
});
