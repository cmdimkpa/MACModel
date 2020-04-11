// modulate IP packets every 100ms

let modulationInterval = 100;
let networkHost = "localhost";
let networkPort = 63457;
let request = require('request');

function modulatePackets() {
    request.get(`http://${networkHost}:${networkPort}/SubNetworkLTE/PhysicalUplinkControlChannel/Modulation`, (error, res, body) => { })
}

let modulator = setInterval(modulatePackets, modulationInterval);
