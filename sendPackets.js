// send packets to network every 10s

let burstSize = 50;
let burstInterval = 10000;
let networkHost = "localhost";
let networkPort = 63457;
let request = require('request');

function sendPackets() {
    request.get(`http://${networkHost}:${networkPort}/SubNetworkLTE/AirInterface/UERegistration/${burstSize}`, (error, res, body) => {})
}

let burst = setInterval(sendPackets, burstInterval);
