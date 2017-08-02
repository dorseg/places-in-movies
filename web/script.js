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

layers.Streets.addTo(map);
L.control.layers(layers).addTo(map);

var markers = new L.MarkerClusterGroup();
var markers_size = 0;
//var polyline = null;
var hull = null;

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
var genre_filters = document.getElementById('genre_filters');
var genre_checkboxes = document.getElementsByClassName('genre_filter');
var on_genres = [];
var years_filters = document.getElementById('years_filters');
var years_checkboxes = document.getElementsByClassName('years_filter');
var on_years = [];

$('.genrebtn').on('click', function() {
    document.getElementById("filters").classList.toggle("show");
});

$('.yearsbtn').on('click', function() {
    document.getElementById("filters").classList.toggle("show");
});


$('.menu-ui a').on('click', function() {
    // For each filter link, get the 'data-filter' attribute value.
    // if (polyline != null){
    //     polyline.remove();
    // }
    if (hull != null){
        map.removeLayer(hull);
    }
    $('#search_title').val('');
    $('#search_director').val('');
    check_genres();
    check_years();
    filter_by("","",on_genres, on_years);
    map.fitBounds(geojsonLayer.getBounds());
    return false;
});

function get_title_with_year(properties) {
  return properties.title + " (" + properties.year + ")";
}

function addPolyline(title) {
    // polyline = L.polyline([]).addTo(map);
    // geojsonLayer.eachLayer(function(marker) {
    //     if (title == marker.feature.properties.title)
    //         polyline.addLatLng(marker.getLatLng());
    // });
    var markers_features = [];
    var markers_cord = [];
    geojsonLayer.eachLayer(function(marker) {
        if (title == marker.feature.properties.title)
            markers_features.push(marker.toGeoJSON());
            markers_cord.push(marker.getLatLng());
    });

    if (markers_features.length < 3){
        hull = L.polyline([]).addTo(map);
        for (var i=0; i<markers_cord.length; i++){
            hull.addLatLng(markers_cord[i]);
        }
        return;
    }

    var collection = {
        type: 'FeatureCollection',
        features: markers_features
    };

    hull = L.mapbox.featureLayer(turf.convex(collection));
    hull.addTo(map);
}

function isTitleInArray(title, items){
    for (var i=0; i<items.length; i++){
        item = items[i];
        var link = item.childNodes[0];
        var link_title = link.innerHTML;
        if (title == link_title){
            return true;
            break;
        }
    }
    return false;
}

function onmove() {
    // Get the map bounds - the top-left and bottom-right locations.
    var inBounds = [],
        bounds = map.getBounds();
    markerList.innerHTML = "";
    var numOfBounds = 1;
    markers.eachLayer(function(marker) {
        var title = marker.feature.properties.title;
        var title_with_year = get_title_with_year(marker.feature.properties);
        // For each marker, consider whether it is currently visible by comparing
        // with the current map bounds.
        if (bounds.contains(marker.getLatLng())) {
            numOfBounds++;
            if (isTitleInArray(title_with_year, inBounds) == false){
                var item = document.createElement('div');
                item.className = 'item';
                var link = item.appendChild(document.createElement('a'));
                link.href = '#';
                link.className = 'title';
                link.innerHTML = title_with_year;
                item.setAttribute('sort_by', title.toLowerCase());
                link.onclick = function() {
                    $('#search_title').val(title);
                    search();
                    map.fitBounds(geojsonLayer.getBounds(), {maxZoom: 15});
                    addPolyline(title);
                };
                // Marker interaction
                marker.on('click', function(e) {
                  map.panTo(marker.getLatLng());
                });
                inBounds.push(item);
            }
        }
    });
    inBounds.sort(function(a, b) {
        return a.getAttribute('sort_by').localeCompare(b.getAttribute('sort_by'));
    });
    inBounds.forEach(function(item) {
        markerList.appendChild(item);
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

    filter_by(title, director, on_genres, on_years);

    // if (polyline!= null){
    //     polyline.remove();
    // }
    if (hull != null){
        map.removeLayer(hull);
    }
}

function filter_by(title, director, genres, years) {
    geojsonLayer.setFilter(filter_feature); // this will "hide" markers that do not match the filter.
    attachPopups();
    
    // replace the content of marker cluster group.
    markers.clearLayers();
    markers.addLayer(geojsonLayer);

    onmove();

    function filter_feature(feature){
        return showMovie(feature, title) && showDirector(feature, director) && showGenres(feature, genres) && showYears(feature, years); 
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
    return false;
}

function showGenres(feature, on) {
    var genres = feature.properties.genres;
    for (var i=0; i<genres.length; i++){
        var found = false;
        for (var j=0; j<on.length; j++){
            if (genres[i].toLowerCase() == on[j].toLowerCase()){
                found = true;
                break;
            }
        }
        if (!found){
            return false;
        }
    }
    return true;
}

function showYears(feature, on) {
    var year = feature.properties.year;
    for (var i=0; i<on.length; i++){
        var decade = on[i];
        var year_bounds = decade.split("-");
        year_bounds[0] = parseInt(year_bounds[0]);
        year_bounds[1] = parseInt(year_bounds[1]);
        if (year >= year_bounds[0] && year <= year_bounds[1]){
            return true;
        }
    }
    return false;
}

// Need a function because it looks like .setFilter() removes the popup…
function attachPopups() {
  // Create popups.
    geojsonLayer.eachLayer(function (layer) {
      var feature = layer.feature;
      var properties = feature.properties;
      var title = get_title_with_year(properties);
      layer.bindPopup("<center><b>" + title + "</b></center>" + 
                        "<b>Location:</b> " + properties.location + '<br/>' +
                        "<b>Directors:</b> " + properties.directors + '<br/>' + 
                        "<b>Rating:</b> " + properties.rating + '<br/>' +
                        "<b>Genres:</b> " + properties.genres + '<br/>' +
                        "<a href=\"https://" + properties.url + "\" target=\"_blank\"><b>IMDb page</b></a>");
    });
}

function change_genres() {
    on_genres = [];
    for (var i = 0; i < genre_checkboxes.length; i++) {
        if (genre_checkboxes[i].checked) on_genres.push(genre_checkboxes[i].value);
    }
    search();
    return false;
}

function check_genres(){
    for (var i = 0; i < genre_checkboxes.length; i++) {
        genre_checkboxes[i].checked = 'checked';
    }
    change_genres();
}

genre_filters.onchange = change_genres;

function change_years() {
    on_years = [];
    for (var i = 0; i < years_checkboxes.length; i++) {
        if (years_checkboxes[i].checked) on_years.push(years_checkboxes[i].value);
    }
    search();
    return false;
}

function check_years(){
    for (var i = 0; i < years_checkboxes.length; i++) {
        years_checkboxes[i].checked = 'checked';
    }
    change_years();
}

years_filters.onchange = change_years;

map.on('move', onmove);

// call onmove off the bat so that the list is populated.
// otherwise, there will be no markers listed until the map is moved.
onmove();
change_genres();
change_years();
