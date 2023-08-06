function block_ui() {
return;
    (function($) {
     var w = jQuery(window)
     var scr_x = w.scrollLeft();
     var scr_y = w.scrollTop();
     var dim_x = w.width();
     var dim_y = w.height();

     var overlay = jQuery('<div>');
     overlay.addClass('specification-overlay');

     var loading = jQuery('<div>');
     loading.addClass('specification-loading');

     loading.css({
         'top':dim_y/2-50 + scr_y + 'px',
         'left':dim_x/2-50 + scr_x + 'px',
         'z-index':2001
         });
     overlay.css({
         'top':scr_y+'px',
         'left':scr_x+'px',
         'z-index':2000,
         'width':dim_x+'px',
         'height':dim_y+'px',
         // 'background-color':'white',
         position:'absolute'
         });

     jQuery('body').append(overlay);
     jQuery('body').append(loading);
     overlay.show();
     loading.show();
    })(jQuery);
}

function unblock_ui(){
return;
  jQuery('.specification-overlay').remove();
  jQuery('.specification-loading').remove();
}


function init_tinymce(el){
  // init tinymce edit fields
(function($) {
  $('.mce_editable', el).each(function(){
    //ids can be repeated because of duplicated field names
    //same field can exist in the main page and also in the popup dialog
    var id = "popup-" + $(this).attr('id');
    $(this).attr('id', id);
    console.log("Initializing tinymce for ", id);
    delete InitializedTinyMCEInstances[id];
    var config = new TinyMCEConfig(id);
    // TODO: fix the editor sizes
    config.widget_config.editor_height = 800;
    config.widget_config.editor_width = 630;
    config.widget_config.autoresize = true;
    config.widget_config.resizing = true;
    config.widget_config.resizing_use_cookie = false;
    console.log(config.widget_config);
    //delete InitializedTinyMCEInstances[id];
    config.init();

    // TODO: resize tinymce to a more decent size
    //config.init();
  });
})(jQuery);
}


function schemata_ajaxify(el){
    //console.info("doing schemata ajaxify");

    (function($) {
      //set_actives();
      init_tinymce(el);

      //set the tags widget
      var widgets = $('.ArchetypesKeywordWidget');
      if(widgets.length){
        widgets.eeatags();
      }

      // other fixes to include: 
      // geographical coverage
      // organisations widget
      // temporal coverage
      // reference system widget has no label
      // geographical accuracy, contact person and disclaimer are not tinymce!?

      $("form", el).submit(
        function(e){
          console.log('doing save');
          block_ui();
          tinyMCE.triggerSave();
          var form = this;

          var inputs = [];
          $(".widgets-list .widget-name").each(function(){
            inputs.push($(this).text());
          });

          var data = "";
          data = $(form).serialize();
          // data += "&_active_region=" + active_region;
          data += "&form_submit=Save&form.submitted=1";
          //console.info("doing ajax schemata ajaxify");

          console.log(data);

          $.ajax({
            "data": data,
            url: this.action,
            type:'POST',
            cache:false,
            // timeout: 2000,
            error: function() {
              unblock_ui();
              alert("Failed to submit");
            },
            success: function(r) {
              $(el).html(r);
              schemata_ajaxify(el);
              unblock_ui();
              return false;
            }
          });
          return false;
        });
    })(jQuery);
}


function dialog_edit(url, title, callback, options){
      // Opens a modal dialog with the given title

    (function($) {
      block_ui();
      options = options || {
        'height':null,
        'width':1000
      };
      var target = $('#dialog_edit_target');
      $("#dialog-inner").remove();     // temporary, apply real fix
      $(target).append("<div id='dialog-inner'></div>");
      window.onbeforeunload = null; // this disables the form unloaders
      $("#dialog-inner").dialog({
        modal         : true,
        width         : options.width,
        minWidth      : options.width,
        height        : options.height,
        minHeight     : options.height,
        'title'       : title,
        closeOnEscape : true,
        buttons: {
          'Save':function(e){
            var button = e.target;
            $("#dialog-inner form").trigger('submit');
          },
          'Cancel':function(e){
            $("#dialog-inner").dialog("close");
          }
        },
        beforeclose:function(event, ui){ return true; }
      });

      $.ajax({
        'url':url,
        'type':'GET',
        'cache':false,
        'success': function(r){
          console.log($("#dialog-inner"));
          $("#dialog-inner").html($(r));
          //set_inout($("#archetypes-fieldname-themes"));
          callback();
        }
      });
    })(jQuery);
}


function set_creators(){
    // Set handlers for Create buttons

    (function($) {
      $('a.new_content_creator').live('click', function(){
        block_ui();
        var link = $(this).attr('href');
        console.log(link);
        var portal_type = "";
        var title = "Edit new " + portal_type;    // should insert portal type here
        var options = {
          'width':1000,
          'height':700
        };
        console.info("doing ajax set creators");
        dialog_edit(link, title, 
                function(text, status, xhr){
                    console.log("got response from ajax");
                    schemata_ajaxify($("#dialog-inner"));   //set someid
                    unblock_ui();
                    console.log("unblocked ui");
                },
                options);

        return false;
      });
    })(jQuery);
}

set_creators();

