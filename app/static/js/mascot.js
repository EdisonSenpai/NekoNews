const mascot = document.getElementById("mascot");

if (mascot) {

    let revertTimer = null;

    const setAwake = () => {
        clearTimeout(revertTimer);
        mascot.src = "/static/img/mascot_awake.png";
    };

    const setIdleDelayed = () => {
        clearTimeout(revertTimer);
        revertTimer = setTimeout(() => {
            mascot.src = "/static/img/mascot_idle.png";
        }, 2000);
    };

    // Hover behavior
    mascot.addEventListener("mouseenter", setAwake);
    mascot.addEventListener("mouseleave", setIdleDelayed);
}
