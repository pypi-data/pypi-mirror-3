
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
    if ($('body').hasClass('portaltype-category-navigator'))
    {
        window.location = 'next' + location.search;
    }
    else
    {
        mediaShow.goToSlide(0, slideshow);
    }
    
}

mediaShow.prevObject = function (slideshow)
{
    if ($('body').hasClass('portaltype-category-navigator'))
    {
        window.location = 'prev' + location.search;
    }
    else
    {
        mediaShow.goToSlide(slideshow.size-1, slideshow);
    }
}

//Adding custom text to the buttons
$(function(){
    $('.buttonPrev').text("Vorige");
    $('.buttonNext').text("Volgende");    
});