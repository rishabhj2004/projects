var canvas = document.querySelector('canvas');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
var c = canvas.getContext('2d');

window.addEventListener('resize', function () {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

var dx = 0;
var sdx =0
let spacePressed=false;
window.addEventListener("keydown", function (e) {
    
        console.log(e.keyCode);
        console.log(e.key);
    
    if (e.keyCode == 37) {
        circle.dx = -3;
        circle1.sdx=-3;
    }
    if (e.keyCode == 39) {
        circle.dx = 3;
        circle1.sdx=3;
    }   

    if (e.keyCode == 32) {
        spacePressed = true;
        if(circle.y + circle.radius >= floor) {
            circle.jumpcount+=1;
            circle.dy = -12;
            circle1.sdy=-12
        }
        else{
            if(circle.jumpcount<2){
                circle.dy=-12;
                circle.jumpcount+=1;
                circle1.sdy=-12
            }
        }
    }
    
});

window.addEventListener("keyup", function (e) {
    if (e.keyCode == 37 || e.keyCode == 39) {
        circle.dx = 0;
        circle1.sdx=0;
    }
    if (e.keyCode == 32) {
        spacePressed = false;
    }
});

var x = 200;
var y = 200;
var dy = 2;
var radius = 30;
var color = 'red';
var floor = canvas.height-100;
var gravity = 0.5;

var sx = 200;
var sy = 200;
var sdy = 2;
var sradius = 10;
var scolor = 'blue';
var sfloor = canvas.height-100;
var sgravity = 0.5;

function Circle(x, y, dx, dy, radius, gravity,color) {
    this.x = x;
    this.y = y;
    this.dx=dx;
    this.dy = dy;
    this.radius = radius;
    this.gravity = gravity;
    this.jumpcount=0;
    this.color=color;

    this.draw = function () {
        c.beginPath();
        c.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
        c.fillStyle = color;
        c.fill();
    }

    this.update = function () {
        this.dy +=gravity;
        this.x += this.dx;

        if (this.y + this.radius + this.dy <= floor) {
            this.y += this.dy;
        } else {
            this.y = floor - this.radius;
            this.dy = 0;
            this.jumpcount=0;
        }

        if (this.x - this.radius < 0) this.x = this.radius;
        if (this.x + this.radius > canvas.width) this.x = canvas.width - this.radius;

        this.draw();
    }
}

var circle = new Circle(x, y, dx, dy, radius, gravity,color);
var circle1 = new Circle(sx, sy, sdx, sdy, sradius, sgravity,scolor);

function animate() {
    c.clearRect(0, 0, innerWidth, innerHeight);
    requestAnimationFrame(animate);

    c.fillStyle = 'black';
    c.fillRect(0, 0, canvas.width, canvas.height);

    c.fillStyle = 'white';
    c.fillRect(0, floor, canvas.width, canvas.height);
    circle.update();
    circle1.update();
}
animate();


