if('serviceWorker' in navigator) {
	navigator.serviceWorker.register('/sw.js');
};

document.getElementById("logo").addEventListener("click", () => {
	document.location = document.location.origin
});

let nav_open = false;
let alerts_open = false;

/* Set the width of the sidebar to 250px and the left margin of the page content to 250px */
function openNav() {
	if (!nav_open) {
		nav_open = true;
		document.getElementById("mySidebar").style.width = "250px";
		document.getElementById("main").style.marginLeft = "250px";
	} else {
		nav_open = false;
		document.getElementById("mySidebar").style.width = "0";
		document.getElementById("main").style.marginLeft = "0";
	}
	
  }

function closeNav(event) {
	if (nav_open) {
		event.stopPropagation();
		nav_open = false;
		document.getElementById("mySidebar").style.width = "0";
		document.getElementById("main").style.marginLeft = "0"
  	}
}

function closeAlerts(event) {
	if (alerts_open) {
		event.stopPropagation();
		alerts_open = false;
		document.getElementById("alerts").style.width = "0";
		document.getElementById("alerts").style.padding = "0";
		document.getElementById("alerts").style.paddingTop = "0";
		document.getElementById("alerts-btn").style.marginRight = "0";
  	}
}

function openAlerts() {
	if (!alerts_open) {
		alerts_open = true;
		document.getElementById("alerts").style.width = "40%";
		document.getElementById("alerts").style.padding = "30px";
		document.getElementById("alerts").style.paddingTop = "15px";
		document.getElementById("alerts-btn").style.marginRight = "40%";
		axios.get('api/get-alerts').then((_res) => {
			let alerts = _res.data;
			let alert_div = document.getElementById("alerts");
			alert_div.innerHTML = "<h2 class=\"text-white\" style=\"text-align: center;\">Notifications</h2>";
			alert_div.innerHTML += alerts;
		});
	} else {
		alerts_open = false;
		document.getElementById("alerts").style.width = "0";
		document.getElementById("alerts").style.padding = "0";
		document.getElementById("alerts").style.paddingTop = "0";
		document.getElementById("alerts-btn").style.marginRight = "0";
	}
}

document.body.addEventListener('click', (event) => {closeNav(event)}, true); 
document.body.addEventListener('click', (event) => {closeAlerts(event)}, true); 
