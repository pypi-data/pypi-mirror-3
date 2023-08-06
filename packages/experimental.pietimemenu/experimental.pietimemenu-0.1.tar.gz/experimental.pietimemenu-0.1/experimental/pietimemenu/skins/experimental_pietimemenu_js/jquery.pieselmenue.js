;(function($){


    function rmDiv(evt){
        $(this).remove();
    };

    function menueItemClick(evt){
         t = $(this).text();
         sel = $(this).parent().parent().find("select");
         $(this).parent().remove();
         $(sel).val(t);
    };

    function createMenuItems(sel, container){
        var i = 0;
        var centerY = container.height()/2;
        var centerX = container.width()/2;
        var radius = Math.min(centerX, centerY) * 0.8;
        sel.find("option").each(function(){
            if (this.value == this.text){
              i+=1;
            };
        });
        j=0;
        sel.find("option").each(function(){
            if (this.value == this.text){
               span = document.createElement('span');
               ob = getCoords(j,i,radius, centerX, centerY);
               $(span).css({'top': ob.top + 'px',
                            'left': ob.left + 'px'});
               $(span).append($(this).val());
               if ($(this).attr('selected')){ $(span).addClass('selected'); };
               $(span).click(menueItemClick);
               container.append(span);
               j+=1;
            };
        });
    };


    function showPieSelMenue(evt, obj) {
         obj.hide()
         evt.preventDefault(true);
         evt.stopPropagation();
         div = document.createElement('div');
         $(div).addClass('piesel-menu-container');
         $(div).click(rmDiv);
         obj.parent().append(div);
         psdiv = obj.parent().find('div.piesel-menu-container');
         var h = psdiv.height();
         var w = psdiv.width();
         createMenuItems(obj, psdiv);
         var top = evt.clientY - w/2;
         var left = evt.clientX - h/2;
         $(psdiv).css({ 'top': top +'px',
                     'left': left + 'px'});
         obj.show();
    };




    /**
     * Get the radians value of an angle given a
     * particular slice of the selection
     *
     *  @params
     *      iIdx - the instance index
     *      iNum - the number of menu items
     */
    function getAngleAtIndex(iIdx, iNum){

        return 2 * Math.PI * parseFloat(iIdx/iNum); // radians

    };

    /**
     * getCoords - returns coordinates for menuitems, as
     *  well as an animation object with the appropriate rotation
     *  as per config
     *
     *  @params
     *      iIdx - the instance index (1st, 2nd, 3rd, etc..)
     *      iNum - the number of menuitems to distribute
     *  @return
     *      Object - (x, y)
     */
    function getCoords(iIdx, iNum, radius, centerX, centerY){


        var angle = getAngleAtIndex(iIdx, iNum);

        angle += toRadians(-90); // provide flexibility of angle

        //  assuming: hypotenuse (hyp) = radius
        //
        //  opposite    |\  hypotenuse
        //              | \
        //      90deg   |__\    (*theta* - angle)
        //              adjacent
        //
        //  x-axis offset: cos(theta) = adjacent / hypotenuse
        //      ==> adjacent = left = cos(theta) * radius
        //  y-axis offset: sin(theta) = opposite / hypotenuse
        //      ==> opposite = top = sin(theta) * radius

        var l = centerX + ( Math.cos( angle ) * radius ), // "left"
            // angle is rounded to 2dp to fix a bug
            t = centerY + ( Math.sin( parseInt(angle*100)/100 ) * radius ); // "top"

        return {
            left: l,
            top: t
            }

        }; // return the x,y coords



    /**
     * simple method to convert degrees to radians
     */
    function toRadians(degrees){

        return degrees * Math.PI / 180;

    };


    /**
     * private :: init fn
     * @params
     *  $menu - the jQuery obj
     */
    function init($menu){
        $menu.mousedown(function(evt){
            showPieSelMenue(evt, $menu);
        });

    };
     /**
     * jQuery PieSel Plugin
     *  @params
     *      > input, dealt with by type
     *  if empty - assumes initialization
     *  if object - assumes initialization
     */
    $.fn.pieselmenu = function(input){

        try {

            var $this = $(this);

            var type = typeof input;

            if(type=="object")

                return init($this, input);


        } catch (e) {

            return "error : "+e;

        }

    };


})(jQuery);
