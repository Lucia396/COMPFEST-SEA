// highlight current link in navbar
const cur = window.location.pathname;
const page = cur.split("/").pop();

if (page === "home.html") {
    document.getElementById("home").classList.add("active");
}
if (page === "meal.html") {
    document.getElementById("meal").classList.add("active");
}
if (page === "subscription.html") {
    document.getElementById("subscription").classList.add("active");
}
if (page === "contact.html") {
    document.getElementById("contact").classList.add("active");
}

// modal popup meal
if (page === "meal.html") {
    const meal1 = document.getElementById("card1");
    const meal2 = document.getElementById("card2");
    const meal3 = document.getElementById("card3");
    const meal4 = document.getElementById("card4");
    const meal5 = document.getElementById("card5");
    const meal6 = document.getElementById("card6");
    const meal7 = document.getElementById("card7");
    const meal8 = document.getElementById("card8");
    const meal9 = document.getElementById("card9");
    const popup1 = document.getElementById("popup1");
    const popup2 = document.getElementById("popup2");
    const popup3 = document.getElementById("popup3");
    const popup4 = document.getElementById("popup4");
    const popup5 = document.getElementById("popup5");
    const popup6 = document.getElementById("popup6");
    const popup7 = document.getElementById("popup7");
    const popup8 = document.getElementById("popup8");
    const popup9 = document.getElementById("popup9");
    const closebtn1 = document.getElementById("closebtn1");
    const closebtn2 = document.getElementById("closebtn2");
    const closebtn3 = document.getElementById("closebtn3");
    const closebtn4 = document.getElementById("closebtn4");
    const closebtn5 = document.getElementById("closebtn5");
    const closebtn6 = document.getElementById("closebtn6");
    const closebtn7 = document.getElementById("closebtn7");
    const closebtn8 = document.getElementById("closebtn8");
    const closebtn9 = document.getElementById("closebtn9");

    meal1.addEventListener("click", () => {
        popup1.classList.add("active");
        popup1.classList.add("open");
        popup1.style.display = "block";
    });
    meal2.addEventListener("click", () => {
        popup2.classList.add("active");
        popup2.classList.add("open");
        popup2.style.display = "block";
    });
    meal3.addEventListener("click", () => {
        popup3.classList.add("active");
        popup3.classList.add("open");
        popup3.style.display = "block";
    });
    meal4.addEventListener("click", () => {
        popup4.classList.add("active");
        popup4.classList.add("open");
        popup4.style.display = "block";
    });
    meal5.addEventListener("click", () => {
        popup5.classList.add("active");
        popup5.classList.add("open");
        popup5.style.display = "block";
    });
    meal6.addEventListener("click", () => {
        popup6.classList.add("active");
        popup6.classList.add("open");
        popup6.style.display = "block";
    });
    meal7.addEventListener("click", () => {
        popup7.classList.add("active");
        popup7.classList.add("open");
        popup7.style.display = "block";
    });
    meal8.addEventListener("click", () => {
        popup8.classList.add("active");
        popup8.classList.add("open");
        popup8.style.display = "block";
    });
    meal9.addEventListener("click", () => {
        popup9.classList.add("active");
        popup9.classList.add("open");
        popup9.style.display = "block";
    });

    closebtn1.addEventListener("click", () => {
        popup1.classList.add("slideOut");
        setTimeout(() => {
            popup1.classList.remove("active", "slideOut");
            popup1.style.display = "none";
        }, 200);
    });
    closebtn2.addEventListener("click", () => {
        popup2.classList.add("slideOut");
        setTimeout(() => {
            popup2.classList.remove("active", "slideOut");
            popup2.style.display = "none";
        }, 200);
    });
    closebtn3.addEventListener("click", () => {
        popup3.classList.add("slideOut");
        setTimeout(() => {
            popup3.classList.remove("active", "slideOut");
            popup3.style.display = "none";
        }, 200);
    });
    closebtn4.addEventListener("click", () => {
        popup4.classList.add("slideOut");
        setTimeout(() => {
            popup4.classList.remove("active", "slideOut");
            popup4.style.display = "none";
        }, 200);
    });
    closebtn5.addEventListener("click", () => {
        popup5.classList.add("slideOut");
        setTimeout(() => {
            popup5.classList.remove("active", "slideOut");
            popup5.style.display = "none";
        }, 200);
    });
    closebtn6.addEventListener("click", () => {
        popup6.classList.add("slideOut");
        setTimeout(() => {
            popup6.classList.remove("active", "slideOut");
            popup6.style.display = "none";
        }, 200);
    });
    closebtn7.addEventListener("click", () => {
        popup7.classList.add("slideOut");
        setTimeout(() => {
            popup7.classList.remove("active", "slideOut");
            popup7.style.display = "none";
        }, 200);
    });
    closebtn8.addEventListener("click", () => {
        popup8.classList.add("slideOut");
        setTimeout(() => {
            popup8.classList.remove("active", "slideOut");
            popup8.style.display = "none";
        }, 200);
    });
    closebtn9.addEventListener("click", () => {
        popup9.classList.add("slideOut");
        setTimeout(() => {
            popup9.classList.remove("active", "slideOut");
            popup9.style.display = "none";
        }, 200);
    });
}

// carousel testimonial
if (page === "home.html") {
    let idx = 1;
    show(idx);
    function next(n) {
        show(idx += n);
    }
    function current(n) {
        show(idx = n);
    }
    function show(n) {
        let slides = document.getElementsByClassName("slide");
        let dots = document.getElementsByClassName("dot");
        if (n > slides.length) {
            idx = 1
        }
        if (n < 1) {
            idx = slides.length
        }
        for (let slide of slides) {
            slide.style.display = "none";
        }
        for (let dot of dots) {
            dot.classList.remove("active");
        }
        slides[idx-1].style.display = "block";
        dots[idx-1].classList.add("active");
    }
}

// counting price
if (page == "subscription.html") {
    let price = 0, time = 0, day = 0;
    function countplan() {
        let plans = document.getElementById("plan");
        let idx = plans.selectedIndex;
        price = 0;
        if (idx == 1) price = 30000;
        if (idx == 2) price = 40000;
        if (idx == 3) price = 60000;
        let total = price * time * day * 4.3;
        document.getElementById("prices").innerHTML = "Rp "+total+",00";
    }
    function counttime() {
        let times = document.getElementById("time").selectedOptions;
        time = 0;
        for (let i = 0; i < times.length; i++) {
            if (times[i].label === "Breakfast") time++;
            if (times[i].label === "Lunch") time++;
            if (times[i].label === "Dinner") time++;
        }
        let total = price * time * day * 4.3;
        document.getElementById("prices").innerHTML = "Rp "+total+",00";
    }
    function countday() {
        let days = document.getElementById("day").selectedOptions;
        day = 0;
        for (let i = 0; i < days.length; i++) {
            if (days[i].label === "Monday") day++;
            if (days[i].label === "Tuesday") day++;
            if (days[i].label === "Wednesday") day++;
            if (days[i].label === "Thursday") day++;
            if (days[i].label === "Friday") day++;
            if (days[i].label === "Saturday") day++;
            if (days[i].label === "Sunday") day++;
        }
        let total = price * time * day * 4.3;
        document.getElementById("prices").innerHTML = "Rp "+total+",00";
    }
}