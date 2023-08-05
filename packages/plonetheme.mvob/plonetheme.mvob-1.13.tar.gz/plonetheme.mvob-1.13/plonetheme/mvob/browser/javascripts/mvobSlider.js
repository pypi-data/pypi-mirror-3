MVOBSlider = {};
MVOBSlider.blocks = [];
MVOBSlider.links = [];
MVOBSlider.descriptions = [];
MVOBSlider.titles = [];
MVOBSlider.currentBlock = -1;
MVOBSlider.buttonNext;
MVOBSlider.buttonPrev;

MVOBSlider.getMediaLinks = function ()
{
    jq(".sliderInfo img").each(function (){
       MVOBSlider.links[MVOBSlider.links.length] = jq(this).attr("src"); 
       MVOBSlider.currentBlock++;
    });
    
    jq(".sliderInfo h2").each(function (){
        MVOBSlider.titles[MVOBSlider.titles.length] = jq(this).text();
    });
    
    
    jq(".sliderInfo h3").each(function (){
        MVOBSlider.descriptions[MVOBSlider.descriptions.length] = jq(this).html();
    });
    
    if(MVOBSlider.currentBlock >= 0)
    {
        jq('.sliderBox').css('display', 'block');
    }
    //MVOBSlider.addCounters();
    
    MVOBSlider.links = MVOBSlider.links.reverse();
    MVOBSlider.descriptions = MVOBSlider.descriptions.reverse();
    MVOBSlider.titles = MVOBSlider.titles.reverse();
}

MVOBSlider.addCounters = function ()
{
    for (var i=0; i< MVOBSlider.titles.length; i++)
    {
        MVOBSlider.titles[i] += " (" + (i+1) + "/" + MVOBSlider.titles.length + ")";
    }
}

MVOBSlider.next = function ()
{
    if(MVOBSlider.currentBlock > 0)
    {
        MVOBSlider.scrollTo(MVOBSlider.currentBlock - 1);
    }
    else
    {
        MVOBSlider.scrollTo(MVOBSlider.blocks.length-1);
    }
    return false;
}

MVOBSlider.prev = function ()
{
    if(MVOBSlider.currentBlock < MVOBSlider.blocks.length-1)
    {
        MVOBSlider.scrollTo(MVOBSlider.currentBlock + 1);
    }
    else
    {
        MVOBSlider.scrollTo(0);
    }
    return false;
}

MVOBSlider.addButtons = function ()
{
    if(MVOBSlider.links.length > 1)
    {
        var prevLink = document.createElement('a');
        var nextLink = document.createElement('a');
        jq(nextLink)
            .addClass("slider-next-button")
            .attr('href', '#')
            .click(function(){return MVOBSlider.next()})
            .text("verder >");
        jq(prevLink)
            .addClass("slider-prev-button")
            .attr('href', '#')
            .click(function(){return MVOBSlider.prev()})
            .text("< terug");
        
        /*var nextImg = new Image();
        jq(nextImg)
            .addClass("slider-next-button")
            .attr('src', 'buttonNextBig.jpg')
            .click(function(){MVOBSlider.next()});
        var prevImg = new Image();
        jq(prevImg)
            .addClass("slider-prev-button")
            .attr('src', 'buttonPrevBig.jpg')
            .click(function(){MVOBSlider.prev()});*/
            
        jq('#slider-media-album').append(prevLink);
        jq('#slider-media-album').append(nextLink);
        MVOBSlider.buttonNext = nextLink;
        MVOBSlider.buttonPrev = prevLink;
        //jq(".slider-prev-button").css('display', 'none');
    }
}

MVOBSlider.loadNextImage = function ()
{
    if(MVOBSlider.blocks.length < MVOBSlider.links.length)
    {
        var url = MVOBSlider.links[MVOBSlider.blocks.length];
        var block = jq(document.createElement('div'));
        jq(block).addClass('slider-media-block');
        var img = new Image();
        
        jq(img).load(
            function(){
                // set the image hidden by default    
                jq(this).hide();
                jq(block).append(this);
                if(MVOBSlider.descriptions[MVOBSlider.blocks.length] != "")
                {
                    var infoBox = jq(document.createElement('div'));
                    jq(infoBox).addClass("slider-media-description");
                    jq(infoBox).html(MVOBSlider.descriptions[MVOBSlider.blocks.length])
                    jq(block).append(infoBox);
                    if(MVOBSlider.titles[MVOBSlider.blocks.length] != "")
                    {
                        jq(infoBox).prepend('<div class="slider-media-title">' + MVOBSlider.titles[MVOBSlider.blocks.length] + '</div>');
                    }
                }
                jq('#slider-media-album-blocks').append(block);
                //fade image in
                jq(this).fadeIn();
                MVOBSlider.blocks[MVOBSlider.blocks.length] = block;
                if (MVOBSlider.blocks.length < MVOBSlider.links.length)
                {
                    MVOBSlider.loadNextImage();
                }else
                {
                    MVOBSlider.addButtons();
                }
            }
        ).attr('src', url);
    }
}

MVOBSlider.scrollTo = function (num)
{
    if(num >= 0 && num < MVOBSlider.blocks.length)
    {
        for(var i=0; i<MVOBSlider.blocks.length; i++)
        {
            if(i === num)
            {
                jq(MVOBSlider.blocks[i]).css('display', 'block');
                MVOBSlider.currentBlock = i;
            }else
            {
                jq(MVOBSlider.blocks[i]).css('display', 'none');
            }
        }
    }
    /*if (num === 0)
    {
        //MVOBSlider.scrollTo(MVOBSlider.blocks.length-1); 
        jq(".slider-next-button").css('display', 'none');
        jq(".slider-prev-button").css('display', 'block');
    }
    else if (num === MVOBSlider.blocks.length - 1)
    {
        //MVOBSlider.scrollTo(0);
       jq(".slider-prev-button").css('display', 'none');
       jq(".slider-next-button").css('display', 'block');
    }
    else
    {
        //delete to loop
        jq(".slider-prev-button").css('display', 'block');
        jq(".slider-next-button").css('display', 'block');
    }*/
}

MVOBSlider.run = function ()
{
    MVOBSlider.getMediaLinks();
    MVOBSlider.loadNextImage();
    setInterval(MVOBSlider.next, 5000);
}

jq(document).ready(function () {MVOBSlider.run();});