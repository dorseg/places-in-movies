L.mapbox.accessToken = 'pk.eyJ1IjoiZG9yc2VnYWwiLCJhIjoiY2o1ZmUyaDJqMGV2ejM2bzEzb2IxcXBpMSJ9.RyTUESYcJTZ2J9mxH_A-1w';

var map = L.mapbox.map('map', 'mapbox.streets')
  .setView([39.279806, 2.402989], 3);

var clusters = new L.MarkerClusterGroup();
$.getJSON("movies.geojson", function(data) {
  var movies = L.geoJson(data, {
    pointToLayer: function(feature, latlng) {
      var properties = feature.properties;
      var coordinates = feature.geometry.coordinates;
      var cord_index = coordinates.findIndex(cords => cords[0]==latlng.lng && cords[1]==latlng.lat);
      var location = properties.synopsis_locations[cord_index];
      var title_with_year = properties.title + " (" + properties.year + ")"
      var marker = L.marker(latlng, {
            icon: L.mapbox.marker.icon({'marker-symbol': 'cinema', 'marker-color': '0044FF'}),
            title: title_with_year
        });
      marker.bindPopup("<center><b>" + title_with_year + "</b></center>" + 
                        "<b>Location:</b> " + location + '<br/>' +
                        "<b>Directors:</b> " + properties.directors + '<br/>' + 
                        "<b>Rating:</b> " + properties.rating + '<br/>' +
                        "<b>Genres:</b> " + properties.genres + '<br/>' +
                        "<a href=\"https://" + properties.url + "\" target=\"_blank\"><b>IMDB page</b></a>");
      return marker;
    },
    onEachFeature: function (feature, layer) {
      layer.addTo(clusters);
    }
  });
  map.addLayer(clusters);
});

var markerList = document.getElementById('marker-list');

function onmove() {
    // Get the map bounds - the top-left and bottom-right locations.
    var inBounds = [],
        bounds = map.getBounds();
    markerList.innerHTML = "";
    clusters.eachLayer(function(marker) {
        var title = marker.options.title;
        // For each marker, consider whether it is currently visible by comparing
        // with the current map bounds.
        if (bounds.contains(marker.getLatLng()) && $.inArray(title, inBounds) == -1) {
            inBounds.push(title);
            var item = markerList.appendChild(document.createElement('li'));
            item.innerHTML = title;
            item.onclick = function() {
              map.setView(marker.getLatLng(), 10);
              marker.openPopup();
            };
        }
    });
}

map.on('move', onmove);

// call onmove off the bat so that the list is populated.
// otherwise, there will be no markers listed until the map is moved.
onmove();

