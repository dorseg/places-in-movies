L.mapbox.accessToken = 'pk.eyJ1IjoiZG9yc2VnYWwiLCJhIjoiY2o1ZmUyaDJqMGV2ejM2bzEzb2IxcXBpMSJ9.RyTUESYcJTZ2J9mxH_A-1w';

var map = L.mapbox.map('map', 'mapbox.streets')
  .setView([37.8, -96], 4)

var clusters = new L.MarkerClusterGroup();
$.getJSON("movies.geojson", function(data) {
  var incidents = L.geoJson(data, {
    pointToLayer: function(feature, latlng) {
      var properties = feature.properties
      var title_with_year = properties.title + " (" + properties.year + ")"
      var marker = L.marker(latlng, {
            icon: L.mapbox.marker.icon({'marker-symbol': 'cinema', 'marker-color': '0044FF'}),
            title: title_with_year
        });
      marker.bindPopup("<center><b>" + title_with_year + "</b></center>" + 
                        "<b>directors:</b> " + properties.directors + '<br/>' + 
                        "<b>rating:</b> " + properties.rating + '<br/>' +
                        "<b>genres:</b> " + properties.genres + '<br/>' +
                        "<b>url:</b> " + properties.url);
      return marker;
    },
    onEachFeature: function (feature, layer) {
      layer.addTo(clusters);
    }
  });
  map.addLayer(clusters);
});

function onmove() {
    // Get the map bounds - the top-left and bottom-right locations.
    var inBounds = [],
        bounds = map.getBounds();
    clusters.eachLayer(function(marker) {
        var title = marker.options.title;
        // For each marker, consider whether it is currently visible by comparing
        // with the current map bounds.
        if (bounds.contains(marker.getLatLng()) && $.inArray(title, inBounds) == -1) {
            inBounds.push(title);
        }
    });
    // Display a list of markers.
    document.getElementById('movies').innerHTML = inBounds.join('\n');
}

map.on('move', onmove);

// call onmove off the bat so that the list is populated.
// otherwise, there will be no markers listed until the map is moved.
onmove();

