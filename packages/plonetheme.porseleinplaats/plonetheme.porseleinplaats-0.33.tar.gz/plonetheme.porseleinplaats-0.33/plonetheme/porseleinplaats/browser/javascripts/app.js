PorseleinApp = {};

//Fix links to keep in app mode
PorseleinApp.fixLinks = function()
{
    var a=document.getElementsByTagName("a");
    for(var i=0;i<a.length;i++) {
        if(!a[i].onclick && a[i].getAttribute("target") != "_blank") {
            a[i].onclick=function() {
                    window.location=this.getAttribute("href");
                    return false; 
            }
        }
    }
};

$(function(){
    PorseleinApp.fixLinks();
    PorseleinApp.stopBounce();
});

//Stop bouncing
PorseleinApp.stopBounce = function ()
{
    var xStart, yStart = 0;

    document.addEventListener('touchstart',function(e) {
        xStart = e.touches[0].screenX;
        yStart = e.touches[0].screenY;
    });
    
    document.addEventListener('touchmove',function(e) {
        var xMovement = Math.abs(e.touches[0].screenX - xStart);
        var yMovement = Math.abs(e.touches[0].screenY - yStart);
        if((yMovement * 3) > xMovement) {
            e.preventDefault();
        }
    });
};
