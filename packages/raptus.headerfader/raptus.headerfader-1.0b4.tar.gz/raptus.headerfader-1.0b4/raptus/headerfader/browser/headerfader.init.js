(function($) {
  $(document).ready(function() {
    if($('#portal-content-headerfader > ul li a').size() > 1) {
      $('#portal-content-headerfader > ul li a').inlineLightBox(inlinelightbox.settings['raptus_headerfader']);
      $('#portal-content-headerfader > ul').hide();
    }
  });
})(jQuery);