//Se pierde Internet
function Lost_internet() {
    $('#modal-alert-lost').modal({ backdrop: 'static', keyboard: false });
    $('#modal-alert-lost').modal('show');
};

//Vuelve
function Internet_back() {
    $('#modal-alert-lost').modal('hide');
};


//Cambio de temas cuando se pulsa el boton dentro del nombre del usuario
function initTheme() {
    var darkThemeSelected = localStorage.getItem("darkSwitch") !== null && localStorage.getItem("darkSwitch") === "dark";
    darkSwitch.checked = darkThemeSelected;
    darkThemeSelected ? document.body.setAttribute("data-theme", "dark") : document.body.removeAttribute("data-theme");
}

function resetTheme() {
    if (darkSwitch.checked) {
        document.body.setAttribute("data-theme", "dark");
        localStorage.setItem("darkSwitch", "dark");
    } else {
        document.body.removeAttribute("data-theme");
        localStorage.removeItem("darkSwitch");
    }
}

function Change_theme(darkSwitch) {
    if (darkSwitch) {
        initTheme();
        darkSwitch.addEventListener("change", function() {
            resetTheme();
        });
    }
};