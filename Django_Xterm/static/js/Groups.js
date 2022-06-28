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


//Scroll cuando viene de students
function Hover_group(groupName) {
    if (groupName != "None") {
        hover = document.getElementById(groupName);
        if (hover != null)
            hover.scrollIntoView();
    }
}


//Modales para las alertas
function Alert_modal(text, address, same) {
    let modal_body = document.getElementById('modal-body-alert');
    while (modal_body.firstChild) {
        modal_body.removeChild(modal_body.firstChild);
    }

    let modal_message = document.createElement("p");
    modal_message.setAttribute('id', 'p-modal-alert')
    modal_message.innerHTML = text;
    modal_body.appendChild(modal_message);
    $('#modal-alert').modal('show');

    if (address.length !== 0) { //Cuando es necesario recargar pagina o ir a otra
        $('#modal-alert').on('hidden.bs.modal', function() {
            window.location.href = address;
        })
    }

    if (same === "Addgroup") { //Cuando es necesario mostrar los botones, mismo nombre detectado
        document.getElementById('delete-before').style.display = "block";
        document.getElementById('merge').style.display = "block";
        document.getElementById('cancel').style.display = "block";
    }
    if (same === "AddgroupFile") { //Cuando es necesario mostrar los botones, mismo nombre detectado
        document.getElementById('delete-before-file').style.display = "block";
        document.getElementById('merge-file').style.display = "block";
        document.getElementById('cancel-file').style.display = "block";
    }
}

function Alert_modal_File(text, address) {
    let modal_body = document.getElementById('modal-body-alert-File');
    while (modal_body.firstChild) {
        modal_body.removeChild(modal_body.firstChild);
    }

    let modal_message = document.createElement("p");
    modal_message.setAttribute('id', 'p-modal-alert')
    modal_message.innerHTML = text;
    modal_body.appendChild(modal_message);
    $('#modal-alert-File').modal('show');

    if (address.length !== 0) { //Cuando es necesario recargar pagina o ir a otra
        $('#modal-alert-File').on('hidden.bs.modal', function() {
            window.location.href = address;
        })
    }
}

// Cambiar modal segun sea crear o editar
function OpenModal(text) {
    if (text === "create") {
        $('#groupName').attr("readonly", false);
        $('#modal-do').attr("value", "create");
    } else if (text === "edit") {
        $('#groupName').attr("readonly", true);
        $('#modal-do').attr("value", "edit");
    }
    $('#editModal').modal('show');
}


//Boton borrar todos los grupos (Correspondientes a super conectado)
function Delete_all(token, url_send, url_recieve) {
    $.ajax({
        type: "POST",
        url: url_send,
        data: { "csrfmiddlewaretoken": token },

        beforeSend: function() {
            $("#loading-overlay").show();
        },

        success: function(data) {
            $("#loading-overlay").hide();
            Alert_modal("Deleted all groups.", url_recieve, "");
        },
        error: function(data) {
            $("#loading-overlay").hide();
            Alert_modal("Could not delete all groups.", "", "");
        }
    });
}


//Crear groupos en el modal (faltaria darle al boton de abajo para el submit)
function Create_modal(token, url_send, User_List, Devices_List) {
    $('#groupName').val('');
    $.ajax({
        type: "GET",
        url: url_send,
        data: { "csrfmiddlewaretoken": token },

        success: function(data) {
            let users = data.Users; // user base datos
            let devices = data.Devices; // devices base datos
            $('#users').empty(); // Desplegable
            $('#devices_select').empty(); // Despegabble
            $('#usersList').empty(); // mostrar
            $('#devicesList').empty(); // mostrar
            User_List = [] // Vaciar para quitar lo que haya de una anterior
            Devices_List = [] // Vaciar para quitar lo que haya de una anterior

            $('#users').append($('<option>', { value: "None", text: "Select User" }));
            $('#devices_select').append($('<option>', { value: "None", text: "Select Device" }));

            users.map(user => {
                $('#users').append($('<option>', {
                    value: user,
                    text: user
                }));
            });

            devices.map(device => {
                $('#devices_select').append($('<option>', {
                    value: device,
                    text: device
                }));
            });

            OpenModal("create");
        },

        error: function(data) {
            Alert_modal("An error occurred", "", "");
        }
    });
}

//Funciones botones dentro del modal
function Add_list_user(List) { //Meter en prelista user
    $('#users').val() != 'None' && !List.includes($('#users').val()) ? List.push($('#users').val()) : null;

    $('#usersList').html('');
    List.map((user) => {
        $('#usersList').append('<li class="list-group-item">' + user + '</li>');
    });
}

function Add_list_device(List) { //Meter en prelista device
    $('#devices_select').val() != 'None' && !List.includes($('#devices_select').val()) ? List.push($('#devices_select').val()) : null;

    $('#devicesList').html('');
    List.map((device) => {
        $('#devicesList').append('<li class="list-group-item">' + device + '</li>');
    });
}

function removeItemList(arr, value) {
    var index = arr.indexOf(value);
    if (index > -1) {
        arr.splice(index, 1);
    }
    return arr;
}

function Delete_list_user(List) {
    $('#users').val() != 'None' && List.includes($('#users').val()) ? removeItemList(List, $('#users').val()) : null;

    $('#usersList').html('');
    List.map((user) => { //Sacar en prelista device
        $('#usersList').append('<li class="list-group-item">' + user + '</li>');
    });
}

function Delete_list_device(List) {
    $('#devices_select').val() != 'None' && List.includes($('#devices_select').val()) ? removeItemList(List, $('#devices_select').val()) : null;

    $('#devicesList').html(''); //Vaciar
    List.map((device) => { //Mostar los que hay en la prelista
        $('#devicesList').append('<li class="list-group-item">' + device + '</li>');
    });
}


//Boton editar individual de cada grupo
function Edit_button(id, name, User_List, Devices_List, token, url_send1, url_send2) {
    $('#groupName').val(name);

    // Obtener students y devices
    $.ajax({
        type: "GET",
        url: url_send1,
        data: { "csrfmiddlewaretoken": token },

        success: function(data) {
            let users = data.Users;
            let devices = data.Devices;
            $('#users').empty();
            $('#devices_select').empty();

            $('#users').append($('<option>', { value: "None", text: "Select User" }));
            $('#devices_select').append($('<option>', { value: "None", text: "Select Device" }));

            users.map(user => {
                $('#users').append($('<option>', {
                    value: user,
                    text: user
                }));
            });

            devices.map(device => {
                $('#devices_select').append($('<option>', {
                    value: device,
                    text: device
                }));
            });
        },

        error: function(data) {
            Alert_modal("An error ocurred.", "", "");
        }
    });

    // Obtener students y devices de ese grupo
    $.ajax({
        type: "GET",
        url: url_send2,
        data: { "csrfmiddlewaretoken": token, groupId: id },

        success: function(data) {
            listu = Object.values(data.normalUsers);
            listd = Object.values(data.devices);

            for (i = 0; i < listu.length; i++) {
                User_List.push(listu[i])
            }

            for (i = 0; i < listd.length; i++) {
                Devices_List.push(listd[i])
            }

            $('#usersList').empty();
            $('#devicesList').empty();

            User_List.map((user) => {
                $('#usersList').append('<li class="list-group-item">' + user + '</li>');
            });

            Devices_List.map((device) => {
                $('#devicesList').append('<li class="list-group-item">' + device + '</li>');
            });

        },

        error: function(data) {
            Alert_modal("An error occurred.", "", "");
        }
    });

    OpenModal("edit");

};

//Boton dentro de modal, aceptar para crear el grupo para el profesor conectado
function Add_group(e, token, url_send, url_recieve, User_List, Devices_List) {
    e.preventDefault();
    let to_do = document.getElementById('modal-do').value;

    $.ajax({
        type: "POST",
        url: url_send,
        data: {
            "csrfmiddlewaretoken": token,
            'groupName': $('#groupName').val(),
            'userList': User_List,
            'devicesList': Devices_List,
            'to_do': to_do
        },

        beforeSend: function() {
            $("#loading-overlay").show();
        },

        success: function(data) {
            if (data.response == 'group') {
                $('#editModal').modal('hide');
                $("#loading-overlay").hide();
                Alert_modal("Detected a group with the same name. What do you want to do?<br/>&nbsp;&nbsp;&nbsp;- Delete the existing one.<br/>&nbsp;&nbsp;&nbsp;- Merge with the existing one.<br/>&nbsp;&nbsp;&nbsp;- Cancel the operation.<br/>", "", "Addgroup");
            } else if (data.response == "created") {
                $('#editModal').modal('hide');
                $("#loading-overlay").hide();
                Alert_modal("Group added successfully.", url_recieve, "");
            } else if (data.response == "edited") {
                $('#editModal').modal('hide');
                $("#loading-overlay").hide();
                Alert_modal("Group edited successfully.", url_recieve, "");
            }
        },

        error: function(data) {
            $("#loading-overlay").hide();
            Alert_modal("An error occurred.", "", "");
        }
    });
}

// Funciones botones modal cuando ya hay un grupo con ese nombre
function Merge(User_List, Devices_List, token, url_send, url_recieve) {
    $.ajax({
        type: "POST",
        url: url_send,
        data: {
            "csrfmiddlewaretoken": token,
            'groupName': $('#groupName').val(),
            'userList': User_List,
            'devicesList': Devices_List
        },

        beforeSend: function() {
            $("#loading-overlay").show();
        },

        success: function(data) {
            $('#modal-alert').modal('hide');
            $("#loading-overlay").hide();
            Alert_modal("Merged the groups with the same name.", url_recieve, "");
        },

        error: function(data) {
            $("#loading-overlay").hide();
            Alert_modal("An error occurred.", "", "");
        }
    });
}

function Delete_Before(User_List, Devices_List, token, url_send, url_recieve) {
    $.ajax({
        type: "POST",
        url: url_send,
        data: {
            "csrfmiddlewaretoken": token,
            'groupName': $('#groupName').val(),
            'userList': User_List,
            'devicesList': Devices_List
        },

        beforeSend: function() {
            $("#loading-overlay").show();
        },

        success: function(data) {
            $('#modal-alert').modal('hide');
            $("#loading-overlay").hide();
            Alert_modal("Deleted group with the same name and added the new one.", url_recieve, "");
        },

        error: function(data) {
            $("#loading-overlay").hide();
            Alert_modal("An error occurred.", "", "");
        }
    });
}


//Boton borrrar grupo individual
function Delete_button(id, token, url_send, url_recieve) {
    $.ajax({
        type: "POST",
        url: url_send,
        data: { "csrfmiddlewaretoken": token, groupId: id },

        success: function(data) {
            Alert_modal("Group Deleted Successfully.", url_recieve, "");
        },

        error: function(data) {
            Alert_modal("An error occurred.", "", "");
        }
    });
}


// Funciones para subir archivo json (Sin gurdarlo en el server), leerlo y crear los grupos para el super conectado        
function Upload_Groups_File(token, url_send, url_recieve) {
    if (document.getElementById('file').value == "") { //Documento no seleccionado
        Alert_modal("No file attach.", "", "");
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

            success: function(data) {
                if (data.response == "Empty") { // Comprobar si hay students o devices en el json que no exsiten en la BD 
                    Alert_modal("Groups were added successfully.", url_recieve, "");

                } else if (data.response == "Not_empty") {
                    let elements = "";

                    for (let i = 0; i < data.noexist["groups"].length; i++) {
                        let obj = data.noexist["groups"][i];

                        elements = elements + "- " + obj.name + ": ";

                        if (obj.users.length > 0 && obj.devices.length > 0) {
                            elements = elements + "<br/>&nbsp;&nbsp;&nbsp;Users -> " + obj.users + ".<br/>&nbsp;&nbsp;&nbsp;" + "Devices -> " + obj.devices;
                        } else if (obj.users.length > 0) {
                            elements = elements + "<br/>&nbsp;&nbsp;&nbsp;Users -> " + obj.users;
                        } else if (obj.devices.length > 0) {
                            elements = elements + "<br/>&nbsp;&nbsp;&nbsp;Devices -> " + obj.devices;
                        }

                        elements = elements + ".<br/>";
                    }
                    Alert_modal('Groups were created successfully but there were elements that could not be added as they did not exist in the DB:<br/>' + elements, url_recieve, "");

                } else if (data.response == "group") {
                    Alert_modal("Detected a group with the same name. What do you want to do?<br/>&nbsp;&nbsp;&nbsp;- Delete the existing one.<br/>&nbsp;&nbsp;&nbsp;- Merge with the existing one.<br/>&nbsp;&nbsp;&nbsp;- Cancel the operation.<br/>", "", "AddgroupFile");

                } else if (data.response == "No_json") {
                    Alert_modal("The file submitted was not a json file.", "", "");

                } else if (data.response == "Nogroups") {
                    Alert_modal("The file submitted did not contain groups.", "", "");
                }
            },
            error: function(data) {
                Alert_modal("Internal Error.", "", "");
            }
        })
    }
}

// Funciones botones modal-File cuando ya hay un grupo con ese nombre
function Merge_File(token, url_send, url_recieve) {
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

        success: function(data) {
            if (data.response == "Empty") { // Comprobar si hay students o devices en el json que no exsiten en la BD 
                $('#modal-alert').modal('hide');
                Alert_modal_File("Groups were created and merged successfully.", url_recieve);

            } else if (data.response == "Not_empty") {
                $('#modal-alert').modal('hide');
                let elements = "";

                for (let i = 0; i < data.noexist["groups"].length; i++) {
                    let obj = data.noexist["groups"][i];

                    elements = elements + "- " + obj.name + ": ";

                    if (obj.users.length > 0 && obj.devices.length > 0) {
                        elements = elements + "<br/>&nbsp;&nbsp;&nbsp;Users -> " + obj.users + ".<br/>&nbsp;&nbsp;&nbsp;" + "Devices -> " + obj.devices;
                    } else if (obj.users.length > 0) {
                        elements = elements + "<br/>&nbsp;&nbsp;&nbsp;Users -> " + obj.users;
                    } else if (obj.devices.length > 0) {
                        elements = elements + "<br/>&nbsp;&nbsp;&nbsp;Devices -> " + obj.devices;
                    }

                    elements = elements + ".<br/>";
                }
                Alert_modal_File('Groups were created and merged successfully but there were elements that could not be added as they did not exist in the DB:<br/>' + elements, url_recieve);

            } else if (data.response == "No_json") {
                $('#modal-alert').modal('hide');
                Alert_modal_File("The file submitted was not a json file.", "");
            }
        },
        error: function(data) {
            $('#modal-alert').modal('hide');
            Alert_modal_File("Internal Error.", "");
        }
    })
}

function Delete_Before_File(token, url_send, url_recieve) {
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

        success: function(data) {
            if (data.response == "Empty") { // Comprobar si hay students o devices en el json que no exsiten en la BD 
                $('#modal-alert').modal('hide');
                Alert_modal_File("Existing groups were deleted and new ones were added successfully.", url_recieve);

            } else if (data.response == "Not_empty") {
                $('#modal-alert').modal('hide');
                let elements = "";
                for (let i = 0; i < data.noexist["groups"].length; i++) {
                    let obj = data.noexist["groups"][i];

                    elements = elements + "- " + obj.name + ": ";

                    if (obj.users.length > 0 && obj.devices.length > 0) {
                        elements = elements + "<br/>&nbsp;&nbsp;&nbsp;Users -> " + obj.users + ".<br/>&nbsp;&nbsp;&nbsp;" + "Devices -> " + obj.devices;
                    } else if (obj.users.length > 0) {
                        elements = elements + "<br/>&nbsp;&nbsp;&nbsp;Users -> " + obj.users;
                    } else if (obj.devices.length > 0) {
                        elements = elements + "<br/>&nbsp;&nbsp;&nbsp;Devices -> " + obj.devices;
                    }

                    elements = elements + ".<br/>";
                }

                Alert_modal_File('Existin groups were deleted and new ones were created successfully but there were elements that could not be added as they did not exist in the DB:<br/>' + elements, url_recieve);
            } else if (data.response == "No_json") {
                $('#modal-alert').modal('hide');
                Alert_modal_File("The file submitted was not a json file.", "");
            }
        },
        error: function(data) {
            $('#modal-alert').modal('hide');
            Alert_modal_File("Internal Error.", "");
        }
    })
}