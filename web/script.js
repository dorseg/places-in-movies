L.mapbox.accessToken = 'pk.eyJ1IjoiZG9yc2VnYWwiLCJhIjoiY2o1ZmUyaDJqMGV2ejM2bzEzb2IxcXBpMSJ9.RyTUESYcJTZ2J9mxH_A-1w';

var map = L.mapbox.map('map', 'mapbox.streets')
  .setView([39.279806, 2.402989], 3);

$('#search').keyup(search);

var markers = new L.MarkerClusterGroup();

var geojsonLayer = omnivore.geojson('movies.geojson', null, L.mapbox.featureLayer())
  .on("ready", function() {
  
    attachPopups();
    
    // Now we can transfer single layers / markers to the marker cluster group.
    markers.addLayer(geojsonLayer); // use the global variable markers.
    map.fitBounds(geojsonLayer.getBounds());
    markers.addTo(map);
  });


var markerList = document.getElementById('listings');

function title_with_year(properties) {
  return properties.title + " (" + properties.year + ")";
}

function setActive(el) {
  var siblings = markerList.getElementsByTagName('div');
  for (var i = 0; i < siblings.length; i++) {
    siblings[i].className = siblings[i].className
    .replace(/active/, '').replace(/\s\s*$/, '');
  }

  el.className += ' active';
}

function onmove() {
    // Get the map bounds - the top-left and bottom-right locations.
    var inBounds = [],
        bounds = map.getBounds();
    markerList.innerHTML = "";
    markers.eachLayer(function(marker) {
        var title = title_with_year(marker.feature.properties);
        // For each marker, consider whether it is currently visible by comparing
        // with the current map bounds.
        if (bounds.contains(marker.getLatLng()) && $.inArray(title, inBounds) == -1) {
            inBounds.push(title);
            var item = markerList.appendChild(document.createElement('div'));
            item.className = 'item';
            var link = item.appendChild(document.createElement('a'));
            link.href = '#';
            link.className = 'title';
            link.innerHTML = title;
            link.onclick = function() {
              setActive(item);
              map.setView(marker.getLatLng(), 10);
              marker.openPopup();
            };
            // Marker interaction
            marker.on('click', function(e) {
              // 1. center the map on the selected marker.
              map.panTo(marker.getLatLng());
              // 2. Set active the markers associated listing.
              setActive(item);
            });
        }
    });
}

function search() {
    // get the value of the search input field
    var searchString = $('#search').val().toLowerCase();

    geojsonLayer.setFilter(showMovie); // this will "hide" markers that do not match the filter.
    attachPopups();
    
    // replace the content of marker cluster group.
    markers.clearLayers();
    markers.addLayer(geojsonLayer);

    onmove();

    // here we're simply comparing the 'state' property of each marker
    // to the search string, seeing whether the former contains the latter.
    function showMovie(feature) {
        return feature.properties.title
            .toLowerCase()
            .indexOf(searchString) !== -1;
    }
}

// Need a function because it looks like .setFilter() removes the popup…
function attachPopups() {
  // Create popups.
    geojsonLayer.eachLayer(function (layer) {
      var feature = layer.feature;
      var properties = feature.properties;
      var title = title_with_year(properties);
      layer.bindPopup("<center><b>" + title + "</b></center>" + 
                        "<b>Location:</b> " + properties.location + '<br/>' +
                        "<b>Directors:</b> " + properties.directors + '<br/>' + 
                        "<b>Rating:</b> " + properties.rating + '<br/>' +
                        "<b>Genres:</b> " + properties.genres + '<br/>' +
                        "<a href=\"https://" + properties.url + "\" target=\"_blank\"><b>IMDb page</b></a>");
    });
}

map.on('move', onmove);

// call onmove off the bat so that the list is populated.
// otherwise, there will be no markers listed until the map is moved.
onmove();
