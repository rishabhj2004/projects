var canvas= document.querySelector('canvas');
canvas.width=window.innerWidth;
canvas.height=window.innerHeight;
var c=canvas.getContext('2d');

maxRadius=5;
let numberOfCircles = Math.floor(window.innerWidth * window.innerHeight / 3000);

var colorArray=[
    'white',
    'gray'
];

var mouse={
    x:undefined,
    y:undefined
}
window.addEventListener('mousemove',function(event){
    mouse.x=event.x;
    mouse.y=event.y;
});

window.addEventListener('resize',function(){
    canvas.width=window.innerWidth;
    canvas.height=window.innerHeight;
});

window.addEventListener('mouseleave', function() {
    mouse.x = undefined;
    mouse.y = undefined;
});

function Circle(x,y,dx,dy,radius)
{
    this.x=x;
    this.y=y;
    this.dx=dx;
    this.dy=dy;
    this.radius=radius;
    this.minRadius=radius;
    this.color=colorArray[Math.floor(Math.random()*colorArray.length)];
    this.draw=function(){
        c.beginPath();
        c.arc(this.x,this.y,this.radius,0,Math.PI*2,false);
        c.fillStyle=this.color;
        c.fill();
    }
    this.update=function(){
        this.x=this.x+this.dx;
        this.y=this.y+this.dy;
        if(this.x+this.radius>innerWidth || this.x-this.radius<0)
        {
            this.dx=-(this.dx);
        }
        if(this.y+this.radius>innerHeight || this.y-this.radius<0)
        {
            this.dy=-(this.dy);
        }

        //interact with mouse
        if(mouse.x-this.x<50 && mouse.x-this.x>-50 && mouse.y-this.y<50 && mouse.y-this.y>-50)
        {
            if(this.radius<maxRadius)
            this.radius+=2;
        }
        else if(this.radius>this.minRadius){
            this.radius-=1;
        }

        this.draw();
    }
}

var circleArray=[];
for(var i=0;i<numberOfCircles;i++)
{
    var radius=(Math.random())+1;
    var x=(Math.random()*(innerWidth-radius*2))+radius;
    var y=(Math.random()*(innerHeight-radius*2))+radius;
    var dx=(Math.random()-0.5)*2;
    var dy=(Math.random()-0.5)*2;
    circleArray.push(new Circle(x,y,dx,dy,radius));
}

function animate() {
    requestAnimationFrame(animate);
    c.fillStyle = 'rgba(0, 0, 0, 0.08)';
    c.fillRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < circleArray.length; i++) {
        circleArray[i].update();
    }
}
animate();

