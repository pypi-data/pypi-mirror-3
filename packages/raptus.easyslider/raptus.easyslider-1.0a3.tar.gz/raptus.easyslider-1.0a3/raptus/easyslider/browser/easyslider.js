/*
 *   Easy Slider 1.7 - jQuery plugin
 *  written by Alen Grakalic
 *  http://cssglobe.com/post/4004/easy-slider-15-the-easiest-jquery-plugin-for-sliding
 *
 *  Copyright (c) 2009 Alen Grakalic (http://cssglobe.com)
 *  Dual licensed under the MIT (MIT-LICENSE.txt)
 *  and GPL (GPL-LICENSE.txt) licenses.
 *
 *  Built for jQuery library
 *  http://jquery.com
 *
 */

/*
 *  markup example for $("#slider").easySlider();
 *
 *   <div id="slider">
 *    <ul>
 *      <li><img src="images/01.jpg" alt="" /></li>
 *      <li><img src="images/02.jpg" alt="" /></li>
 *      <li><img src="images/03.jpg" alt="" /></li>
 *      <li><img src="images/04.jpg" alt="" /></li>
 *      <li><img src="images/05.jpg" alt="" /></li>
 *    </ul>
 *  </div>
 *
 */

(function($) {
  $.fn.loaded = function(callback) {
    if($(this).data('interval'))
      window.clearInterval($(this).data('interval'));
    $(this).data('interval', window.setInterval($.proxy(function(){
      for (i = 0; i < this.obj.length; i++) {
        if (this.obj.eq(i).complete == false)
          return;
        this.callback();
        window.clearInterval(this.obj.data('interval'));
      }
    }, {obj: $(this), callback: callback}), 50));
  }

  $.fn.easySlider = function(options){

    // default configuration properties
    var defaults = {
      prevId:     'prevBtn',
      prevText:     'Previous',
      nextId:     'nextBtn',
      nextText:     'Next',
      controlsShow: true,
      controlsBefore: '',
      controlsAfter:  '',
      controlsFade: true,
      controlsEmbedded: false,
      firstId:    'firstBtn',
      firstText:    'First',
      firstShow:    false,
      lastId:     'lastBtn',
      lastText:     'Last',
      lastShow:   false,
      vertical:   false,
      speed:      800,
      auto:     false,
      pause:      2000,
      continuous:   false,
      numeric:    false,
      numericId:    'controls',
      wrapperId:    'wrapper'
    };

    var options = $.extend(defaults, options);
    options.prevId += '_'+easyslider.count+'_';
    options.nextId += '_'+easyslider.count+'_';
    options.firstId += '_'+easyslider.count+'_';
    options.lastId += '_'+easyslider.count+'_';
    options.numericId += '_'+easyslider.count+'_';
    options.wrapperId += '_'+easyslider.count+'_';
    easyslider.count++;

    this.each(function() {
      var obj = $(this);
      var lis = $("li", obj);
      var ul = $("ul", obj);
      var w = 0;
      lis.each(function() { w = Math.max(w, $(this).width()); }).css('width', w+'px');
      var h = 0;
      lis.each(function() { h = Math.max(h, $(this).height()); }).css('height', h+'px');
      var s = lis.length;
      var clickable = true;
      $(obj).width(w).height(h);
      var ts = s-1;
      var t = 0;
      if(!options.vertical) ul.css('width',s*w);
      ul.wrap('<div class="wrapper" id="'+options.wrapperId+'" />');
      $("#"+options.wrapperId).width(w).height(h).css({
        overflow: "hidden",
        position: 'relative'
      });
      if(lis.size() < 2)
        return;

      // Provide continuous sliding functionality
      if(options.continuous){
        ul.prepend($("ul li:last-child", obj).clone().css("margin-left","-"+ w +"px"));
        ul.append($("ul li:nth-child(2)", obj).clone());
        ul.css('width',(s+1)*w);
        lis = $("li", obj);
      };

      // Set slide direction
      if(!options.vertical) {
        lis.css('float', 'left');
        $(obj).addClass('horizontal');
      } else
        $(obj).addClass('vertical');

      // Show control elements
      if(options.controlsShow){

        var html = options.controlsBefore;
        if (!options.numeric || options.numeric == 'both') {
          $(obj).addClass('controls');
          if(options.firstShow) html += '<span class="firstBtn '+ options.firstId +'" id="'+ options.firstId +'"><a href=\"javascript:void(0);\">'+ options.firstText +'</a></span>';
          html += ' <span class="prevBtn '+ options.prevId +'" id="'+ options.prevId +'"><a href=\"javascript:void(0);\">'+ options.prevText +'</a></span>';

        }

        if (options.numeric || options.numeric == 'both') {
          $(obj).addClass('numeric');
          html += '<ol class="controls '+ options.numericId +'" id="'+ options.numericId +'"></ol>';
        }

        if (!options.numeric || options.numeric == 'both') {
          html += ' <span class="nextBtn '+ options.nextId +'" id="'+ options.nextId +'"><a href=\"javascript:void(0);\">'+ options.nextText +'</a></span>';
          if(options.lastShow) html += ' <span class="lastBtn '+ options.lastId +'" id="'+ options.lastId +'"><a href=\"javascript:void(0);\">'+ options.lastText +'</a></span>';
        }

        html += options.controlsAfter;

        if (options.controlsEmbedded) {
          html = '<div class="controls-wrapper">' + html + '</div>';
          lis.each(function() { $(this).append(html); });
        } else {
          $(obj).append(html);
        }
      };

      // Bind events
      if (options.numeric || options.numeric == 'both') {
        for(var i=0;i<s;i++){
          $(document.createElement("li"))
            .attr('id',options.numericId + (i+1))
            .attr('class',options.numericId + (i+1))
            .html('<a rel='+ i +' href=\"javascript:void(0);\">'+ (i+1) +'</a>')
            .appendTo($("."+ options.numericId))
            .click(function(){
              animate($("a",$(this)).attr('rel'),true);
            });
        };
      }
      if (!options.numeric || options.numeric == 'both') {
        $("a","."+options.nextId).click(function(){
          animate("next",true);
        });
        $("a","."+options.prevId).click(function(){
          animate("prev",true);
        });
        $("a","."+options.firstId).click(function(){
          animate("first",true);
        });
        $("a","."+options.lastId).click(function(){
          animate("last",true);
        });
      };

      function setCurrent(i){
        i = parseInt(i)+1;
        $("li", "." + options.numericId).removeClass("current");
        $("li." + options.numericId + i).addClass("current");
      };

      function adjust(){
        if(t>ts) t=0;
        if(t<0) t=ts;
        if(!options.vertical) {
          $("ul",obj).css("margin-left",(t*w*-1));
        } else {
          $("ul",obj).css("margin-top",(t*h*-1));
        }
        clickable = true;
        if(options.numeric) setCurrent(t);
      };

      function animate(dir,clicked){
        if (clickable){
          clickable = false;
          var ot = t;
          switch(dir){
            case "next":
              t = (ot>=ts) ? (options.continuous ? t+1 : ts) : t+1;
              break;
            case "prev":
              t = (t<=0) ? (options.continuous ? t-1 : 0) : t-1;
              break;
            case "first":
              t = 0;
              break;
            case "last":
              t = ts;
              break;
            default:
              t = dir;
              break;
          };
          var diff = Math.abs(ot-t);
          var speed = diff*options.speed;
          if(!options.vertical) {
            p = (t*w*-1);
            $("ul",obj).animate(
              { marginLeft: p },
              { queue:false, duration:speed, complete:adjust }
            );
          } else {
            p = (t*h*-1);
            $("ul",obj).animate(
              { marginTop: p },
              { queue:false, duration:speed, complete:adjust }
            );
          };

          if(!options.continuous && options.controlsFade){
            if(t==ts){
              $("a","."+options.nextId).hide();
              $("a","."+options.lastId).hide();
            } else {
              $("a","."+options.nextId).show();
              $("a","."+options.lastId).show();
            };
            if(t==0){
              $("a","."+options.prevId).hide();
              $("a","."+options.firstId).hide();
            } else {
              $("a","."+options.prevId).show();
              $("a","."+options.firstId).show();
            };
          };

          if(clicked) clearTimeout(timeout);
          if(options.auto && dir=="next" && !clicked){;
            timeout = setTimeout(function(){
              animate("next",false);
            },diff*options.speed+options.pause);
          };

        };

      };

      // init
      var timeout;
      if(options.auto){;
        timeout = setTimeout(function(){
          animate("next",false);
        },options.pause);
      };

      if(options.numeric) setCurrent(0);

      if(!options.continuous && options.controlsFade){
        $("a","."+options.prevId).hide();
        $("a","."+options.firstId).hide();
      };

    });

  };

})(jQuery);



