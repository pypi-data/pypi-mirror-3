(function(){

/**

Search form
**/
jQuery.fn.EEAlchemy = function(settings){
  var self = this;
  self.valid = false;

  self.options = {
    initialize: function(){
      var form = jQuery('form', self);

      jQuery('input[type=submit]', form).hide();
      var img = jQuery('<img>')
        .attr('src', '++resource++eea.alchemy.loader.gif')
        .attr('id', 'eea-alchemy-loader')
        .css('display', 'inline')
        .hide();
      jQuery('input[type=submit]', form).after(img);
      jQuery('input[type=checkbox]', form).click(function(){
        self.options.validate(form);
      });

      form.submit(function(){
        if(!self.valid){
          return false;
        }
        self.options.search(form);
        return false;
      });

      self.msg = jQuery('<div>').addClass('alchemy-msg').hide();
      self.msg.ajaxError(function(evt, request, settings){
        self.options.search_end(form, 'ERROR: Please try again later');
      });
      jQuery('input[type=submit]', form).after(self.msg);
    },

    // Validate search form
    validate: function(form){
      self.valid = false;
      // Portal type required
      var portal_type = jQuery('input[name=portal_type]:checked', form).length;
      if(!portal_type){
        jQuery('input[type=submit]', form).hide();
        return false;
      }

      // Lookin required
      var lookin = jQuery('input[name=lookin]:checked', form).length;
      if(!lookin){
        jQuery('input[type=submit]', form).hide();
        return false;
      }

      // Discover required
      var discover = jQuery('input[name=discover]:checked', form).length;
      if(!discover){
        jQuery('input[type=submit]', form).hide();
        return false;
      }

      // Valid
      self.valid = true;
      jQuery('input[type=submit]', form).show();
    },

    search_start: function(form){
      jQuery('input[type=submit]', form).hide();
      jQuery('input[type=checkbox]', form).attr('disabled', true);
      jQuery('#eea-alchemy-loader').show();
    },

    search_end: function(form, message){
      jQuery('#eea-alchemy-loader').hide();
      self.msg.text(message);
      self.msg.show();
    },

    search: function(form){
      var query = form.serialize();
      query += '&redirect=';
      var action = form.attr('action');
      self.options.search_start(form);
      jQuery.get(action, query, function(data){
        self.options.search_end(form, data);
      });
    }
  };

  // Update settings
  if(settings){
    jQuery.extend(self.options, settings);
  }

  self.options.initialize();
  return this;
};

/**

Load
*/
jQuery(document).ready(function(){
  // Cleanup main template
  jQuery("#belowContent").remove();
  jQuery("#eea-comments").remove();
  jQuery(".discussion").remove();

  // Initialize
  jQuery('#eea-alchemy .alchemy-search').EEAlchemy();
});

}());
