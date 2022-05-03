document.getElementById("logo").addEventListener("click", () => {
	document.location = document.location.origin
});

let nav_open = false;

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

function closeNav() {
	console.log(nav_open);
	if (nav_open) {
		nav_open = false;
		document.getElementById("mySidebar").style.width = "0";
		document.getElementById("main").style.marginLeft = "0"
  	}
}

document.body.addEventListener('click', () => {closeNav()}, true); 
