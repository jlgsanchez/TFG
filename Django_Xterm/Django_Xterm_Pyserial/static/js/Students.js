//Se pierde Internet
function Lost_internet() {
    $('#modal-alert-lost').modal({ backdrop: 'static', keyboard: false });
    $('#modal-alert-lost').modal('show');
};

//Vuelve
function Internet_back() {
    $('#modal-alert-lost').modal('hide');
};


// Mostrar boton cuando el usuario haga scroll hacia abajo
function Show_totop() {
    let mybutton = document.getElementById("to-top");

    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        mybutton.style.display = "block";
    } else {
        mybutton.style.display = "none";
    }
};

function topFunction() { //Boton hacia arriba
    document.body.scrollTop = 0; // Para Safari
    document.documentElement.scrollTop = 0; // Para Chrome, Firefox, IE y Opera
}


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


// Si se viene desde Groups pinchando en el email del student
function Hover_student(studentName) {
    if (studentName != "None") {
        student = document.getElementById(studentName);
        if (student != null) {
            student.scrollIntoView()

            //Colores para hover el seleccionado
            mode = localStorage.getItem("darkSwitch")
            if (mode == "dark") {
                student.style.backgroundColor = "#545b62"
            } else {
                student.style.backgroundColor = "#ececec"
            }

            student.onmouseover = function() {
                student.style.removeProperty("background-color");
            }
        }
    }
}

// Modal para las alertas y, en el caso que sea necessario, actualizar pagina
function Alert_modal(text, address) {
    let modal_body = document.getElementById('modal-body-alert');
    while (modal_body.firstChild) {
        modal_body.removeChild(modal_body.firstChild);
    }

    let modal_message = document.createElement("p");
    modal_message.setAttribute('id', 'p-modal-alert')
    modal_message.innerHTML = text;
    modal_body.appendChild(modal_message);
    $('#modal-alert').modal('show');

    if (address.length !== 0) {
        $('#modal-alert').on('hidden.bs.modal', function() {
            window.location.href = address;
        })
    }
}


// Abrir modal para poner los inputs crear
function Create() {
    $('#CreateModal').modal('show');
}

// Boton en modal para crear crear
function Create_user(e, token, url_send, url_recieve) {

    e.preventDefault()
    $('#CreateModal').modal('hide');

    $.ajax({
        type: 'POST',
        url: url_send,
        data: {
            "csrfmiddlewaretoken": token,
            'email': $('#email').val(),
            'password': $('#password').val(),
            'first_name': $('#first_name').val(),
            'last_name': $('#last_name').val()
        },

        success: function(data) {
            document.getElementById("CreateStudent").reset();
            if (data.response == "ok") {
                Alert_modal("Student Created.", url_recieve);
            } else if (data.response == "exist") {
                Alert_modal("Student with that e-mail exist already.", "");
            }
        },

        error: function(data) {
            Alert_modal("The student could not be created.", url_recieve);
        }
    });
}


// Para seleccionar y quitar todos
function Checks_all(list) {
    checkboxes = $("input:checkbox[name='row-check']");

    if ($("input:checkbox[name='check_all']").prop("checked")) { //Comprobacion check all 

        for (let i = 0; i < checkboxes.length; i++) { //Para cada check
            let checkbox = checkboxes[i];
            if (!$(checkbox).prop("checked")) {
                let row = checkbox.parentNode.parentNode;
                let column = row.getElementsByTagName("td")[1];
                list.push(column.textContent);

                $(checkbox).prop("checked", true);
            } //Si ya estan seleccionados nada
        }
    } else { //quitar todos
        list.length = 0;
        for (let i = 0; i < checkboxes.length; i++) {
            let checkbox = checkboxes[i];
            if ($(checkbox).prop("checked")) {
                $(checkbox).prop("checked", false);
            } // Si no estan seleccionados nada
        }
    }
}

// Elementos de la tabla
function removeItemList(arr, value) {
    var index = arr.indexOf(value);
    if (index > -1) {
        arr.splice(index, 1);
    }
    return arr;
}

// Para seleccionar y quitar individualmente
function Check_single(row, is_checked, list) {
    let checkboxes = $("input:checkbox[name='row-check']").length;
    let checked_checkboxes = $("input:checkbox[name='row-check']:checked").length;

    let column = row.getElementsByTagName("td")[1];

    // Si el total de checks coincide con el total de checked, checkear check_all
    if (checkboxes === checked_checkboxes) {
        $("input:checkbox[name='check_all']").prop("checked", true);
    } else {
        $("input:checkbox[name='check_all']").prop("checked", false);
    }

    if (is_checked) { //meter en la lista el email
        list.push(column.textContent);
    } else { //sacarlo de la lista
        removeItemList(list, column.textContent);
    }
}

// Borrar elementos seleccionados de la tabla
function Delete_selected(list, token, url_send, url_recieve) {

    if (list.length > 0) { // Si hay studiantes seleccionados
        $.ajax({
            type: "POST",
            url: url_send,
            data: { "csrfmiddlewaretoken": token, 'list': list },

            beforeSend: function() {
                $("#loading-overlay").show();
            },

            success: function(data) {
                $("#loading-overlay").hide();
                Alert_modal("Deleted selected students.", url_recieve);
            },

            error: function(data) {
                $("#loading-overlay").hide();
                Alert_modal("Could not delete the students.", "");
            }
        });
    } else {
        $("#loading-overlay").hide();
        Alert_modal("There are no students selected.", "");
    }
}


// Funciones para subir archivo json (Sin gurdarlo en el server), leerlo y crear los grupos para el super conectado        
function Upload_Students_File(token, url_send, url_recieve) {
    if (document.getElementById('file').value == "") { // Documento no seleccionado
        Alert_modal("No file attach.", "");
        document.getElementById('file').focus();
    } else {
        var data_file = new FormData();
        data_file.append("file", $("input[id^='file']")[0].files[0]);
        data_file.append("csrfmiddlewaretoken", token);
        $.ajax({
            method: "POST",
            url: url_send,
            processData: false,
            contentType: false,
            mimeType: "multipart/form-data",
            data: data_file,
            dataType: "json",

            beforeSend: function() {
                $("#loading-overlay").show();
            },

            success: function(data) {

                if (data.response == "Empty") { // Existen en la DB o no
                    $("#loading-overlay").hide();
                    Alert_modal("Students were added successfully.", url_recieve);
                } else if (data.response == "Not_empty") {
                    let elements = "";
                    for (let i = 0; i < data.noexist.length; i++) {
                        let obj = data.noexist[i];

                        elements = elements + "- " + obj + "<br/>";
                    }
                    $("#loading-overlay").hide();
                    Alert_modal('Students were added successfully but there were some that could not be added as they already exist:<br/>' + elements, url_recieve);
                } else if (data.response == "No_json") {
                    $("#loading-overlay").hide();
                    Alert_modal("The file submitted was not a json file.", "");
                } else if (data.response == "Nousers") {
                    $("#loading-overlay").hide();
                    Alert_modal("The file submitted did not contain users.", "");
                }
            },
            error: function(data) {
                $("#loading-overlay").hide();
                Alert_modal("Internal Error.", "");
            }
        })
    }
}