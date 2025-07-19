var canvas= document.querySelector('canvas');
canvas.width=window.innerWidth;
canvas.height=window.innerHeight;
var c=canvas.getContext('2d');

window.addEventListener('resize',function(){
    canvas.width=window.innerWidth;
    canvas.height=window.innerHeight;
});

var x=innerWidth/2;
var y=innerHeight/2;
var dx=2;
var dy=2;
var radius=30;

function circle(x,y,dx,dy,radius)
{
    this.x=x;
    this.y=y;
    this.dx=dx;
    this.dy=dy;
    this.radius=radius;
    this.draw=function(){
        c.beginPath();
        c.arc(this.x,this.y,this.radius,0,Math.PI*2,false);
        c.fillStyle='black';
        c.fill();
        c.stroke()
    }
}

var obj=new circle(x,y,dx,dy,radius)

function animate()
{
    requestAnimationFrame(animate);
    c.clearRect(0,0,innerWidth,innerHeight);
    c.fillStyle = 'white'; 
    obj.draw();
    
}

animate();
