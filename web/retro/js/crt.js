/* USER CUSTOMIZATIONS */

const CRT_SCREEN_FLICKER = false;

/* DO NOT EDIT BELOW THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING!!!! */

const elem = document.body;

function toggleFlicker() {
    const shouldFlicker = Math.random() > 0.7; // 30% chance to flicker
    if (shouldFlicker) {
        elem.classList.add("flicker");
        setTimeout(() => {
            elem.classList.remove("flicker");
            toggleFlicker();
        }, 1000); // flicker for 200ms
    } else {
        setTimeout(toggleFlicker, 300); // check every 300ms
    }
}

// Run it every random interval
if(CRT_SCREEN_FLICKER) {
    setTimeout(toggleFlicker, 300);
}

const distortion = document.querySelector('.crt-distortion');
let $rand = 0;
distortion.addEventListener('animationend', function(){
    this.classList.remove("scanline-animation");
    $rand = (Math.floor(Math.random() * 6) + 4);
    this.style.animationDuration =  $rand + 's';
    void this.offsetWidth; // hack to reflow css animation
    this.classList.add("scanline-animation");
});
