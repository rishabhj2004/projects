var canvas= document.querySelector('canvas');
canvas.width=window.innerWidth;
canvas.height=window.innerHeight;
var c=canvas.getContext('2d');
//var x=90;
//var y=100;
//var width=80;
//var height=70;
//c.fillStyle='rgba(0,0,70,0.2)';
//c.fillRect(x,y,width,height);
//c.fillStyle='rgba(200,0,70,0.3)';
//c.fillRect(170,170,width,height);
//console.log("canvas");
//
//c.beginPath();
//c.moveTo(300,700);
//c.lineTo(400,600);
//c.strokeStyle='rgba(0,40,0,0.5)';
//c.stroke();
//c.beginPath();
//c.moveTo(70,200);
//c.lineTo(80,300);
//c.lineTo(100,600);
//c.strokeStyle="blue";
//c.stroke();
//
//for(var i=0;i<900;i++){
//    var x=Math.random()*window.innerWidth;
//    var y=Math.random()*window.innerHeight;
//    var a=Math.random()*255;
//    var b=Math.random()*255;
//    var n=Math.random()*255;
//    c.beginPath();
//    c.arc(x,y,30,0,Math.PI*2,false);
//    c.strokeStyle='rgba(90,70,67,1)';
//    c.fillStyle=`rgba(${a},${b},${n},0.5)`;
//    c.fill();
//    c.stroke();
//}
//
//c.beginPath();
//c.arc(x,y,30,0,Math.PI*2,false);
//c.strokeStyle='rgba(90,70,67,1)';
//c.fillStyle=`rgba(90,90,0,0.1)`;
//c.fill();
//c.stroke();
//x=x+dx;
//y=y+dy;
//if(x+30>innerWidth || x-30<0)
//{
//    dx=-(dx);
//}
//if(y+30>innerHeight || y-30<0)
//{
//    dy=-(dy);
//}
maxRadius=40;
var colorArray=[
    '#00b3b3',
    '#7f00ff',
    '#00bfff',
    '#ffd700',
    '#ff69b4'
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
        c.stroke();
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
for(var i=0;i<1000;i++)
{
    var radius=(Math.random()*8)+1;
    var x=(Math.random()*(innerWidth-radius*2))+radius;
    var y=(Math.random()*(innerHeight-radius*2))+radius;
    var dx=(Math.random()-0.5)*2;
    var dy=(Math.random()-0.5)*2;
    circleArray.push(new Circle(x,y,dx,dy,radius));
}

function animate()
{ 
    c.clearRect(0,0,innerWidth,innerHeight);
    requestAnimationFrame(animate);
    c.fillStyle = 'white'; 
    c.fillRect(0, 0, canvas.width, canvas.height);
    for(var i=0;i<circleArray.length;i++)
    {
        circleArray[i].update();
    }
}
animate();

