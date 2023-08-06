var ajaxManager = jq.manageAjax.create('queuedRequests', {
    queue: true,
    cacheResponse: false
});



simplelayout.toggleEditMode = function(enable, el){
    var $controls = jq('.sl-controls', jq(el));
    var $block = $controls.closest('.BlockOverallWrapper');

    if(enable){
        //show controls div
        $controls.show();
        $controls.animate({opacity:1.0, width:400}, {queue: false, duration: 0});
        if (!$block.hasClass("blockHighlight"))
            $block.addClass("blockHighlight");

        jq(".simplelayout-content").trigger('actionsloaded');

        // init empty block spaces
        setHeightOfEmptyDropZone();

    }else{
        $block.removeClass("blockHighlight");
        $controls.animate({opacity:0,width:10}, { queue: false, duration: 0 }, function(){
            $controls.hide();
        });

        //expose edit area
        //enable later
        //simplelayout.expose().close();

    }

    var imgblocks = jq('.BlockOverallWrapper.image');
    for (var b=0;b<imgblocks.length;b++) {
        var query_controls = '#'+imgblocks[b].id + ' .sl-controls';
        var controls_el = jq(query_controls)[0];
        //simplelayout.setControlsWidth(controls_el);
    }



}

/* not really intuitive so far */
/*
simplelayout.expose = function(){
    var editable = jq('#portal-columns');
    var exposed =  editable.expose({api: true,
                                    opacity: 0.3,
                                    color:'black',
                                    zIndex:2000});

    return exposed;
}

*/

function gup( name, url )
{
  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  if (typeof url == "undefined") {
      url = window.location.href;
      }
  var results = regex.exec( url );
  if( results == null )
    return "";
  else
    return results[1];
}

function getBaseUrl(){
    var bhref= base_href = jq('base')[0].href;
    if(bhref.substr(bhref.length-1,1)!='/'){
        bhref += "/";
        }
    return bhref;

}

simplelayout.refreshParagraph = function(item){
    //var item = this;
    var a_el = jq('a', item);
    var id = a_el[0].id.split("_");
    var uid = id[0];
    //outch we have to change this asap - it makes no sense
    var params = id[1].split('-')
    var layout = params[0];
    var cssclass = params[1];
    var viewname = params[2];
    if (cssclass==undefined){
        cssclass = '';
    }
    if (viewname==undefined){
        viewname = '';
    }

    var fieldname = gup('fieldname',a_el[0].href);

    ajaxManager.add({url:'sl_ui_changelayout',
                            data:{ uid : uid, layout :layout,viewname:viewname,fieldname:fieldname },
                            success:function(data){
                                jq('#uid_' + uid +' .simplelayout-block-wrapper').replaceWith(data);
                                jq('#uid_' + uid +' .active').removeClass('active');
                                jq(item).addClass('active');
                                simplelayout.alignBlockToGridAction();
                                //simplelayout.setControlsWidth(item);
                                //trigger refreshed event
                                var $wrapper = jq(item).closest('.BlockOverallWrapper');
                                jq(".simplelayout-content:first").trigger('refreshed',[$wrapper]);
                                initializeSimplelayoutColorbox(jq('.sl-img-wrapper a'));
                                }
                            });
    return 0;

};

// simplelayout.setControlsWidth = function(item){
//     var imgblock = jq(item).closest('.BlockOverallWrapper.image');
//     if (imgblock.length != 0) {
//         // Get wrapper width
//         var wrapper_width = jq('.sl-img-wrapper', imgblock).width();
//         var controls_el = jq('.sl-controls', imgblock);
//         controls_el.css('width',wrapper_width+'px');
//     }
//     return 0;
// }


function activeSimpleLayoutControls(){
    jq(".sl-layout").bind("click", function(e){
            e.stopPropagation();
            e.preventDefault();

            simplelayout.refreshParagraph(this);

        });

}


function activateSimplelayoutActions(){
    // delete
    jq('.simplelayout-content a.sl-delete-action').each(function(i, o){
        var $this = jq(o);
        var uid = $this.closest('.BlockOverallWrapper').attr('id');
        $this.prepOverlay({
            subtype:'ajax',
            urlmatch:'$',urlreplace:' #content > *',
            formselector:'[action*=delete_confirmation]',
            noform:function(){
                //remove deleted block manually, because we won't reload the
                //hole page
                jq('#'+uid).hide('blind',function(){
                    jq(this).remove();
                });
                return 'close';
            },
            'closeselector':'[name=form.button.Cancel]'
        });
    });

    // TODO: Currently we miss some js after loading de edit.pt in the overlay
    // Example: WYSIWYG-editor will no load...
    // I tried to use subtype iframe, wihtout success
    //edit
    // jq('.simplelayout-content a.sl-edit-action').each(function(i, o){
    //     var $this = jq(o);
    //     $this.prepOverlay({
    //         subtype:'ajax',
    //         filter:'#visual-portal-wrapper > *',
    //         formselector:'[action*=base_edit]',
    //         noform:function(){
    //             simplelayout.refreshParagraph(
    //                 $this.closest('.BlockOverallWrapper').find('.sl-layout.active')
    //             );
    //
    //             return 'close';
    //         },
    //         'closeselector':'[name=form.button.cancel]'
    //     });
    // });
    // return false;


}

jq(function(){
    jq(".simplelayout-content:first").bind("actionsloaded", activateSimplelayoutActions);
    jq(".simplelayout-content:first").bind("actionsloaded", activeSimpleLayoutControls);

// XXX initializeMenus is a toggle and is already called by plone
//     jq(".simplelayout-content:first").bind("actionsloaded", function(){initializeMenus();});

    //bind mouseover/mouseout event on edit-button
    jq('div.simplelayout-content .BlockOverallWrapper').bind('mouseenter',function(e){
        e.stopPropagation();
        e.preventDefault();
        simplelayout.toggleEditMode(enable=true, el=this);
    });
    jq('div.simplelayout-content .BlockOverallWrapper').bind('mouseleave',function(e){
        e.stopPropagation();
        e.preventDefault();
        simplelayout.toggleEditMode(enable=false, el=this);
    });

    // Implement edit-bar slide
    jq('.sl-toggle-edit-bar-wrapper').bind('click', function(e){
        var $this = jq(this);
        var $bar = jq('.sl-toggle-edit-bar', $this);
        if ($bar.hasClass('ui-icon-triangle-1-e')){
            jq(this).closest('.simplelayout-content').find('.sl-actions-wrapper').hide();
            jq(this).closest('.simplelayout-content').find('.sl-toggle-edit-bar').removeClass('ui-icon-triangle-1-e').addClass('ui-icon-triangle-1-w');
        } else {
            jq(this).closest('.simplelayout-content').find('.sl-actions-wrapper').show();
            jq(this).closest('.simplelayout-content').find('.sl-toggle-edit-bar').removeClass('ui-icon-triangle-1-w').addClass('ui-icon-triangle-1-e');
        }
    });
});
