// modulate IP packets to MAC packets every interval

let modulationInterval = 500;
let networkHost = "localhost";
let networkPort = 63457;
let request = require('request');
let events = 0;

function modulatePackets() {
    events++;
    request.get(`http://${networkHost}:${networkPort}/SubNetworkLTE/PhysicalUplinkControlChannel/Modulation`, (error, res, body) => { 
        console.log(`${body} (${events})`)
    })
}

let modulator = setInterval(modulatePackets, modulationInterval);
