// Add your JavaScript code here
const MAX_WIDTH = Math.max(1080, window.innerWidth);
const MAX_HEIGHT = 720;
const margin = { top: 40, right: 100, bottom: 40, left: 175 };

let map_width = MAX_WIDTH,
    map_height = MAX_HEIGHT;

let filename = "county_agg.csv";

ids_to_states = {};

// initial field
let curr_field = "PopDensity";

// ---------------------------Map Setup---------------------------------
// Static elements only
let mapsvg = d3
    .select("#map") // svg object for the map
    .append("svg")
    .attr("width", map_width)
    .attr("height", map_height)
    .append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

var countymap = d3.json("us_counties.json");
var projection = d3.geoEquirectangular();
projection
    .translate([map_width / 2 - margin.left, map_height / 2 - margin.top])
    .scale(1400)
    .center([-95.5, 40]);
var path = d3.geoPath().projection(projection);

// -----------Redraw the map with a given field------------------------
function updateMap() {
    d3.csv(filename).then(function (data) {
        const maxVal = Math.max(...data.map((d) => d[curr_field]));
        countymap.then(function (values) {
            // for (let x = 0; x < values.features.length; x++){
            //     // console.log(values.features[x].properties.STATE);
            //     ids_to_states[values.features[x].properties.STATE] = [];
            // }
            // console.log(ids_to_states)
            let counties = mapsvg.selectAll("path").data(values.features);
            // draw map
            counties
                .enter()
                .append("path")
                .merge(counties)
                .attr("class", "continent")
                .attr("name", (d) => d.properties.NAME)
                .attr("d", path)
                .style("fill", (d) =>
                    countyColor(
                        d.properties.NAME,
                        d.properties.STATE,
                        data,
                        maxVal
                    )
                );
            // for (let i = 0; i < values.features.length; i++) {
            //     console.log(values.features[i].properties.ADMIN)
            // }
            console.log("Before");
            console.log(ids_to_states);
            convertKeys();
            console.log("after");
            console.log(ids_to_states);
        });
    });
}

function countyColor(county, state, data, maxVal) {
    // lowercase and remove whitespace
    county = county.replace(/\s*/g, "").toLowerCase();
    const goodColor = [7, 31, 184];
    const badColor = [255, 104, 0];

    let noData = [161, 160, 157, 0.8];
    let color = noData;

    for (let i = 0; i < data.length; i++) {
        if (data[i]["County"] === county) {
            color = [
                goodColor[0],
                goodColor[1],
                goodColor[2],
                (data[i][curr_field] / maxVal)*0.8 + 0.2,
            ];
            if (!(state in ids_to_states)) {
                ids_to_states[state] = [];
            }
            let temp = ids_to_states[state];
            temp.push(data[i]["State"]);

            ids_to_states[state] = temp;
            break;
        }
    }
    colorString = `rgba(${color[0]},${color[1]},${color[2]},${color[3]})`;
    return colorString;
}

updateMap();
// code to calculate and print the most propable mapping
// of state numbers to state names since whoever made
// this stupid dataset thought it would be a good idea
// to refer to states with numbers

// giving up because I cannot for the life of me figure out
// how to simply iterate through the object properties here

// going to make the num->state mapping manually


console.log(ids_to_states["11"]);
console.log(Object.keys(ids_to_states));

const convertKeys = () => {
    for (let [k, v] of Object.entries(ids_to_states)) {
        console.log(k);
        state_freqs = {};
        for (let s of ids_to_states[k]) {
            if (!(s in state_freqs)) {
                state_freqs[s] = 0;
            }
            state_freqs[s]++;
        }
        maxKey = "";
        maxFreq = 0;
        for (let s in state_freqs) {
            if (state_freqs[s] >= maxFreq) {
                maxFreq = state_freqs[s];
                maxKey = s;
            }
        }
        ids_to_states[k] = maxKey;
    }
};

// // console.log()
