L.mapbox.accessToken = 'pk.eyJ1IjoiZG9yc2VnYWwiLCJhIjoiY2o1ZmUyaDJqMGV2ejM2bzEzb2IxcXBpMSJ9.RyTUESYcJTZ2J9mxH_A-1w';

var map = L.mapbox.map('map')
  .setView([39.279806, 2.402989], 3);

var layers = {
    Streets: L.mapbox.tileLayer('mapbox.streets'),
    Outdoors: L.mapbox.tileLayer('mapbox.outdoors'),
    Light: L.mapbox.tileLayer('mapbox.light'),
    Dark: L.mapbox.tileLayer('mapbox.dark'),
    Satellite: L.mapbox.tileLayer('mapbox.satellite')
};

$('#search_title').keyup(search);
$('#search_director').keyup(search);
$('#search_genre').keyup(search);

layers.Streets.addTo(map);
L.control.layers(layers).addTo(map);

var markers = new L.MarkerClusterGroup();
var markers_size = 0;
var polyline = null;

var geojsonLayer = omnivore.geojson('movies.geojson', null, L.mapbox.featureLayer())
  .on("ready", function() {
  
    attachPopups();
    
    // Now we can transfer single layers / markers to the marker cluster group.
    markers.addLayer(geojsonLayer); // use the global variable markers.
    map.fitBounds(geojsonLayer.getBounds());
    markers.addTo(map);
    markers.eachLayer(function(marker) {
        markers_size++;
    });
  });


var markerList = document.getElementById('listings');

$('.menu-ui a').on('click', function() {
    // For each filter link, get the 'data-filter' attribute value.
    if (polyline != null){
        polyline.remove();
    }
    $('#search_title').val('');
    $('#search_director').val('');
    $('#search_genre').val('');
    filter_by("","","");
    map.fitBounds(geojsonLayer.getBounds());
    return false;
});

function title_with_year(properties) {
  return properties.title + " (" + properties.year + ")";
}

function addPolyline(title) {
    polyline = L.polyline([]).addTo(map);
    geojsonLayer.eachLayer(function(marker) {
        if (title == marker.feature.properties.title)
        polyline.addLatLng(marker.getLatLng());
    });
}

function onmove() {
    // Get the map bounds - the top-left and bottom-right locations.
    var inBounds = [],
        bounds = map.getBounds();
    markerList.innerHTML = "";
    var numOfBounds = 1;
    markers.eachLayer(function(marker) {
        var title = title_with_year(marker.feature.properties);
        // For each marker, consider whether it is currently visible by comparing
        // with the current map bounds.
        if (bounds.contains(marker.getLatLng())) {
            numOfBounds++;
            if ($.inArray(title, inBounds) == -1){
            inBounds.push(title);
            var item = markerList.appendChild(document.createElement('div'));
            item.className = 'item';
            var link = item.appendChild(document.createElement('a'));
            link.href = '#';
            link.className = 'title';
            link.innerHTML = title;
            link.onclick = function() {
                filter_by(marker.feature.properties.title, "", "");
                map.fitBounds(geojsonLayer.getBounds());
                addPolyline(marker.feature.properties.title);
            };
            // Marker interaction
            marker.on('click', function(e) {
              // 1. center the map on the selected marker.
              map.panTo(marker.getLatLng());
            });
        }
      }
    });
    if (numOfBounds == markers_size){
      $('.menu-ui a').removeClass('active');
    }
    else $('.menu-ui a').addClass('active');
}

function search() {
    // get the value of the search input field
    var title = $('#search_title').val().toLowerCase();
    var director = $('#search_director').val().toLowerCase();
    var genre = $('#search_genre').val().toLowerCase();

    filter_by(title, director, genre);
}

function filter_by(title, director, genre) {
    geojsonLayer.setFilter(filter_feature); // this will "hide" markers that do not match the filter.
    attachPopups();
    
    // replace the content of marker cluster group.
    markers.clearLayers();
    markers.addLayer(geojsonLayer);

    onmove();

    function filter_feature(feature){
        return showMovie(feature, title) && showDirector(feature, director) && showGenre(feature, genre); 
    }
}

function showMovie(feature, query) {
    return feature.properties.title
        .toLowerCase()
        .indexOf(query.toLowerCase()) !== -1;
}

function showDirector(feature, query) {
    var directors = feature.properties.directors;
    for (var i=0; i<directors.length; i++){
      if (directors[i].toLowerCase().indexOf(query) !== -1)
        return true;
    }
}

function showGenre(feature, query) {
    var genres = feature.properties.genres;
    for (var i=0; i<genres.length; i++){
      if (genres[i].toLowerCase().indexOf(query) !== -1)
        return true;
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
