// profile MAC packets every interval

let profilerInterval = 200;
let networkHost = "localhost";
let networkPort = 63457;
let request = require('request');
let events = 0;

function profilePackets() {
    events++;
    request.get(`http://${networkHost}:${networkPort}/SubNetworkLTE/MAC/Profiler`, (error, res, body) => { 
        console.log(`${body} (${events})`)
    })
}

let profiler = setInterval(profilePackets, profilerInterval);
