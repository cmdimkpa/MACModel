// sort MAC packets for scheduling at every interval

let sortingInterval = 200;
let networkHost = "localhost";
let networkPort = 63457;
let request = require('request');
let events = 0;

function sortPackets() {
    events++;
    request.get(`http://${networkHost}:${networkPort}/SubNetworkLTE/Scheduler/Sorter`, (error, res, body) => {
        console.log(`${body} (${events})`)
    })
}

let sorter = setInterval(sortPackets, sortingInterval);
