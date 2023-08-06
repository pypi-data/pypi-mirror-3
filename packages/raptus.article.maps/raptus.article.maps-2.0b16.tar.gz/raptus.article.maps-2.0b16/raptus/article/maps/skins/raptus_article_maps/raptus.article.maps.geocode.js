jQuery(document).ready(function() {
  function getLatLng() {
    jQuery('#spinner').show();
    
    var geocoder = new google.maps.Geocoder()
    geocoder.geocode({ 'address': jQuery('#geocode').val()}, function(results, status){
      if (status == google.maps.GeocoderStatus.OK) {
        jQuery('#longitude').val(results[0].geometry.location.lng());
        jQuery('#latitude').val(results[0].geometry.location.lat());
      }
      jQuery('#spinner').hide();
    });
    
  }
  if(jQuery('#archetypes-fieldname-geocode').length) {
    jQuery('#archetypes-fieldname-geocode').append('<input type="hidden" name="longitude" id="longitude" /><input type="hidden" name="latitude" id="latitude" />');
    jQuery('#archetypes-fieldname-longitude, #archetypes-fieldname-latitude').remove();
    jQuery('#archetypes-fieldname-geocode').show();
    jQuery('#geocode').blur(getLatLng);
    getLatLng();
  }
});
