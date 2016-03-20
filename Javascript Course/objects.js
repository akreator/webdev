function Plant(type, name, age, color, parents) {
  this.type = type;
  this.name = name;
  this.age = age;
  this.color = color;
  this.parents = parents;
  this.reproduce = function(plant, name) {
    if (plant.type == this.type) {
      return new Plant(this.type, name, 0, (plant.color + this.color) / 2, [this, plant]);
    }
  };
}

var james = new Plant('cactus', 'James', 12, '#9ce1b0');
var brian = new Plant('cactus', 'Brian', 10, '#50835e');
var child = brian.reproduce(james, 'child');

console.log(james);
console.log('loaded');

var test = document.getElementById('content');
test.textContent = 'loaded';


var human = {
  name : 'alexis',
  age : '17',
  hometown : 'somewhere in texas',
  birthday : new Date(),
  wishHappyBirthday : function() {
    if (new Date() == this.birthday) {
      console.log("Happy birthday, " + this.name + "!");
    }
  }
};

var gameboard = {
  size : 4,
  tiles : (function() {
    return this.size * this.size;
  })
}
