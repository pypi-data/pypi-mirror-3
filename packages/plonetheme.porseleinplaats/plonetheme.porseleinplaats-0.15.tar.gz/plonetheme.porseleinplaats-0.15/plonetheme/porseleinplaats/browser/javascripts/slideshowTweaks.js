
//Show the next slide in the given slideshow
//OVERRIDE
mediaShow.next = function (slideshowIndex)
{
  var slideshow = mediaShow.slideshows[slideshowIndex];
  if(slideshow.currentSlide + 1 <= slideshow.size - 1)
  { 
    mediaShow.goToSlide(slideshow.currentSlide + 1, slideshow); 
  }
  else
  {
    mediaShow.nextObject(slideshow);
  }
  
  return false;
}

//Show the previews slide in given slideshow
//OVERRIDE
mediaShow.prev = function (slideshowIndex)
{
  var slideshow = mediaShow.slideshows[slideshowIndex];
  if(slideshow.currentSlide - 1 >= 0)
  {
    mediaShow.goToSlide(slideshow.currentSlide - 1, slideshow);
  }
  else
  {
    mediaShow.prevObject(slideshow);
  }
  
  return false;
}

mediaShow.nextObject = function (slideshow)
{
    //if ($('body').hasClass('portaltype-category-navigator'))
    //{
    //    window.location = 'next' + location.search;
    //}
    //else
    //{
        mediaShow.goToSlide(0, slideshow);
    //}
    
}

mediaShow.prevObject = function (slideshow)
{
    //if ($('body').hasClass('portaltype-category-navigator'))
    //{
    //    window.location = 'prev' + location.search;
    //}
    //else
    //{
        mediaShow.goToSlide(slideshow.size-1, slideshow);
    //}
}


//This starts loading a slide assynchrounosly and when it finishes loading it starts the next one
mediaShow.loadSlide = function (slideshow, slideNumber)
{
    var slide = slideshow.slides[slideNumber];
    var URL = slide.url + '/get_media_show_item';
    
    if(slideshow.presentation)
    {
      URL = slide.url + '/get_media_show_item?presentation=true'
    }
    else{
      URL = slide.url + '/get_media_show_item';
    }
    
    $.getJSON(URL, function(data, textStatus, jqXHR) {
        var slideContainer = $(slideshow.obj).find(".mediaShowSlide_" + slideNumber);
        
        if (slideNumber == 4)
        {
          test = "breakpoint";
        }
        
        //var titleDiv = '<div class="mediaShowTitle"><h2><a href="'+slide.url+'">'+data.title+'</a></h2></div>';
        var descriptionDiv = "";
        if(slideshow.presentation)
        {
          descriptionDiv = '<div class="mediaShowDescription">'+$("<div />").html(data.description).text();+'</div>';
        }
        else
        {
          descriptionDiv = $('<div class="mediaShowDescription">'+data.description+'</div>');
        }
        var infoDiv = $('<div class="mediaShowInfo"></div>');
        
        infoDiv.append(descriptionDiv);
        slideContainer.append(infoDiv);
        
        //INFO: Uncomment this if you want clickable pictures
        var link = '<a class="media"></a><a class="infoButton" href="'+slide.url+'" title="info">info</a>';
        if (data.media.type == 'Video' || data.media.type == 'Youtube' || data.media.type == 'Vimeo')
        {
          var link = '<a class="media"></a>';
        }
        
        //INFO: Comment next line if you want clickable pictures 
        //var link = "<a></a>";
        
        slideContainer.append('<div class="mediaShowMedia mediaShowMediaType_'+data.media.type+'">'+link+'</div>');
        
        if (slideshow.height == 0)
        {
          slideshow.height = $(slideContainer).find(".mediaShowMedia").height();
          slideshow.width = $(slideContainer).find(".mediaShowMedia").width();
        }
        
        //TODO: Here I prepend the loader image but for now it is not working so well I need to change the loading event processing a bit no make it nicer.
        //slideContainer.find('.mediaShowMedia').prepend(mediaShow.loaderObj);
        
        slideContainer.find('.mediaShowMedia a.media').append(mediaShow.getMediaObject(data.media, slideshow));
        
        if(slideshow.presentation)
        {
          slideContainer.find('.mediaShowDescription').css({'top': '50%', 'margin-top': -(slideContainer.find('.mediaShowDescription').height()/2)});
        }
        
        slide.loaded = mediaShow.LOADED;
        mediaShow.loadNext(slideshow);
    });
}

//Adding custom text to the buttons
$(function(){
    $('.buttonPrev').text("Vorige");
    $('.buttonNext').text("Volgende");    
});