// send IP packets to network every burst interval

let burstSize = 10;
let burstInterval = 20000;
let networkHost = "localhost";
let networkPort = 63457;
let request = require('request');
let events = 0;

function sendPackets() {
    events++;
    request.get(`http://${networkHost}:${networkPort}/SubNetworkLTE/AirInterface/UERegistration/${burstSize}`, (error, res, body) => {
        console.log(`${body} (${events})`)
    })
}

let burst = setInterval(sendPackets, burstInterval);
