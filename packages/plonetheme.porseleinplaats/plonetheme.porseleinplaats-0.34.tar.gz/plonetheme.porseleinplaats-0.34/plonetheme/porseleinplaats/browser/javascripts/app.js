//Definition of a page
function Page ()
{
    this.obj = $('<div class="page"></div>');
    this.loaded = false;
    this.URL = null;
}

Page.prototype.load = function ()
{
    if (this.URL !== null)
    {
        
    }
}
//================


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

PorseleinApp.getQueryVariable = function(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split('&');
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split('=');
        if (decodeURIComponent(pair[0]) == variable) {
            return decodeURIComponent(pair[1]);
        }
    }
    return null
}

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
        
        /*
        xStart = e.touches[0].screenX;
        yStart = e.touches[0].screenY;
    
        var xScroll = 0;
        var currentValue = $('.h_scroll').css("margin-left");
        
        //console.log("XMovement: " + xMovement);
        if(typeof currentValue !== 'undefined')
        {
            xScroll = parseInt(currentValue.replace("px", "")) + xMovement;
        }
        else
        {
            xScroll = xMovement ;
        }
        
        if(xScroll > -($('.h_scroll').width() - screen.width) && xScroll <= 0 )
        {
            $('.h_scroll').css("margin-left", xScroll);
        }
        
        e.preventDefault();
        */
        
        
        //console.log("mov: " + xMovement + " / " + yMovement);
        if (xMovement <= yMovement)
        {
            e.preventDefault();
        }
        
    });
};

$(function(){
    PorseleinApp.fixLinks();
    PorseleinApp.stopBounce();
});



// Temporary stuff
//=================================

//Stores the current pages, basically keeps the content
PorseleinApp.pages = [];

//Checks for existing pages on the current content and syncs the arry to that
PorseleinApp.sync = function ()
{
    
}

//Checks if the page exists
PorseleinApp.find = function()
{
    for (page in this.pages)
    {
        
    }
}

//Ads a page to the end of the stack, returns the position of the new page
PorseleinApp.addPage = function(page)
{
    PorseleinApp.pages.push(page);
    return PorseleinApp.pages.length -1;
};

//Removes a page from the stack
PorseleinApp.removePage = function (position)
{
    
};

//Move a page to a new position
PorseleinApp.movePage = function(origin, destination)
{
    
};

//Initialize everything and prepare for operation
PorseleinApp.init = function()
{
    
};

//Touchstart event
PorseleinApp.touchstart = function (e)
{
    
};

//Touchmove event
PorseleinApp.touchmove = function(e)
{
    
};

//Register the events
PorseleinApp.registerEvents = function(e)
{
    
};

//=================================
